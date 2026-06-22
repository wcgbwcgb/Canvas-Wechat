"""Sync Canvas announcements (discussion_topics flagged as announcements)."""

import datetime
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.announcement import Announcement
from app.models.course import Course
from app.models.user_mapping import UserMapping
from app.sync.canvas_client import get_user_canvas_client
from app.sync.delta_detector import publish_delta

logger = logging.getLogger(__name__)


async def sync_announcements_for_all_users(db: AsyncSession) -> dict:
    """Sync announcements for every active bound user."""
    stmt = select(UserMapping).where(UserMapping.is_active == True)
    result = await db.execute(stmt)
    users = result.scalars().all()

    total_new = 0
    total_errors = 0

    for user in users:
        try:
            canvas, _ = await get_user_canvas_client(db, user.id)
        except ValueError:
            continue  # No valid token

        # Get enrolled courses
        from app.models.enrollment import Enrollment

        enroll_stmt = (
            select(Enrollment)
            .where(Enrollment.user_mapping_id == user.id)
            .where(Enrollment.enrollment_state == "active")
        )
        enroll_result = await db.execute(enroll_stmt)
        enrollments = enroll_result.scalars().all()

        for enrollment in enrollments:
            course_stmt = select(Course).where(Course.id == enrollment.course_id)
            course_result = await db.execute(course_stmt)
            course = course_result.scalar_one_or_none()
            if course is None:
                continue

            try:
                new_count = await _sync_course_announcements(db, canvas, course)
                total_new += new_count
            except Exception as exc:
                logger.error("Failed to sync announcements for course %s: %s", course.canvas_course_id, exc)
                total_errors += 1

        # Update last_synced_at
        user.updated_at = datetime.datetime.now(datetime.timezone.utc)

    return {"new_announcements": total_new, "errors": total_errors}


async def _sync_course_announcements(db: AsyncSession, canvas, course: Course) -> int:
    """Sync announcements for a single course. Returns count of new announcements."""
    canvas_course = canvas.get_course(course.canvas_course_id)

    new_count = 0
    for topic in canvas_course.get_discussion_topics(only_announcements=True):
        # Check if we already have this announcement
        existing_stmt = (
            select(Announcement)
            .where(Announcement.canvas_topic_id == topic.id)
            .where(Announcement.course_id == course.id)
        )
        existing_result = await db.execute(existing_stmt)
        existing = existing_result.scalar_one_or_none()

        if existing is None:
            announcement = Announcement(
                canvas_topic_id=topic.id,
                course_id=course.id,
                title=str(topic.title or ""),
                message=str(topic.message or ""),
                posted_at=_parse_canvas_date(getattr(topic, "posted_at", None)),
                author_name=getattr(getattr(topic, "author", None), "display_name", None),
                last_synced_at=datetime.datetime.now(datetime.timezone.utc),
            )
            db.add(announcement)
            new_count += 1

            # Publish delta for notification engine
            await publish_delta(db, "announcement_created", {
                "topic_id": topic.id,
                "course_id": course.id,
                "title": str(topic.title or ""),
            })
        else:
            existing.last_synced_at = datetime.datetime.now(datetime.timezone.utc)

    return new_count


def _parse_canvas_date(value) -> datetime.datetime | None:
    """Parse Canvas date strings to datetime."""
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value
    try:
        return datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
