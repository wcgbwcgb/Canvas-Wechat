"""Routes incoming iLink messages to the appropriate handler.

Supported commands:
  /bind    — start Canvas OAuth2 binding flow
  /help    — show available commands
  anything else — (Phase 4) forward to AI Chat Service; for now, echo + hint
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_mapping import UserMapping

logger = logging.getLogger(__name__)

HELP_TEXT = (
    "📚 Canvas 微信助教\n"
    "\n"
    "可用命令：\n"
    "  /bind  — 绑定你的 Canvas 账号\n"
    "  /help  — 显示此帮助\n"
    "\n"
    "绑定后即可查询作业、公告和成绩。"
)


async def handle_message(
    db: AsyncSession,
    wechat_user_id: str,
    text: str,
    user: UserMapping | None,
) -> str | None:
    """Route an incoming text message. Returns the reply text or None."""

    text = text.strip()

    # Commands
    if text.startswith("/help") or text in ("帮助", "help"):
        return HELP_TEXT

    if text.startswith("/bind") or text == "绑定":
        return await _handle_bind(db, wechat_user_id, user)

    # If user is not yet bound, guide them
    if user is None:
        return (
            "👋 欢迎！请先绑定你的 Canvas 账号。\n"
            "\n"
            "发送 /bind 开始绑定流程。"
        )

    # TODO Phase 4: forward to AI Chat Service
    # For now: simple echo with status
    course_count = await _get_course_count(db, user.id)
    return (
        f"👋 你好 {user.canvas_name or '同学'}！\n"
        f"\n"
        f"📚 已绑定课程：{course_count} 门\n"
        f"\n"
        f"（AI 对话功能即将上线，敬请期待）\n"
        f"\n"
        f"你可以问我：\n"
        f"  • 这周有什么作业？\n"
        f"  • 我的成绩怎么样？\n"
        f"  • 最近有什么新公告？"
    )


async def _handle_bind(
    db: AsyncSession,
    wechat_user_id: str,
    user: UserMapping | None,
) -> str:
    """Start or report the Canvas OAuth2 binding flow."""
    if user is not None:
        return (
            f"✅ 你已经绑定过 Canvas 账号了！\n"
            f"\n"
            f"👤 {user.canvas_name or '未知用户'}\n"
            f"📧 {user.canvas_email or '未知邮箱'}\n"
            f"🏫 {user.canvas_domain}\n"
            f"\n"
            f"如需重新绑定，请先在 Canvas 中撤销授权后再发送 /bind。"
        )

    from app.config import settings

    if not settings.canvas_client_id:
        return "⚠️ Canvas 尚未配置（缺少 CLIENT_ID）。请联系管理员。"

    # Generate a state parameter encoding the wechat_user_id
    import base64
    import hashlib
    import hmac

    raw = f"{wechat_user_id}:{settings.canvas_token_encryption_key}"
    state = base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")

    auth_url = (
        f"{settings.canvas_oauth2_auth_url}"
        f"?client_id={settings.canvas_client_id}"
        f"&response_type=code"
        f"&redirect_uri={settings.canvas_redirect_uri}"
        f"&state={state}"
    )

    return (
        "🔐 请点击以下链接绑定你的 Canvas 账号：\n"
        "\n"
        f"{auth_url}\n"
        "\n"
        "1. 在浏览器中打开链接\n"
        "2. 登录你的 Canvas 账号\n"
        "3. 授权后自动完成绑定"
    )


async def _get_course_count(db: AsyncSession, user_mapping_id: int) -> int:
    """Count active enrollments for a user."""
    from sqlalchemy import func, select

    from app.models.enrollment import Enrollment

    stmt = (
        select(func.count())
        .select_from(Enrollment)
        .where(Enrollment.user_mapping_id == user_mapping_id)
        .where(Enrollment.enrollment_state == "active")
    )
    result = await db.execute(stmt)
    return result.scalar_one() or 0
