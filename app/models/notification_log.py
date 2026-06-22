"""Sent notification log — idempotency + analytics."""

import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class NotificationLog(Base, TimestampMixin):
    __tablename__ = "notification_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_mapping_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user_mappings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    course_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("courses.id"), nullable=True
    )
    assignment_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("assignments.id"), nullable=True
    )
    announcement_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("announcements.id"), nullable=True
    )
    submission_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("submissions.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="sent", nullable=False
    )  # sent, failed, suppressed, pending
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
