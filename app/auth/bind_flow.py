"""Canvas OAuth2 binding flow — webhook callback handler.

The /auth/canvas/callback endpoint receives the OAuth2 redirect after
the user authorizes the app in Canvas.
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.canvas_oauth import encrypt_token, exchange_code_for_token
from app.models.user_mapping import UserMapping

logger = logging.getLogger(__name__)


async def handle_canvas_callback(
    db: AsyncSession,
    code: str,
    state: str,
) -> str:
    """Handle the Canvas OAuth2 callback.

    Decodes state to find wechat_user_id, exchanges code for tokens,
    creates or updates the UserMapping, and returns a success message.

    Returns a user-facing message string.
    """
    # Decode state to get wechat_user_id
    wechat_user_id = _decode_state(state)
    if not wechat_user_id:
        return "❌ 绑定失败：无法解析请求参数。请重新发送 /bind。"

    try:
        token_data = await exchange_code_for_token(code)
    except Exception as exc:
        logger.error("Token exchange failed: %s", exc)
        return "❌ 绑定失败：无法获取 Canvas 授权。请检查链接是否过期后重新发送 /bind。"

    # Upsert user mapping
    stmt = select(UserMapping).where(UserMapping.wechat_user_id == wechat_user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        user = UserMapping(
            wechat_user_id=wechat_user_id,
            canvas_user_id=token_data["canvas_user_id"],
            canvas_domain=_extract_domain(),
            canvas_name=token_data["canvas_name"],
            canvas_email=token_data["canvas_email"],
            encrypted_access_token=encrypt_token(token_data["access_token"]),
            encrypted_refresh_token=encrypt_token(token_data["refresh_token"]),
            token_expires_at=token_data["expires_at"],
            is_active=True,
        )
        db.add(user)
    else:
        user.canvas_user_id = token_data["canvas_user_id"]
        user.canvas_domain = _extract_domain()
        user.canvas_name = token_data["canvas_name"]
        user.canvas_email = token_data["canvas_email"]
        user.encrypted_access_token = encrypt_token(token_data["access_token"])
        user.encrypted_refresh_token = encrypt_token(token_data["refresh_token"])
        user.token_expires_at = token_data["expires_at"]
        user.is_active = True

    await db.flush()

    # Trigger initial sync (via Celery)
    _trigger_initial_sync(user.id)

    return (
        f"✅ 绑定成功！欢迎你，{token_data['canvas_name'] or '同学'}！\n"
        f"\n"
        f"📧 {token_data['canvas_email'] or '未知邮箱'}\n"
        f"🏫 {_extract_domain()}\n"
        f"\n"
        f"系统正在同步你的课程数据，请稍候。\n"
        f"同步完成后我会通知你。"
    )


def _decode_state(state: str) -> str | None:
    """Decode the state parameter to recover the wechat_user_id."""
    import base64

    try:
        # Add padding back
        padding = 4 - len(state) % 4
        if padding != 4:
            state += "=" * padding
        raw = base64.urlsafe_b64decode(state.encode()).decode()
        wechat_user_id, _sep, _key = raw.partition(":")
        return wechat_user_id
    except Exception:
        return None


def _extract_domain() -> str:
    """Extract hostname from Canvas base URL."""
    from urllib.parse import urlparse

    return urlparse(settings.canvas_base_url).hostname or settings.canvas_base_url


def _trigger_initial_sync(user_mapping_id: int) -> None:
    """Trigger an initial data sync for a newly bound user."""
    try:
        from app.sync.tasks import sync_assignments, sync_announcements, sync_enrollments

        sync_enrollments.delay()
    except Exception as exc:
        logger.warning("Failed to trigger initial sync: %s", exc)


from app.config import settings  # noqa: E402
