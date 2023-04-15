import datetime
import re
from unittest.mock import patch
from urllib.parse import quote

import pytest

from backtick import dto


class TestScheduleRequestDTO:
    VALID_TASK_NAME = "task1"
    DOES_NOT_EXIST_TASK_NAME = "does_not_exist_task"
    VALID_QUEUE_NAME = "default"
    DOES_NOT_EXIST_QUEUE_NAME = "does_not_exist_queue"

    VALID_DATETIME = datetime.datetime(1970, 1, 1, 0, 0, 0)
    VALID_CRON = "0 12 * * *"
    VALID_KWARGS = {"foo": "hello", "bar": "world"}

    INVALID_TASK_NAME = "invalid&task"
    INVALID_QUEUE_NAME = "invalid queue"
    INVALID_DATETIME = "not a datetime"
    INVALID_CRON = "invalid cron expression"
    INVALID_KWARGS = {"invalid_kwarg": True}

    def test_check_task_name_valid(self, mock_settings):
        with patch("backtick.dto.settings", mock_settings):
            request = dto.ScheduleRequestDTO(task_name=self.VALID_TASK_NAME)
            assert request.task_name == quote(self.VALID_TASK_NAME, safe="%")

    def test_check_task_name_invalid_characters(self):
        with pytest.raises(ValueError, match="Task name contains unsafe characters"):
            dto.ScheduleRequestDTO(task_name=self.INVALID_TASK_NAME)

    def test_check_task_name_not_registered(self, mock_settings):
        with patch("backtick.dto.settings", mock_settings):
            with pytest.raises(
                ValueError, match="Task does_not_exist_task is not registered"
            ):
                dto.ScheduleRequestDTO(task_name=self.DOES_NOT_EXIST_TASK_NAME)

    def test_check_queue_name_valid(self, mock_settings):
        with patch("backtick.dto.settings", mock_settings):
            request = dto.ScheduleRequestDTO(
                task_name=self.VALID_TASK_NAME, queue_name=self.VALID_QUEUE_NAME
            )
            assert request.queue_name == quote(self.VALID_QUEUE_NAME, safe="%")

    def test_check_queue_name_invalid_characters(self, mock_settings):
        with patch("backtick.dto.settings", mock_settings):
            with pytest.raises(
                ValueError, match=re.escape("Queue name contains URL-unsafe characters")
            ):
                dto.ScheduleRequestDTO(
                    task_name=self.VALID_TASK_NAME, queue_name=self.INVALID_QUEUE_NAME
                )

    def test_check_queue_name_not_registered(self, mock_settings):
        with patch("backtick.dto.settings", mock_settings):
            with pytest.raises(
                ValueError, match="Queue does_not_exist_queue is not registered"
            ):
                dto.ScheduleRequestDTO(
                    task_name=self.VALID_TASK_NAME,
                    queue_name=self.DOES_NOT_EXIST_QUEUE_NAME,
                )

    def test_check_when_and_cron_valid(self, mock_settings):
        with patch("backtick.dto.settings", mock_settings):
            request = dto.ScheduleRequestDTO(
                task_name=self.VALID_TASK_NAME, when=self.VALID_DATETIME
            )
            assert request.when == self.VALID_DATETIME

            request = dto.ScheduleRequestDTO(
                task_name=self.VALID_TASK_NAME, cron=self.VALID_CRON
            )
            assert request.cron == self.VALID_CRON

    def test_check_when_and_cron_both_specified(self, mock_settings):
        with patch("backtick.dto.settings", mock_settings):
            with pytest.raises(ValueError, match="Cannot set both when and cron"):
                dto.ScheduleRequestDTO(
                    task_name=self.VALID_TASK_NAME,
                    when=self.VALID_DATETIME,
                    cron=self.VALID_CRON,
                )

    def test_check_kwargs_match_task_kwargs_valid(self, mock_settings):
        with patch("backtick.dto.settings", mock_settings):
            request = dto.ScheduleRequestDTO(
                task_name="task1", kwargs=self.VALID_KWARGS
            )
            assert request.kwargs == self.VALID_KWARGS

        with patch("backtick.dto.settings", mock_settings):
            with pytest.raises(ValueError, match="Task task2 is not keyword only"):
                dto.ScheduleRequestDTO(task_name="task2", kwargs=self.VALID_KWARGS)

    def test_check_kwargs_match_task_kwargs_invalid_kwargs(self, mock_settings):
        with patch("backtick.dto.settings", mock_settings):
            with pytest.raises(ValueError, match="Kwargs do not match task1 kwargs"):
                dto.ScheduleRequestDTO(task_name="task1", kwargs=self.INVALID_KWARGS)


class TestScheduleResponseDTO:
    def test_task_id(self):
        response = dto.ScheduleResponseDTO(
            task_id="task_id", message="message", next_run=None
        )
        assert response.task_id == "task_id"

    def test_message(self):
        response = dto.ScheduleResponseDTO(task_id="task_id", message="message")
        assert response.message == "message"

    def test_next_run(self):
        next_run = datetime.datetime(1970, 1, 1, 0, 0, 0)
        response = dto.ScheduleResponseDTO(
            task_id="task_id", message="message", next_run=next_run
        )
        assert response.next_run == next_run


class TestUnscheduleRequestDTO:
    def test_task_id(self):
        request = dto.UnscheduleRequestDTO(task_id="task_id")
        assert request.task_id == "task_id"
