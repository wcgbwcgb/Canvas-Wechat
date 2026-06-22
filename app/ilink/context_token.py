"""context_token persistence, staleness checks, and pending-notification flush."""

import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.pending_notification import PendingNotification
from app.models.user_mapping import UserMapping


async def save_context_token(
    db: AsyncSession,
    wechat_user_id: str,
    token: str,
) -> UserMapping | None:
    """Persist the latest context_token for a WeChat user."""
    if not token:
        return None

    stmt = (
        select(UserMapping)
        .where(UserMapping.wechat_user_id == wechat_user_id)
        .where(UserMapping.is_active == True)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is not None:
        user.context_token = token
        user.context_token_updated_at = datetime.datetime.now(datetime.timezone.utc)
        await db.flush()

    return user


def is_context_token_stale(user: UserMapping) -> bool:
    """Return True if the context_token hasn't been updated for > STALE_HOURS."""
    if user.context_token_updated_at is None:
        return True
    age = datetime.datetime.now(datetime.timezone.utc) - user.context_token_updated_at
    return age > datetime.timedelta(hours=settings.context_token_stale_hours)


async def get_pending_notifications(db: AsyncSession, user_id: int) -> list[PendingNotification]:
    """Retrieve pending notifications for a user, ordered oldest first."""
    stmt = (
        select(PendingNotification)
        .where(PendingNotification.user_mapping_id == user_id)
        .order_by(PendingNotification.created_at.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def clear_pending_notifications(db: AsyncSession, ids: list[int]) -> None:
    """Delete flushed pending notifications by ID."""
    if not ids:
        return
    from sqlalchemy import delete

    await db.execute(delete(PendingNotification).where(PendingNotification.id.in_(ids)))
    await db.flush()
