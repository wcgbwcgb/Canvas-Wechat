#!/usr/bin/env python3
"""Verify that all dependencies and configuration are correct.

Usage:
    python scripts/setup_check.py
"""

import sys


def check_imports() -> bool:
    """Verify all required packages are importable."""
    packages = [
        "fastapi",
        "uvicorn",
        "httpx",
        "sqlalchemy",
        "redis",
        "celery",
        "pydantic",
        "pydantic_settings",
        "canvasapi",
        "cryptography",
        "structlog",
    ]
    ok = True
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"  ✅ {pkg}")
        except ImportError:
            print(f"  ❌ {pkg} — not installed")
            ok = False
    return ok


def check_config() -> bool:
    """Verify required env vars are set."""
    from app.config import settings

    checks = [
        ("CANVAS_BASE_URL", settings.canvas_base_url, "https://canvas.instructure.com"),
        ("CANVAS_CLIENT_ID", settings.canvas_client_id, ""),
        ("CANVAS_CLIENT_SECRET", bool(settings.canvas_client_secret), True),
        ("DATABASE_URL", settings.database_url, ""),
        ("REDIS_URL", settings.redis_url, ""),
    ]

    ok = True
    for name, value, required in checks:
        if required and not value:
            print(f"  ⚠️  {name} — not configured")
        elif value and value != required:
            print(f"  ✅ {name} = {value[:50]}...")
        elif value == required:
            print(f"  ⚠️  {name} — using default ({value})")
        else:
            print(f"  ✅ {name} — OK")

    return ok


def main():
    print("Canvas-WeChat Clawbot — Setup Check\n")

    print("📦 Checking imports...")
    imports_ok = check_imports()

    print("\n⚙️  Checking configuration...")
    config_ok = check_config()

    print("\n" + "=" * 50)
    if imports_ok and config_ok:
        print("✅ All checks passed!")
    else:
        print("❌ Some checks failed. See details above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
