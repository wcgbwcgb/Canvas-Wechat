"""Canvas submission model — student work for an assignment."""

import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Submission(Base, TimestampMixin):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    canvas_submission_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False
    )
    canvas_assignment_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
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
    )
    score: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    grade: Mapped[str | None] = mapped_column(String(50), nullable=True)
    submitted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    graded_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    workflow_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    late: Mapped[bool] = mapped_column(Boolean, default=False)
    missing: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    last_synced_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
