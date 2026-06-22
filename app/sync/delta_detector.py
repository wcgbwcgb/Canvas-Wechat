"""Delta detection — publishes data-change events to Redis pub/sub.

Notification engine subscribes to these channels for real-time relay.
"""

import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def publish_delta(
    db: AsyncSession,
    event_type: str,
    payload: dict,
) -> None:
    """Publish a delta event to Redis pub/sub.

    Channels match the event type: 'assignment_created', 'announcement_created', etc.
    Payload is JSON-serialized and published so notification engine can react.
    """
    try:
        from app.db.redis import get_redis

        redis = await get_redis()
        channel = f"canvas:{event_type}"
        await redis.publish(channel, json.dumps(payload, default=str))
        logger.debug("Published delta: %s → %s", channel, payload)
    except Exception as exc:
        # Delta publishing is best-effort — don't fail the sync
        logger.warning("Failed to publish delta %s: %s", event_type, exc)
