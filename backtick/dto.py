import datetime
from typing import Any

from pydantic import BaseModel, root_validator, validator

from . import settings, utils


class ScheduleRequestDTO(BaseModel):
    """The schedule request dto."""

    task_name: str
    datetimes: list[datetime.datetime] | None = None
    kwargs: dict[str, Any] = {}

    @root_validator()
    def check(cls, values: dict[str, Any]) -> dict[str, Any]:
        # Check if task is registered
        if (task_name := values.get("task_name")) not in settings.BACKTICK_TASKS:
            raise ValueError(f"Task {task_name} is not registered")

        # Check if task is discoverable
        try:
            task = utils.discover_task(settings.BACKTICK_TASKS[task_name])
        except (ImportError, AttributeError, ValueError):
            raise ValueError(f"Registered task {task_name} is not discoverable")

        # Check task is keyword only
        if not utils.check_keyword_only_func(task):
            raise ValueError(f"Task {task_name} is not keyword only")

        # Check if kwargs match the task kwargs
        if not utils.check_func_kwargs_match_kwargs(task, values.get("kwargs", {})):
            raise ValueError("Kwargs do not match task kwargs")

        return values

    @validator("datetimes", each_item=True)
    def check_datetimes(cls, v: datetime.datetime) -> datetime.datetime:
        if not v:
            return v

        if v < datetime.datetime.now(tz=datetime.timezone.utc):
            raise ValueError(f"Datetime {v} is in the past")

        # Check if datetimes are not more than a month in the future
        if v > datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
            days=30
        ):
            raise ValueError(f"Datetime {v} is more than a month in the future")

        # Check if datetimes are utc
        if v.tzinfo != datetime.timezone.utc:
            raise ValueError(
                "Datetime must be in UTC YYYY-MM-DDTHH:MM:SS+00:00 / YYYY-MM-DDTHH:MM:SSZ format"
            )
        return v


class ScheduleResponseDTO(BaseModel):
    task_ids: list[str]
    message: str


class UnscheduleRequestDTO(BaseModel):
    task_ids: list[str]
    enqueue_dependents: bool


UnscheduleResponseDTO = ScheduleResponseDTO
