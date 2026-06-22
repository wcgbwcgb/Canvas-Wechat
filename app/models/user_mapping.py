"""Maps WeChat user identities to Canvas user accounts."""

import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class UserMapping(Base, TimestampMixin):
    __tablename__ = "user_mappings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    wechat_user_id: Mapped[str] = mapped_column(
        String(256), unique=True, nullable=False, index=True
    )
    canvas_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    canvas_domain: Mapped[str] = mapped_column(String(255), nullable=False)
    canvas_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    canvas_email: Mapped[str | None] = mapped_column(String(500), nullable=True)
    encrypted_access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    encrypted_refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    context_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    context_token_updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
