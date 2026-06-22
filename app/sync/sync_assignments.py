"""Sync Canvas assignments for all enrolled courses."""

import datetime
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assignment import Assignment
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.user_mapping import UserMapping
from app.sync.canvas_client import get_user_canvas_client
from app.sync.delta_detector import publish_delta
from app.sync.sync_announcements import _parse_canvas_date

logger = logging.getLogger(__name__)


async def sync_assignments_for_all_users(db: AsyncSession) -> dict:
    """Sync assignments for every active bound user."""
    stmt = (
        select(Enrollment)
        .where(Enrollment.enrollment_state == "active")
    )
    result = await db.execute(stmt)
    enrollments = result.scalars().all()

    # Deduplicate courses — use a single user token per course
    processed_courses: set[int] = set()
    total_new = 0
    total_updated = 0
    total_errors = 0

    for enrollment in enrollments:
        if enrollment.course_id in processed_courses:
            continue
        processed_courses.add(enrollment.course_id)

        course_stmt = select(Course).where(Course.id == enrollment.course_id)
        course_result = await db.execute(course_stmt)
        course = course_result.scalar_one_or_none()
        if course is None:
            continue

        try:
            canvas, _ = await get_user_canvas_client(db, enrollment.user_mapping_id)
        except ValueError:
            continue

        try:
            new, updated = await _sync_course_assignments(db, canvas, course)
            total_new += new
            total_updated += updated
        except Exception as exc:
            logger.error("Failed to sync assignments for course %s: %s", course.canvas_course_id, exc)
            total_errors += 1

    return {"new_assignments": total_new, "updated_assignments": total_updated, "errors": total_errors}


async def _sync_course_assignments(db: AsyncSession, canvas, course: Course) -> tuple[int, int]:
    """Sync assignments for a single course. Returns (new_count, updated_count)."""
    canvas_course = canvas.get_course(course.canvas_course_id)

    new_count = 0
    updated_count = 0

    for raw in canvas_course.get_assignments():
        existing_stmt = (
            select(Assignment)
            .where(Assignment.canvas_assignment_id == raw.id)
            .where(Assignment.course_id == course.id)
        )
        existing_result = await db.execute(existing_stmt)
        existing = existing_result.scalar_one_or_none()

        due_at = _parse_canvas_date(getattr(raw, "due_at", None))

        if existing is None:
            assignment = Assignment(
                canvas_assignment_id=raw.id,
                course_id=course.id,
                name=str(raw.name or ""),
                description=str(raw.description or "") if raw.description else None,
                due_at=due_at,
                unlock_at=_parse_canvas_date(getattr(raw, "unlock_at", None)),
                lock_at=_parse_canvas_date(getattr(raw, "lock_at", None)),
                points_possible=float(raw.points_possible) if raw.points_possible else None,
                submission_types=list(raw.submission_types) if raw.submission_types else None,
                workflow_state=str(getattr(raw, "workflow_state", "published")),
                html_url=getattr(raw, "html_url", None),
                last_synced_at=datetime.datetime.now(datetime.timezone.utc),
            )
            db.add(assignment)
            new_count += 1

            if due_at:
                await publish_delta(db, "assignment_created", {
                    "assignment_id": raw.id,
                    "course_id": course.id,
                    "name": str(raw.name or ""),
                    "due_at": due_at.isoformat(),
                })
        else:
            # Check if due_at changed
            old_due = existing.due_at
            existing.name = str(raw.name or "")
            existing.description = str(raw.description or "") if raw.description else None
            existing.due_at = due_at
            existing.unlock_at = _parse_canvas_date(getattr(raw, "unlock_at", None))
            existing.lock_at = _parse_canvas_date(getattr(raw, "lock_at", None))
            existing.points_possible = float(raw.points_possible) if raw.points_possible else None
            existing.submission_types = list(raw.submission_types) if raw.submission_types else None
            existing.workflow_state = str(getattr(raw, "workflow_state", "published"))
            existing.html_url = getattr(raw, "html_url", None)
            existing.last_synced_at = datetime.datetime.now(datetime.timezone.utc)
            updated_count += 1

            if due_at != old_due:
                await publish_delta(db, "assignment_updated", {
                    "assignment_id": raw.id,
                    "course_id": course.id,
                    "name": str(raw.name or ""),
                    "due_at": due_at.isoformat() if due_at else None,
                })

    return new_count, updated_count
