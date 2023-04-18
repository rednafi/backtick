from unittest.mock import patch

from backtick import dispatch, utils
import rq
import time
import pytest

class FakeScheduleRequestDTO:
    def __init__(self, task_name, datetimes=None, kwargs=None):
        self.task_name = task_name
        self.datetimes = datetimes
        self.kwargs = kwargs


@utils.task("default", utils.get_redis())
def vanilla_task():
    return "result"


@pytest.mark.integration
@patch("backtick.dispatch.utils.discover_task", new=lambda _: vanilla_task)
def test_submit_tasks_ok(mock_settings):
    with patch("backtick.dispatch.settings", mock_settings):
        response = dispatch.submit_tasks(
            schedule_request_dto=FakeScheduleRequestDTO(
                task_name="task1",
                kwargs={},
            )
        )

        task_id = response.task_ids[0]
        task = rq.job.Job.fetch(task_id, utils.get_redis())

        assert task.id == task_id
        assert task.origin == "default"

        time.sleep(1)
        result = task.latest_result()
        assert result.Type.SUCCESSFUL
        assert result.return_value == "result"
