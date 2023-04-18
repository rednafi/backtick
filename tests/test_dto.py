import datetime
import zoneinfo
from contextlib import ExitStack
from unittest.mock import patch

import pytest

from backtick import dto


class TestScheduleRequestDTO:
    """Test ScheduleRequestDTO."""

    def test_task_name_ok(self, mock_settings):
        """Test task_name."""

        stack = ExitStack()
        stack.enter_context(
            patch("backtick.dto.utils.discover_task", return_value=lambda: None)
        )
        stack.enter_context(patch("backtick.dto.settings", mock_settings))

        with stack:
            schedule_request_dto = dto.ScheduleRequestDTO(
                task_name="task1",
            )
            assert schedule_request_dto.task_name == "task1"

    def test_task_name_not_ok(self, mock_settings):
        """Test task_name."""

        stack = ExitStack()
        stack.enter_context(patch("backtick.dto.settings", mock_settings))

        with stack:
            # Raise ValueError for unknown task
            with pytest.raises(ValueError, match="Task task3 is not registered"):
                _ = dto.ScheduleRequestDTO(
                    task_name="task3",
                )

            # Raise ValueError for un-discoverable task
            with pytest.raises(
                ValueError, match="Registered task task2 is not discoverable"
            ):
                _ = dto.ScheduleRequestDTO(
                    task_name="task2",
                )

    def test_datetimes_ok(self, mock_settings):
        """Test datetimes."""

        stack = ExitStack()
        stack.enter_context(
            patch("backtick.dto.utils.discover_task", return_value=lambda: None)
        )
        stack.enter_context(patch("backtick.dto.settings", mock_settings))

        with stack:
            dt1 = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
                days=1
            )
            dt2 = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
                days=2
            )
            schedule_request_dto = dto.ScheduleRequestDTO(
                task_name="task1",
                datetimes=[dt1, dt2],
            )
            assert schedule_request_dto.datetimes == [dt1, dt2]

    def test_datetimes_not_ok(self, mock_settings):
        """Test datetimes."""

        stack = ExitStack()
        stack.enter_context(
            patch("backtick.dto.utils.discover_task", return_value=lambda: None)
        )
        stack.enter_context(patch("backtick.dto.settings", mock_settings))

        with stack:
            dt1 = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(
                days=1
            )

            # Raise ValueError for past datetime
            with pytest.raises(ValueError, match="Datetime .* is in the past"):
                _ = dto.ScheduleRequestDTO(
                    task_name="task1",
                    datetimes=[dt1],
                )

            # Raise ValueError for datetime more than a month in the future
            dt2 = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
                days=31
            )
            with pytest.raises(
                ValueError, match="Datetime .* is more than a month in the future"
            ):
                _ = dto.ScheduleRequestDTO(
                    task_name="task1",
                    datetimes=[dt2],
                )

            # Raise ValueError for datetime not in UTC
            tz = zoneinfo.ZoneInfo("Europe/Amsterdam")
            dt3 = datetime.datetime.now(tz=tz) + datetime.timedelta(days=1)
            with pytest.raises(ValueError, match="Datetime must be in UTC .* format"):
                _ = dto.ScheduleRequestDTO(
                    task_name="task1",
                    datetimes=[dt3],
                )

    def test_task_is_keyword_only(self, mock_settings):
        """Test kwargs."""

        stack = ExitStack()
        stack.enter_context(
            patch("backtick.dto.utils.discover_task", return_value=lambda a, b: None)
        )
        stack.enter_context(patch("backtick.dto.settings", mock_settings))

        with stack:
            # Test task is keyword-only
            with pytest.raises(ValueError, match="Task task1 is not keyword only"):
                _ = dto.ScheduleRequestDTO(
                    task_name="task1",
                    kwargs={"a": "foo", "b": "bar"},
                )

    def test_task_kwargs_match_incoming_kwargs(self, mock_settings):
        """Test kwargs."""

        stack = ExitStack()
        stack.enter_context(
            patch("backtick.dto.utils.discover_task", return_value=lambda a, b: None)
        )
        stack.enter_context(patch("backtick.dto.settings", mock_settings))

        with stack:
            # Test kwargs match incoming kwargs
            with pytest.raises(ValueError, match="Task task1 is not keyword only "):
                _ = dto.ScheduleRequestDTO(
                    task_name="task1",
                    kwargs={"a": "foo"},
                )


class TestScheduleResponseDTO:
    def test_required_fields(self, mock_settings):
        """Test required fields."""

        stack = ExitStack()
        stack.enter_context(patch("backtick.dto.settings", mock_settings))

        with stack:
            with pytest.raises(ValueError, match="field required"):
                _ = dto.ScheduleResponseDTO(
                    message="message",
                )

            with pytest.raises(ValueError, match="field required"):
                _ = dto.ScheduleResponseDTO(
                    task_ids=["task1", "task2"],
                )

    def test_task_ids(self, mock_settings):
        """Test task_ids."""

        stack = ExitStack()
        stack.enter_context(patch("backtick.dto.settings", mock_settings))

        with stack:
            schedule_response_dto = dto.ScheduleResponseDTO(
                task_ids=["task1", "task2"],
                message="message",
            )
            assert schedule_response_dto.task_ids == ["task1", "task2"]

    def test_message(self, mock_settings):
        """Test message."""

        stack = ExitStack()
        stack.enter_context(patch("backtick.dto.settings", mock_settings))

        with stack:
            schedule_response_dto = dto.ScheduleResponseDTO(
                task_ids=["task1", "task2"],
                message="message",
            )
            assert schedule_response_dto.message == "message"


class TestUnscheduleRequestDTO:
    def test_required_fields(self, mock_settings):
        """Test required fields."""

        stack = ExitStack()
        stack.enter_context(patch("backtick.dto.settings", mock_settings))

        with stack:
            with pytest.raises(ValueError, match="field required"):
                _ = dto.UnscheduleRequestDTO(
                    task_ids=["task1", "task2"],
                )

            with pytest.raises(ValueError, match="field required"):
                _ = dto.UnscheduleRequestDTO(
                    enqueue_dependents=True,
                )

    def test_task_ids(self, mock_settings):
        """Test task_ids."""

        stack = ExitStack()
        stack.enter_context(patch("backtick.dto.settings", mock_settings))

        with stack:
            unschedule_request_dto = dto.UnscheduleRequestDTO(
                task_ids=["task1", "task2"],
                enqueue_dependents=True,
            )
            assert unschedule_request_dto.task_ids == ["task1", "task2"]

    def test_enqueue_dependents(self, mock_settings):
        """Test message."""

        stack = ExitStack()
        stack.enter_context(patch("backtick.dto.settings", mock_settings))

        with stack:
            unschedule_request_dto = dto.UnscheduleRequestDTO(
                task_ids=["task1", "task2"],
                enqueue_dependents=True,
            )
            assert unschedule_request_dto.enqueue_dependents is True


TestUnscheduleResponseDTO = TestScheduleResponseDTO
