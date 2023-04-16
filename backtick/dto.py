import datetime
from typing import Any, Literal
from urllib.parse import quote

from pydantic import BaseModel, root_validator, validator

from . import settings, utils


class CronDTO(BaseModel):
    cron_str: str
    repeat: int | None = None
    result_ttl: int | None = None
    ttl: int | None = None


class ScheduleRequestDTO(BaseModel):
    task_name: str
    queue_name: str | None = None
    when: datetime.datetime | Literal[""] | None = None
    cron: CronDTO | Literal[""] | None = None
    kwargs: dict[str, Any] = {}

    @validator("task_name")
    def check_task_name(cls, value: str) -> str:
        # Disallow empty task names
        if not value:
            raise ValueError("Task name cannot be empty")

        # Check that value doesn't contain any URL unsafe special characters
        if (sanitized_value := quote(value, safe="%")) != value:
            raise ValueError("Task name contains unsafe characters")

        # Check that value is a registered task
        if sanitized_value not in settings.BACKTICK_TASKS:
            raise ValueError(f"Task {value} is not registered")
        return sanitized_value

    @validator("queue_name")
    def check_queue_name(cls, value: str | None) -> str | None:
        # If queue_name is not set, use the default queue
        if not value:
            return value

        # Check that value doesn't contain any URL unsafe special characters
        if (sanitized_value := quote(value, safe="%")) != value:
            raise ValueError("Queue name contains URL-unsafe characters")

        # Check that value is a registered queue
        if sanitized_value not in settings.BACKTICK_QUEUES:
            raise ValueError(f"Queue {value} is not registered")
        return sanitized_value

    @root_validator(pre=True)
    def check_both_when_and_cron(cls, values: dict[str, Any]) -> dict[str, Any]:
        # Check that when and cron are not both set
        if values.get("when") and values.get("cron"):
            raise ValueError("Cannot set both when and cron")
        return values

    @validator("when")
    def check_when(
        cls, value: datetime.datetime | Literal[""] | None
    ) -> datetime.datetime | Literal[""] | None:
        # If when is not set, schedule immediately
        if not value:
            return value

        # Check when is a valid with UTC timezone
        if value.tzinfo != datetime.timezone.utc:
            raise ValueError(
                "When must be a UTC datetime in the format YYYY-MM-DDTHH:MM:SS+00:00"
            )
        return value

    @validator("cron")
    def check_cron(cls, value: CronDTO | None) -> CronDTO | None:
        # If cron is not set, do nothing
        if not value:
            return value

        # Check that cron is a valid cron expression
        if not utils.check_cron(value.cron_str):
            raise ValueError("Cron must be a valid cron expression")
        return value

    @validator("kwargs")
    def check_kwargs_match_task_kwargs(
        cls, value: dict[str, Any], values: dict[str, Any]
    ) -> dict[str, Any]:
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


class UnscheduleRequestDTO(BaseModel):
    task_id: str


UnscheduleResponseDTO = ScheduleResponseDTO
