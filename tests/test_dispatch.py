import datetime
import time
from unittest.mock import patch

import pytest
import rq

from backtick import dispatch, utils


class FakeScheduleRequestDTO:
    def __init__(self, task_name, datetimes=None, kwargs=None):
        self.task_name = task_name
        self.datetimes = datetimes
        self.kwargs = kwargs


@utils.task("default", utils.get_redis())
def task_ok():
    return "result"


@utils.task("default", utils.get_redis())
def task_error():
    raise ValueError("fail")


@utils.task("default", utils.get_redis(), retry=utils.Retry(max=3, interval=[1, 2, 3]))
def task_retry():
    raise ValueError("fail")


@pytest.mark.integration()
@patch("backtick.dispatch.utils.discover_task", new=lambda _: task_ok)
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


@pytest.mark.integration()
@patch("backtick.dispatch.utils.discover_task", new=lambda _: task_error)
def test_submit_tasks_error(mock_settings):
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
        assert result.Type.FAILED
        assert "ValueError: fail" in result.exc_string


@pytest.mark.integration()
@patch("backtick.dispatch.utils.discover_task", new=lambda _: task_retry)
def test_submit_tasks_retry(mock_settings):
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
        assert task.retries_left == 3
        assert task.retry_intervals == [1, 2, 3]


@pytest.mark.integration()
@patch("backtick.dispatch.utils.discover_task", new=lambda _: task_ok)
def test_submit_scheduled_tasks_ok(mock_settings):
    with patch("backtick.dispatch.settings", mock_settings):
        dt = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
            seconds=5
        )
        response = dispatch.submit_tasks(
            schedule_request_dto=FakeScheduleRequestDTO(
                task_name="task1",
                datetimes=[dt],
                kwargs={},
            )
        )

        task_id = response.task_ids[0]
        task = rq.job.Job.fetch(task_id, utils.get_redis())

        assert task.id == task_id
        assert task.origin == "default"

        time.sleep(6)
        result = task.latest_result()
        assert result.Type.SUCCESSFUL
        assert result.return_value == "result"


@pytest.mark.integration()
@patch("backtick.dispatch.utils.discover_task", new=lambda _: task_error)
def test_submit_scheduled_tasks_error(mock_settings):
    with patch("backtick.dispatch.settings", mock_settings):
        dt = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
            seconds=5
        )
        response = dispatch.submit_tasks(
            schedule_request_dto=FakeScheduleRequestDTO(
                task_name="task1",
                datetimes=[dt],
                kwargs={},
            )
        )

        task_id = response.task_ids[0]
        task = rq.job.Job.fetch(task_id, utils.get_redis())

        assert task.id == task_id
        assert task.origin == "default"

        time.sleep(6)
        result = task.latest_result()

        assert result.Type.FAILED
        assert "ValueError: fail" in result.exc_string


@pytest.mark.integration()
@patch("backtick.dispatch.utils.discover_task", new=lambda _: task_retry)
def test_submit_scheduled_tasks_retry(mock_settings):
    with patch("backtick.dispatch.settings", mock_settings):
        dt = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
            seconds=5
        )
        response = dispatch.submit_tasks(
            schedule_request_dto=FakeScheduleRequestDTO(
                task_name="task1",
                datetimes=[dt],
                kwargs={},
            )
        )

        task_id = response.task_ids[0]
        task = rq.job.Job.fetch(task_id, utils.get_redis())

        assert task.id == task_id
        assert task.origin == "default"

        time.sleep(1)
        assert task.retries_left == 3
        assert task.retry_intervals == [1, 2, 3]
