"""Notification checkers — detect overdue and soon-due assignments."""

import datetime
import logging

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assignment import Assignment
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.submission import Submission
from app.models.user_mapping import UserMapping

logger = logging.getLogger(__name__)


async def find_overdue_assignments(
    db: AsyncSession,
) -> list[dict]:
    """Find assignments past due with no submission.

    Returns list of dicts with keys:
      user_mapping_id, wechat_user_id, course_name, assignment_name,
      due_at, days_overdue, html_url
    """
    now = datetime.datetime.now(datetime.timezone.utc)

    stmt = (
        select(
            UserMapping.id.label("user_mapping_id"),
            UserMapping.wechat_user_id,
            Course.name.label("course_name"),
            Assignment.id.label("assignment_id"),
            Assignment.name.label("assignment_name"),
            Assignment.due_at,
            Assignment.html_url,
        )
        .select_from(UserMapping)
        .join(Enrollment, Enrollment.user_mapping_id == UserMapping.id)
        .join(Course, Course.id == Enrollment.course_id)
        .join(Assignment, Assignment.course_id == Course.id)
        .outerjoin(
            Submission,
            (Submission.canvas_assignment_id == Assignment.canvas_assignment_id)
            & (Submission.user_mapping_id == UserMapping.id),
        )
        .where(UserMapping.is_active == True)
        .where(Enrollment.enrollment_state == "active")
        .where(Assignment.due_at.isnot(None))
        .where(Assignment.due_at < now)
        .where(Assignment.workflow_state == "published")
        .where(
            (Submission.id.is_(None))
            | (Submission.submitted_at.is_(None))
        )
    )

    result = await db.execute(stmt)
    rows = result.all()

    results = []
    for row in rows:
        days_overdue = (now - row.due_at).days
        results.append({
            "user_mapping_id": row.user_mapping_id,
            "wechat_user_id": row.wechat_user_id,
            "course_name": row.course_name,
            "assignment_id": row.assignment_id,
            "assignment_name": row.assignment_name,
            "due_at": row.due_at,
            "days_overdue": days_overdue,
            "html_url": row.html_url,
        })

    return results


async def find_soon_due_assignments(
    db: AsyncSession,
    hours_ahead: int = 24,
) -> list[dict]:
    """Find assignments due within the next N hours that haven't been submitted."""
    now = datetime.datetime.now(datetime.timezone.utc)
    cutoff = now + datetime.timedelta(hours=hours_ahead)

    stmt = (
        select(
            UserMapping.id.label("user_mapping_id"),
            UserMapping.wechat_user_id,
            Course.name.label("course_name"),
            Assignment.id.label("assignment_id"),
            Assignment.name.label("assignment_name"),
            Assignment.due_at,
            Assignment.html_url,
        )
        .select_from(UserMapping)
        .join(Enrollment, Enrollment.user_mapping_id == UserMapping.id)
        .join(Course, Course.id == Enrollment.course_id)
        .join(Assignment, Assignment.course_id == Course.id)
        .outerjoin(
            Submission,
            (Submission.canvas_assignment_id == Assignment.canvas_assignment_id)
            & (Submission.user_mapping_id == UserMapping.id),
        )
        .where(UserMapping.is_active == True)
        .where(Enrollment.enrollment_state == "active")
        .where(Assignment.due_at.isnot(None))
        .where(Assignment.due_at.between(now, cutoff))
        .where(Assignment.workflow_state == "published")
        .where(
            (Submission.id.is_(None))
            | (Submission.submitted_at.is_(None))
        )
    )

    result = await db.execute(stmt)
    rows = result.all()

    results = []
    for row in rows:
        hours_left = (row.due_at - now).total_seconds() / 3600
        results.append({
            "user_mapping_id": row.user_mapping_id,
            "wechat_user_id": row.wechat_user_id,
            "course_name": row.course_name,
            "assignment_id": row.assignment_id,
            "assignment_name": row.assignment_name,
            "due_at": row.due_at,
            "hours_left": round(hours_left, 1),
            "html_url": row.html_url,
        })

    return results


def is_quiet_hours() -> bool:
    """Check if current Beijing time is within quiet hours."""
    from app.config import settings

    now_beijing = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
    hour = now_beijing.hour
    if settings.quiet_hours_start > settings.quiet_hours_end:
        # Crosses midnight, e.g. 22:00-08:00
        return hour >= settings.quiet_hours_start or hour < settings.quiet_hours_end
    else:
        return settings.quiet_hours_start <= hour < settings.quiet_hours_end
