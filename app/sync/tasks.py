"""Celery tasks for Canvas data synchronization."""

import logging

from celery.utils.log import get_task_logger

from app.sync.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(name="app.sync.tasks.sync_announcements")
def sync_announcements() -> dict:
    """Sync announcements for all active users (every 5 min)."""
    return _run_async(_sync_announcements_async())


@celery_app.task(name="app.sync.tasks.sync_assignments")
def sync_assignments() -> dict:
    """Sync assignments for all active users (every 15 min)."""
    return _run_async(_sync_assignments_async())


@celery_app.task(name="app.sync.tasks.sync_grades")
def sync_grades() -> dict:
    """Sync submissions/grades for all active users (every hour)."""
    return _run_async(_sync_grades_async())


@celery_app.task(name="app.sync.tasks.sync_enrollments")
def sync_enrollments() -> dict:
    """Sync enrollment rosters (every 6 hours)."""
    return _run_async(_sync_enrollments_async())


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

import asyncio  # noqa: E402


def _run_async(coro) -> dict:
    """Run an async coroutine from a sync Celery task.

    Celery worker tasks run in a forked process where no running event loop
    exists on the current thread. asyncio.run() creates a fresh loop each
    call, which is exactly what we want here — never use get_event_loop().
    """
    try:
        return asyncio.run(coro)
    except Exception as exc:
        logger.error("Task failed: %s", exc)
        return {"error": str(exc)}


# ------------------------------------------------------------------
# Actual sync logic (runs in async context)
# ------------------------------------------------------------------


async def _sync_announcements_async() -> dict:
    from app.db.session import async_session_factory
    from app.sync.sync_announcements import sync_announcements_for_all_users

    async with async_session_factory() as db:
        stats = await sync_announcements_for_all_users(db)
        await db.commit()
    return stats


async def _sync_assignments_async() -> dict:
    from app.db.session import async_session_factory
    from app.sync.sync_assignments import sync_assignments_for_all_users

    async with async_session_factory() as db:
        stats = await sync_assignments_for_all_users(db)
        await db.commit()
    return stats


async def _sync_grades_async() -> dict:
    from app.db.session import async_session_factory
    from app.sync.sync_grades import sync_grades_for_all_users

    async with async_session_factory() as db:
        stats = await sync_grades_for_all_users(db)
        await db.commit()
    return stats


async def _sync_enrollments_async() -> dict:
    from app.db.session import async_session_factory
    from app.sync.sync_enrollments import sync_enrollments_for_all_users

    async with async_session_factory() as db:
        stats = await sync_enrollments_for_all_users(db)
        await db.commit()
    return stats
