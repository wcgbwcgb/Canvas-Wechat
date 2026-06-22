"""Canvas OAuth2 token lifecycle — encryption, refresh, exchange."""

import datetime
import logging
import time

import httpx
from cryptography.fernet import Fernet

from app.config import settings

logger = logging.getLogger(__name__)


def _get_fernet() -> Fernet:
    """Derive a Fernet key from the configured encryption key."""
    import base64
    import hashlib

    key = hashlib.sha256(settings.canvas_token_encryption_key.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_token(token: str) -> str:
    """Encrypt a Canvas OAuth2 token for DB storage."""
    f = _get_fernet()
    return f.encrypt(token.encode()).decode()


def decrypt_token(encrypted: str) -> str:
    """Decrypt a Canvas OAuth2 token from DB storage."""
    f = _get_fernet()
    return f.decrypt(encrypted.encode()).decode()


async def exchange_code_for_token(code: str) -> dict:
    """Exchange an authorization code for access + refresh tokens.

    Returns:
        {
            "access_token": str,
            "refresh_token": str,
            "expires_in": int,  # seconds
            "expires_at": datetime,
            "canvas_user_id": int,
            "canvas_name": str,
            "canvas_email": str,
        }
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            settings.canvas_oauth2_token_url,
            data={
                "grant_type": "authorization_code",
                "client_id": settings.canvas_client_id,
                "client_secret": settings.canvas_client_secret,
                "redirect_uri": settings.canvas_redirect_uri,
                "code": code,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    access_token = data["access_token"]
    expires_in = data.get("expires_in", 3600)
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        seconds=expires_in - 60  # refresh 1 minute before expiry
    )

    # Fetch user info
    from canvasapi import Canvas

    canvas = Canvas(settings.canvas_base_url, access_token)
    user = canvas.get_current_user()

    return {
        "access_token": access_token,
        "refresh_token": data["refresh_token"],
        "expires_in": expires_in,
        "expires_at": expires_at,
        "canvas_user_id": user.id,
        "canvas_name": getattr(user, "name", None) or user.short_name,
        "canvas_email": getattr(user, "email", None),
    }


async def refresh_access_token(refresh_token: str) -> dict:
    """Refresh an expired Canvas access token.

    Returns:
        {
            "access_token": str,
            "refresh_token": str,
            "expires_in": int,
            "expires_at": datetime,
        }
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            settings.canvas_oauth2_token_url,
            data={
                "grant_type": "refresh_token",
                "client_id": settings.canvas_client_id,
                "client_secret": settings.canvas_client_secret,
                "refresh_token": refresh_token,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    expires_in = data.get("expires_in", 3600)
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        seconds=expires_in - 60
    )

    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expires_in": expires_in,
        "expires_at": expires_at,
    }
