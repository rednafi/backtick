import datetime
from typing import Any, Literal
from urllib.parse import quote

from pydantic import BaseModel, root_validator, validator

from . import settings, utils


class ScheduleRequestDTO(BaseModel):
    task_name: str
    queue_name: str = settings.BACKTICK_QUEUES["default"]
    when: datetime.datetime | Literal[""] | None = None
    cron: str | None = None
    kwargs: dict[str, Any] = {}

    @validator("task_name")
    def check_task_name(cls, value):
        # Check that value doesn't contain any URL unsafe special characters
        if (sanitized_value := quote(value, safe="%")) != value:
            raise ValueError("Task name contains unsafe characters")

        if sanitized_value not in settings.BACKTICK_TASKS:
            raise ValueError(f"Task {value} is not registered")
        return sanitized_value

    @validator("queue_name")
    def check_queue_name(cls, value):
        # Check that value doesn't contain any URL unsafe special characters
        if (sanitized_value := quote(value, safe="%")) != value:
            raise ValueError("Queue name contains URL-unsafe characters")

        if sanitized_value not in settings.BACKTICK_QUEUES:
            raise ValueError(f"Queue {value} is not registered")
        return sanitized_value

    @root_validator()
    def check_when_and_cron(cls, values):
        # Check that when and cron are not both set
        if values.get("when") and values.get("cron"):
            raise ValueError("Cannot set both when and cron")
        return values

    @validator("kwargs")
    def check_kwargs_match_task_kwargs(cls, value, values):
        # Check that kwargs match the task kwargs
        task = settings.BACKTICK_TASKS[values["task_name"]]

        if not utils.check_keyword_only_func(task):
            raise ValueError(f"Task {values['task_name']} is not keyword only")

        if not utils.check_func_kwargs_match_kwargs(task, value):
            raise ValueError(f"Kwargs do not match {values['task_name']} kwargs")
        return value


class ScheduleResponseDTO(BaseModel):
    task_id: str
    message: str
    next_run: datetime.datetime | None = None


class UnscheduleRequestDTO(BaseModel):
    task_id: str


UnscheduleResponseDTO = ScheduleResponseDTO
