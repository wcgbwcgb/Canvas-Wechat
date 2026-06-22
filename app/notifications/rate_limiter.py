"""Redis-based rate limiter for notifications."""

import logging

from app.config import settings

logger = logging.getLogger(__name__)


async def check_and_increment(user_id: int) -> bool:
    """Check if user is under daily notification limit. Increments counter.

    Returns True if under limit (send allowed), False if limit exceeded.
    """
    try:
        from app.db.redis import get_redis

        redis = await get_redis()
        import datetime

        today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        key = f"notif_rate:{user_id}:{today}"

        count = await redis.incr(key)
        if count == 1:
            # Set expiry to end of day (Beijing time)
            await redis.expire(key, 86400)

        return count <= settings.max_daily_notifications
    except Exception as exc:
        logger.warning("Rate limiter check failed: %s", exc)
        return True  # Fail open
