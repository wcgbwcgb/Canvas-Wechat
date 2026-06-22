"""Notification dispatcher — sends notifications via iLink, with context_token pre-check and pending queue fallback."""

import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.ilink.client import ilink_client
from app.ilink.context_token import is_context_token_stale
from app.models.notification_log import NotificationLog
from app.models.pending_notification import PendingNotification
from app.models.user_mapping import UserMapping

logger = logging.getLogger(__name__)


async def dispatch_notification(
    db: AsyncSession,
    user: UserMapping,
    notification_type: str,
    text: str,
    assignment_id: int | None = None,
    announcement_id: int | None = None,
    submission_id: int | None = None,
    course_id: int | None = None,
) -> str:
    """Send a notification to a user via iLink.

    Returns status: 'sent', 'pending', 'failed', or 'suppressed'.
    """
    # Check if already sent (idempotency)
    if await _already_sent(db, user.id, notification_type, assignment_id, announcement_id):
        return "suppressed"

    # Check context_token staleness
    if is_context_token_stale(user) or not user.context_token:
        # Queue as pending
        pn = PendingNotification(
            user_mapping_id=user.id,
            notification_type=notification_type,
            payload={"text": text},
        )
        db.add(pn)

        # Also log
        log = NotificationLog(
            user_mapping_id=user.id,
            notification_type=notification_type,
            course_id=course_id,
            assignment_id=assignment_id,
            announcement_id=announcement_id,
            submission_id=submission_id,
            status="pending",
        )
        db.add(log)
        return "pending"

    # Attempt to send
    try:
        await ilink_client.send_message(
            to_user_id=user.wechat_user_id,
            text=text,
            context_token=user.context_token,
        )

        log = NotificationLog(
            user_mapping_id=user.id,
            notification_type=notification_type,
            course_id=course_id,
            assignment_id=assignment_id,
            announcement_id=announcement_id,
            submission_id=submission_id,
            status="sent",
            sent_at=datetime.datetime.now(datetime.timezone.utc),
        )
        db.add(log)
        return "sent"

    except Exception as exc:
        logger.error("Failed to send notification to %s: %s", user.wechat_user_id, exc)

        # Queue as pending
        pn = PendingNotification(
            user_mapping_id=user.id,
            notification_type=notification_type,
            payload={"text": text},
        )
        db.add(pn)

        log = NotificationLog(
            user_mapping_id=user.id,
            notification_type=notification_type,
            course_id=course_id,
            assignment_id=assignment_id,
            announcement_id=announcement_id,
            submission_id=submission_id,
            status="failed",
            error_message=str(exc)[:500],
        )
        db.add(log)
        return "failed"


async def _already_sent(
    db: AsyncSession,
    user_mapping_id: int,
    notification_type: str,
    assignment_id: int | None,
    announcement_id: int | None,
) -> bool:
    """Check if a notification was already sent for this event."""
    from sqlalchemy import select

    stmt = select(NotificationLog).where(
        NotificationLog.user_mapping_id == user_mapping_id,
        NotificationLog.notification_type == notification_type,
        NotificationLog.status == "sent",
    )

    if assignment_id is not None:
        stmt = stmt.where(NotificationLog.assignment_id == assignment_id)
    if announcement_id is not None:
        stmt = stmt.where(NotificationLog.announcement_id == announcement_id)

    result = await db.execute(stmt.limit(1))
    return result.scalar_one_or_none() is not None
