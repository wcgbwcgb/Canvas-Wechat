"""User-course enrollment mapping."""

import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Enrollment(Base, TimestampMixin):
    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    canvas_enrollment_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False
    )
    user_mapping_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user_mappings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(50), default="StudentEnrollment")
    enrollment_state: Mapped[str] = mapped_column(
        String(50), default="active", index=True
    )
    last_synced_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
