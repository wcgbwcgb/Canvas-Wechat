"""FastAPI application entry point.

Wires together:
  - iLink Bot API long-polling (background asyncio task)
  - Canvas OAuth2 callback endpoint
  - Health check and status endpoints
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.config import settings
from app.ilink.poller import poll_loop

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Background task handle for the iLink poller
_poller_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start iLink poller on startup, stop on shutdown."""
    global _poller_task

    # Start the iLink long-polling loop
    _poller_task = asyncio.create_task(poll_loop())
    logger.info("iLink poller started as background task")

    yield

    # Shutdown
    if _poller_task is not None:
        _poller_task.cancel()
        try:
            await _poller_task
        except asyncio.CancelledError:
            pass
    logger.info("iLink poller stopped")

    # Close redis
    from app.db.redis import close_redis
    await close_redis()


app = FastAPI(
    title="Canvas-WeChat Clawbot",
    description="AI-powered Canvas LMS assistant accessible via WeChat iLink Bot API",
    version="0.1.0",
    lifespan=lifespan,
)


# ------------------------------------------------------------------
# Middleware
# ------------------------------------------------------------------

from app.middleware.error_handler import LoggingMiddleware  # noqa: E402

app.add_middleware(LoggingMiddleware)


# ------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/status")
async def status():
    """Detailed status including iLink connection."""
    from app.db.redis import get_redis

    redis_ok = False
    db_ok = False

    try:
        r = await get_redis()
        await r.ping()
        redis_ok = True
    except Exception:
        pass

    try:
        from app.db.session import engine
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        db_ok = True
    except Exception:
        pass

    return {
        "redis": "connected" if redis_ok else "disconnected",
        "postgres": "connected" if db_ok else "disconnected",
        "ilink_token": "configured" if settings.ilink_bot_token else "not_configured",
        "canvas": f"configured ({settings.canvas_base_url})" if settings.canvas_client_id else "not_configured",
    }


# ------------------------------------------------------------------
# Canvas OAuth2 Callback
# ------------------------------------------------------------------

@app.get("/auth/canvas/callback")
async def canvas_oauth2_callback(
    code: str = Query(...),
    state: str = Query(...),
):
    """Handle Canvas OAuth2 redirect after user authorizes the app."""
    from app.db.session import async_session_factory
    from app.auth.bind_flow import handle_canvas_callback

    async with async_session_factory() as db:
        try:
            message = await handle_canvas_callback(db, code, state)
            await db.commit()
            return HTMLResponse(
                content=f"""
                <html>
                <head><meta charset="utf-8"><title>Canvas 绑定</title></head>
                <body style="font-family: sans-serif; max-width: 600px; margin: 50px auto; padding: 20px;">
                    <pre style="white-space: pre-wrap;">{message}</pre>
                    <p>你现在可以返回微信继续使用 Canvas 助教了。</p>
                </body>
                </html>
                """
            )
        except Exception as exc:
            await db.rollback()
            logger.error("Canvas OAuth2 callback failed: %s", exc)
            return HTMLResponse(
                content=f"<h1>绑定失败</h1><p>{exc}</p>",
                status_code=500,
            )


# ------------------------------------------------------------------
# iLink QR Code endpoint (for initial setup)
# ------------------------------------------------------------------

@app.get("/ilink/qrcode")
async def get_ilink_qrcode():
    """Return a QR code URL for iLink Bot setup.

    The user scans this QR code in WeChat to connect their account.
    After scanning, the bot_token is stored in settings (or manually set).
    """
    from app.ilink.client import ilink_client

    try:
        qrcode = await ilink_client.get_bot_qrcode()
        return {
            "qrcode_url": qrcode,
            "instructions": "Scan this QR code in WeChat to connect your bot account. "
                            "After scanning, set ILINK_BOT_TOKEN in your .env file.",
        }
    except Exception as exc:
        return JSONResponse(
            content={"error": str(exc)},
            status_code=500,
        )
