"""Long-polling main loop for iLink Bot API.

Runs as a background asyncio task alongside FastAPI.
Continuously polls /ilink/bot/getupdates, dispatches messages, and handles reconnection.
"""

import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.ilink.client import ilink_client
from app.ilink.context_token import (
    clear_pending_notifications,
    get_pending_notifications,
    save_context_token,
)
from app.ilink.message_handler import handle_message

logger = logging.getLogger(__name__)

# Reconnection parameters
RECONNECT_DELAY_SECONDS = 5
MAX_CONSECUTIVE_ERRORS = 10


async def flush_and_send_pending(
    db: AsyncSession,
    user_id: int,
    wechat_user_id: str,
    current_context_token: str,
) -> int:
    """Send all pending notifications for a user. Returns count sent."""
    pending = await get_pending_notifications(db, user_id)
    if not pending:
        return 0

    sent_ids: list[int] = []
    for pn in pending:
        text = pn.payload.get("text", "")
        if not text:
            sent_ids.append(pn.id)
            continue

        try:
            await ilink_client.send_message(
                to_user_id=wechat_user_id,
                text=text,
                context_token=current_context_token,
            )
            sent_ids.append(pn.id)
            pn.retry_count += 1
        except Exception as exc:
            logger.error("Failed to flush pending notification %d: %s", pn.id, exc)
            pn.retry_count += 1
            # Keep it in the queue if under max_retries
            if pn.retry_count >= pn.max_retries:
                sent_ids.append(pn.id)

        # Rate-limit: 1s between messages
        await asyncio.sleep(1.0)

    await clear_pending_notifications(db, sent_ids)
    return len(sent_ids)


async def poll_loop() -> None:
    """Main long-polling loop. Runs until cancelled."""
    buf = ""
    consecutive_errors = 0

    logger.info("iLink poller started (channel_version=%s)", ilink_client.base_url)

    while True:
        try:
            resp = await ilink_client.get_updates(buf)
            buf = resp.get("get_updates_buf", buf)
            consecutive_errors = 0

            msgs = resp.get("msgs") or []
            for raw_msg in msgs:
                await _handle_one_message(raw_msg)

        except asyncio.CancelledError:
            logger.info("iLink poller cancelled")
            break
        except Exception as exc:
            consecutive_errors += 1
            logger.error(
                "iLink poller error (consecutive=%d/%d): %s",
                consecutive_errors,
                MAX_CONSECUTIVE_ERRORS,
                exc,
            )
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                logger.critical("Too many consecutive poll errors — sleeping 60s")
                await asyncio.sleep(60)
                consecutive_errors = 0
            else:
                await asyncio.sleep(RECONNECT_DELAY_SECONDS)


async def _handle_one_message(raw_msg: dict) -> None:
    """Process a single incoming message within its own DB session."""
    from_user_id = raw_msg.get("from_user_id", "")
    context_token = raw_msg.get("context_token", "")
    text = ""
    for item in raw_msg.get("item_list", []):
        if item.get("type") == 1:
            text = item.get("text_item", {}).get("text", "")
            break

    if not text:
        return  # skip non-text or empty messages

    async with async_session_factory() as db:
        try:
            # 1. Persist the latest context_token
            user = await save_context_token(db, from_user_id, context_token)

            if user is not None:
                # 2. Flush pending notifications first
                count = await flush_and_send_pending(
                    db, user.id, from_user_id, context_token or ""
                )
                if count:
                    logger.info("Flushed %d pending notifications for %s", count, from_user_id)

            # 3. Handle the message
            reply = await handle_message(db, from_user_id, text, user)

            # 4. Send reply if one was produced
            if reply and context_token:
                await ilink_client.send_message(
                    to_user_id=from_user_id,
                    text=reply,
                    context_token=context_token,
                )

            await db.commit()

        except Exception as exc:
            await db.rollback()
            logger.error("Error handling message from %s: %s", from_user_id, exc)
