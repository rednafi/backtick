from backtick import settings
from unittest.mock import patch

def test_settings(mock_settings):
    with patch("backtick.settings", mock_settings):
        assert settings.BACKTICK_TASKS == mock_settings.BACKTICK_TASKS
        assert settings.BACKTICK_QUEUES == mock_settings.BACKTICK_QUEUES
