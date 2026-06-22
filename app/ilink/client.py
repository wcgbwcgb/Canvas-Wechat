"""iLink Bot API HTTP client.

All calls go to https://ilinkai.weixin.qq.com.
Requires a Bearer bot_token obtained after QR code scan + confirmation.
"""

import base64
import os
import random
import struct

import httpx

from app.config import settings


def _random_x_wechat_uin() -> str:
    """Generate a random X-WECHAT-UIN header (anti-replay)."""
    u32 = random.randint(0, 0xFFFFFFFF)
    return base64.b64encode(struct.pack(">I", u32)).decode("ascii")


def _auth_headers() -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.ilink_bot_token}",
        "AuthorizationType": "ilink_bot_token",
        "X-WECHAT-UIN": _random_x_wechat_uin(),
    }


class ILinkClient:
    """Async HTTP client for the iLink Bot API."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or settings.ilink_base_url).rstrip("/")
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(45.0))
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    # ------------------------------------------------------------------
    # QR Code / Auth
    # ------------------------------------------------------------------

    async def get_bot_qrcode(self) -> str:
        """Fetch a QR code URL for the user to scan."""
        client = await self._get_client()
        resp = await client.get(
            f"{self.base_url}/ilink/bot/get_bot_qrcode",
            params={"bot_type": 3},
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("qrcode", "")

    async def get_qrcode_status(self, qrcode: str) -> dict:
        """Poll for QR code scan status. Returns {'status': ..., 'bot_token': ...}."""
        client = await self._get_client()
        resp = await client.get(
            f"{self.base_url}/ilink/bot/get_qrcode_status",
            params={"qrcode": qrcode},
        )
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Long-polling
    # ------------------------------------------------------------------

    async def get_updates(self, buf: str) -> dict:
        """Long-poll for new messages (holds up to 35s)."""
        client = await self._get_client()
        resp = await client.post(
            f"{self.base_url}/ilink/bot/getupdates",
            json={
                "get_updates_buf": buf,
                "base_info": {"channel_version": settings.ilink_channel_version},
            },
            headers=_auth_headers(),
            timeout=httpx.Timeout(50.0),
        )
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Send message
    # ------------------------------------------------------------------

    async def send_message(
        self,
        to_user_id: str,
        text: str,
        context_token: str,
    ) -> dict:
        """Send a text reply to a user (requires context_token from last inbound msg)."""
        client = await self._get_client()
        payload = {
            "msg": {
                "to_user_id": to_user_id,
                "message_type": 2,
                "message_state": 2,
                "context_token": context_token,
                "item_list": [
                    {
                        "type": 1,
                        "text_item": {"text": text[:4000]},
                    }
                ],
            }
        }
        resp = await client.post(
            f"{self.base_url}/ilink/bot/sendmessage",
            json=payload,
            headers=_auth_headers(),
        )
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Typing indicator
    # ------------------------------------------------------------------

    async def send_typing(self, to_user_id: str, context_token: str) -> dict:
        """Send 'typing...' indicator."""
        client = await self._get_client()
        # Get typing_ticket first
        cfg = await client.post(
            f"{self.base_url}/ilink/bot/getconfig",
            json={"base_info": {"channel_version": settings.ilink_channel_version}},
            headers=_auth_headers(),
        )
        cfg.raise_for_status()
        typing_ticket = cfg.json().get("typing_ticket", "")

        resp = await client.post(
            f"{self.base_url}/ilink/bot/sendtyping",
            json={
                "to_user_id": to_user_id,
                "context_token": context_token,
                "typing_ticket": typing_ticket,
            },
            headers=_auth_headers(),
        )
        resp.raise_for_status()
        return resp.json()


# Singleton
ilink_client = ILinkClient()
