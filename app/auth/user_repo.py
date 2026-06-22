"""Data access helpers for UserMapping."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_mapping import UserMapping


async def get_user_by_wechat_id(
    db: AsyncSession,
    wechat_user_id: str,
) -> UserMapping | None:
    """Look up an active user by WeChat user ID."""
    stmt = (
        select(UserMapping)
        .where(UserMapping.wechat_user_id == wechat_user_id)
        .where(UserMapping.is_active == True)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> UserMapping | None:
    """Look up a user by internal ID."""
    stmt = select(UserMapping).where(UserMapping.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
