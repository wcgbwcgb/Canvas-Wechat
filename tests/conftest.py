"""Pytest fixtures for canvas-wechat tests."""

import pytest


@pytest.fixture
def anyio_backend():
    return "asyncio"
