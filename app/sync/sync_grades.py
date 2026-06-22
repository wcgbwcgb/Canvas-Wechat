"""Sync Canvas submissions (grades) for all enrolled users."""

import datetime
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assignment import Assignment
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.submission import Submission
from app.models.user_mapping import UserMapping
from app.sync.canvas_client import get_user_canvas_client
from app.sync.delta_detector import publish_delta
from app.sync.sync_announcements import _parse_canvas_date

logger = logging.getLogger(__name__)


async def sync_grades_for_all_users(db: AsyncSession) -> dict:
    """Sync submissions/grades for all enrolled users."""
    stmt = (
        select(Enrollment)
        .where(Enrollment.enrollment_state == "active")
    )
    result = await db.execute(stmt)
    enrollments = result.scalars().all()

    total_new = 0
    total_grade_changes = 0
    total_errors = 0

    for enrollment in enrollments:
        # Get the course
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
            canvas_course = canvas.get_course(course.canvas_course_id)
            # Get all assignments for this course
            assignment_stmt = (
                select(Assignment)
                .where(Assignment.course_id == course.id)
            )
            assign_result = await db.execute(assignment_stmt)
            assignments = assign_result.scalars().all()

            for assignment in assignments:
                try:
                    new, grade_changes = await _sync_assignment_submissions(
                        db, canvas_course, assignment, enrollment.user_mapping_id
                    )
                    total_new += new
                    total_grade_changes += grade_changes
                except Exception as exc:
                    logger.error(
                        "Failed to sync submissions for assignment %s: %s",
                        assignment.canvas_assignment_id,
                        exc,
                    )
                    total_errors += 1

        except Exception as exc:
            logger.error("Failed to sync grades for course %s: %s", course.canvas_course_id, exc)
            total_errors += 1

    return {"new_submissions": total_new, "grade_changes": total_grade_changes, "errors": total_errors}


async def _sync_assignment_submissions(
    db: AsyncSession,
    canvas_course,
    assignment: Assignment,
    user_mapping_id: int,
) -> tuple[int, int]:
    """Sync submissions for one assignment. Returns (new_count, grade_change_count)."""
    canvas_assignment = canvas_course.get_assignment(assignment.canvas_assignment_id)

    new_count = 0
    grade_change_count = 0

    for raw in canvas_assignment.get_submissions():
        existing_stmt = (
            select(Submission)
            .where(Submission.canvas_submission_id == raw.id)
        )
        existing_result = await db.execute(existing_stmt)
        existing = existing_result.scalar_one_or_none()

        score = float(raw.score) if raw.score else None
        grade = str(raw.grade) if raw.grade else None

        if existing is None:
            submission = Submission(
                canvas_submission_id=raw.id,
                canvas_assignment_id=assignment.canvas_assignment_id,
                user_mapping_id=user_mapping_id,
                course_id=assignment.course_id,
                score=score,
                grade=grade,
                submitted_at=_parse_canvas_date(getattr(raw, "submitted_at", None)),
                graded_at=_parse_canvas_date(getattr(raw, "graded_at", None)),
                workflow_state=str(getattr(raw, "workflow_state", "")),
                late=bool(getattr(raw, "late", False)),
                missing=bool(getattr(raw, "missing", False)),
                last_synced_at=datetime.datetime.now(datetime.timezone.utc),
            )
            db.add(submission)
            new_count += 1

            if score is not None:
                await publish_delta(db, "grade_posted", {
                    "submission_id": raw.id,
                    "assignment_id": assignment.canvas_assignment_id,
                    "user_mapping_id": user_mapping_id,
                    "score": score,
                })
        else:
            old_score = existing.score
            old_grade = existing.grade

            existing.score = score
            existing.grade = grade
            existing.submitted_at = _parse_canvas_date(getattr(raw, "submitted_at", None))
            existing.graded_at = _parse_canvas_date(getattr(raw, "graded_at", None))
            existing.workflow_state = str(getattr(raw, "workflow_state", ""))
            existing.late = bool(getattr(raw, "late", False))
            existing.missing = bool(getattr(raw, "missing", False))
            existing.last_synced_at = datetime.datetime.now(datetime.timezone.utc)

            if score != old_score or grade != old_grade:
                grade_change_count += 1
                await publish_delta(db, "grade_changed", {
                    "submission_id": raw.id,
                    "assignment_id": assignment.canvas_assignment_id,
                    "user_mapping_id": user_mapping_id,
                    "old_score": old_score,
                    "new_score": score,
                })

    return new_count, grade_change_count
