from unittest.mock import patch

from backtick import settings


def test_settings(mock_settings):
    with patch("tests.test_settings.settings", mock_settings):
        assert settings.BACKTICK_TASKS == mock_settings.BACKTICK_TASKS
        assert settings.BACKTICK_QUEUES == mock_settings.BACKTICK_QUEUES
