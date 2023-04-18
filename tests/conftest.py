"""Canned objects for testing."""

from unittest.mock import MagicMock

import pytest
import redis


@pytest.fixture()
def mock_settings():
    """Return canned settings."""

    class Settings:
        BACKTICK_TASKS = {
            "task1": "backtick.tests.tasks.task1",
            "task2": "backtick.tasks.task2",
        }
        BACKTICK_QUEUES = {"default": "queue1", "other": "queue2"}

    return Settings()


@pytest.fixture()
def mock_redis():
    return MagicMock(spec=redis.Redis)
