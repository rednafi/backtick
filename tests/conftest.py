import pytest


@pytest.fixture()
def mock_settings():
    class Settings:
        BACKTICK_TASKS = {
            "task1": lambda *, foo, bar: (foo, bar),
            "task2": lambda **kwargs: kwargs,
        }
        BACKTICK_QUEUES = {"default": "queue1", "other": "queue2"}

    return Settings()
