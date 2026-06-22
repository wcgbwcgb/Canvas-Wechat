"""Canvas LMS REST API client wrapper.

Wraps canvasapi (ucfopen) with OAuth2 token lifecycle management,
per-user encrypted token storage, and rate-limit-aware fetching.
"""

import logging
import time
from collections.abc import Iterator

from canvasapi import Canvas
from canvasapi.paginated_list import PaginatedList
from sqlalchemy import select

from app.config import settings

logger = logging.getLogger(__name__)

# Approx rate limit: ~700 requests per 10 minutes → ~1.16 req/s
# Be conservative: max 1 req/s with 200ms padding
MIN_REQUEST_INTERVAL = 0.2  # seconds between paginated requests


def get_canvas_client(access_token: str) -> Canvas:
    """Create a Canvas API client for a given OAuth2 access token."""
    return Canvas(settings.canvas_base_url, access_token)


def paginate_with_delay(paginated: PaginatedList) -> Iterator:
    """Iterate over a PaginatedList with rate-limit-friendly delays."""
    last_request = 0.0
    for item in paginated:
        elapsed = time.monotonic() - last_request
        if elapsed < MIN_REQUEST_INTERVAL:
            time.sleep(MIN_REQUEST_INTERVAL - elapsed)
        last_request = time.monotonic()
        yield item


async def get_user_canvas_client(db, user_mapping_id: int):
    """Get a Canvas client for a specific user (with decrypted token).

    Returns (Canvas, user_mapping) or raises ValueError if token is missing/expired.
    """
    from app.auth.canvas_oauth import decrypt_token, refresh_access_token
    from app.models.user_mapping import UserMapping

    stmt = select(UserMapping).where(UserMapping.id == user_mapping_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise ValueError(f"UserMapping {user_mapping_id} not found")

    if not user.encrypted_access_token:
        raise ValueError(f"No Canvas token for user {user_mapping_id} — needs re-bind")

    access_token = decrypt_token(user.encrypted_access_token)

    # Refresh if expired
    if user.token_expires_at and user.token_expires_at.timestamp() < time.time() + 60:
        if user.encrypted_refresh_token:
            refresh_token_str = decrypt_token(user.encrypted_refresh_token)
            new_tokens = await refresh_access_token(refresh_token_str)
            from app.auth.canvas_oauth import encrypt_token

            user.encrypted_access_token = encrypt_token(new_tokens["access_token"])
            user.encrypted_refresh_token = encrypt_token(new_tokens["refresh_token"])
            user.token_expires_at = new_tokens["expires_at"]
            await db.flush()
            access_token = new_tokens["access_token"]
        else:
            raise ValueError(f"Canvas token expired and no refresh token for user {user_mapping_id}")

    return get_canvas_client(access_token), user
