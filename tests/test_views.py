import datetime
from http import HTTPStatus
from unittest.mock import patch

from fastapi.testclient import TestClient

from backtick import dto, views

client = TestClient(views.app)


@patch(
    "backtick.views.dispatch.submit_tasks",
    new=lambda **kwargs: dto.ScheduleResponseDTO(
        task_ids=["task1", "task2"],
        message="message",
    ),
)
@patch("backtick.dto.utils.discover_task", new=lambda name: lambda: None)
def test_schedule_ok(mock_settings):
    """Test schedule."""

    with patch("backtick.dto.settings", mock_settings):
        dt = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
            days=1
        )
        response = client.post(
            "/schedule",
            json={
                "task_name": "task1",
                "datetimes": [dt.isoformat()],
                "kwargs": {},
            },
        )
        assert response.status_code == HTTPStatus.OK
        json_response = response.json()
        assert json_response["task_ids"] == ["task1", "task2"]
        assert json_response["message"] == "message"


@patch(
    "backtick.views.dispatch.cancel_tasks",
    new=lambda **kwargs: dto.UnscheduleResponseDTO(
        task_ids=["task1", "task2"],
        message="message",
    ),
)
def test_unschedule_ok(mock_settings):
    """Test unschedule."""

    with patch("backtick.dto.settings", mock_settings):
        response = client.post(
            "/unschedule",
            json={"task_ids": ["task1", "task2"], "enqueue_dependents": False},
        )
        assert response.status_code == HTTPStatus.OK
        json_response = response.json()
        assert json_response["task_ids"] == ["task1", "task2"]
        assert json_response["message"] == "message"
