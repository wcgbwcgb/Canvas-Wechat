"""Sync Canvas enrollments (course roster) for all bound users."""

import datetime
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.user_mapping import UserMapping
from app.sync.canvas_client import get_user_canvas_client

logger = logging.getLogger(__name__)


async def sync_enrollments_for_all_users(db: AsyncSession) -> dict:
    """Sync enrollments (courses) for every active bound user."""
    stmt = select(UserMapping).where(UserMapping.is_active == True)
    result = await db.execute(stmt)
    users = result.scalars().all()

    total_courses_new = 0
    total_enrollments_new = 0
    total_errors = 0

    for user in users:
        try:
            canvas, _ = await get_user_canvas_client(db, user.id)
        except ValueError:
            continue

        try:
            courses_new, enrollments_new = await _sync_user_enrollments(db, canvas, user)
            total_courses_new += courses_new
            total_enrollments_new += enrollments_new
        except Exception as exc:
            logger.error("Failed to sync enrollments for user %d: %s", user.id, exc)
            total_errors += 1

    return {"new_courses": total_courses_new, "new_enrollments": total_enrollments_new, "errors": total_errors}


async def _sync_user_enrollments(db: AsyncSession, canvas, user: UserMapping) -> tuple[int, int]:
    """Sync courses and enrollments for one user. Returns (new_courses, new_enrollments)."""
    courses_new = 0
    enrollments_new = 0

    for raw_course in canvas.get_courses(
        enrollment_state="active",
        include=["term"],
    ):
        # Upsert course
        course_stmt = (
            select(Course)
            .where(Course.canvas_course_id == raw_course.id)
            .where(Course.canvas_domain == user.canvas_domain)
        )
        course_result = await db.execute(course_stmt)
        course = course_result.scalar_one_or_none()

        if course is None:
            course = Course(
                canvas_course_id=raw_course.id,
                canvas_domain=user.canvas_domain,
                name=str(raw_course.name or ""),
                course_code=getattr(raw_course, "course_code", None),
                start_at=_parse_date(getattr(raw_course, "start_at", None)),
                end_at=_parse_date(getattr(raw_course, "end_at", None)),
                workflow_state=str(getattr(raw_course, "workflow_state", "available")),
                syllabus_body=getattr(raw_course, "syllabus_body", None),
                last_synced_at=datetime.datetime.now(datetime.timezone.utc),
            )
            db.add(course)
            await db.flush()
            courses_new += 1

        # Check enrollment
        enroll_stmt = (
            select(Enrollment)
            .where(Enrollment.user_mapping_id == user.id)
            .where(Enrollment.course_id == course.id)
        )
        enroll_result = await db.execute(enroll_stmt)
        enrollment = enroll_result.scalar_one_or_none()

        if enrollment is None:
            # Try to get the actual enrollment from Canvas
            raw_enrollments = list(raw_course.get_enrollments(user_id=user.canvas_user_id))
            if raw_enrollments:
                raw_enrollment = raw_enrollments[0]
                enrollment = Enrollment(
                    canvas_enrollment_id=raw_enrollment.id,
                    user_mapping_id=user.id,
                    course_id=course.id,
                    role=str(getattr(raw_enrollment, "type", "StudentEnrollment")),
                    enrollment_state=str(getattr(raw_enrollment, "enrollment_state", "active")),
                    last_synced_at=datetime.datetime.now(datetime.timezone.utc),
                )
            else:
                # Create a synthetic enrollment based on course listing
                import random

                enrollment = Enrollment(
                    canvas_enrollment_id=random.randint(10**9, 10**10 - 1),
                    user_mapping_id=user.id,
                    course_id=course.id,
                    role="StudentEnrollment",
                    enrollment_state="active",
                    last_synced_at=datetime.datetime.now(datetime.timezone.utc),
                )
            db.add(enrollment)
            enrollments_new += 1
        else:
            enrollment.last_synced_at = datetime.datetime.now(datetime.timezone.utc)

    return courses_new, enrollments_new


def _parse_date(value) -> datetime.datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value
    try:
        return datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
