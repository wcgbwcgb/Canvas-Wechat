"""Celery task: periodic notification check.

Runs every 2 hours during active hours (09:00-21:00 Beijing time).
"""

import datetime
import logging

from celery.utils.log import get_task_logger

from app.sync.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(name="app.notifications.tasks.run_notification_check")
def run_notification_check() -> dict:
    """Run overdue + soon-due checks and dispatch notifications."""
    return _run_async(_notification_check_async())


import asyncio  # noqa: E402


def _run_async(coro) -> dict:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result(timeout=600)
        return asyncio.run(coro)
    except Exception as exc:
        logger.error("Notification check failed: %s", exc)
        return {"error": str(exc)}


async def _notification_check_async() -> dict:
    from app.db.session import async_session_factory
    from app.notifications.checker import (
        find_overdue_assignments,
        find_soon_due_assignments,
        is_quiet_hours,
    )
    from app.notifications.dispatcher import dispatch_notification
    from app.notifications.formatter import (
        format_due_soon_alert,
        format_overdue_alert,
    )
    from app.notifications.rate_limiter import check_and_increment
    from app.models.user_mapping import UserMapping
    from sqlalchemy import select

    if is_quiet_hours():
        return {"skipped": "quiet_hours"}

    async with async_session_factory() as db:
        stats = {"overdue_sent": 0, "overdue_pending": 0, "due_soon_sent": 0, "due_soon_pending": 0}

        # --- Overdue checks ---
        overdue = await find_overdue_assignments(db)
        for item in overdue:
            # Rate check
            if not await check_and_increment(item["user_mapping_id"]):
                continue

            user_stmt = select(UserMapping).where(
                UserMapping.id == item["user_mapping_id"]
            )
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()
            if not user:
                continue

            due_str = item["due_at"].strftime("%Y-%m-%d %H:%M") if item["due_at"] else "未知"
            text = format_overdue_alert(
                course_name=item["course_name"],
                assignment_name=item["assignment_name"],
                due_at_str=due_str,
                days_overdue=item["days_overdue"],
                html_url=item.get("html_url") or "",
            )

            status = await dispatch_notification(
                db=db,
                user=user,
                notification_type="overdue",
                text=text,
                assignment_id=item["assignment_id"],
            )

            if status == "sent":
                stats["overdue_sent"] += 1
            elif status == "pending":
                stats["overdue_pending"] += 1

        # --- Due-soon checks ---
        due_soon = await find_soon_due_assignments(db, hours_ahead=24)
        for item in due_soon:
            if not await check_and_increment(item["user_mapping_id"]):
                continue

            user_stmt = select(UserMapping).where(
                UserMapping.id == item["user_mapping_id"]
            )
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()
            if not user:
                continue

            due_str = item["due_at"].strftime("%Y-%m-%d %H:%M") if item["due_at"] else "未知"
            text = format_due_soon_alert(
                course_name=item["course_name"],
                assignment_name=item["assignment_name"],
                due_at_str=due_str,
                hours_left=item["hours_left"],
                html_url=item.get("html_url") or "",
            )

            status = await dispatch_notification(
                db=db,
                user=user,
                notification_type="due_soon",
                text=text,
                assignment_id=item["assignment_id"],
            )

            if status == "sent":
                stats["due_soon_sent"] += 1
            elif status == "pending":
                stats["due_soon_pending"] += 1

        await db.commit()
        return stats
