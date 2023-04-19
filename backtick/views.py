from http import HTTPStatus

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from . import dispatch, dto

app = FastAPI()


@app.exception_handler(Exception)
def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={
            "type": request.url.path,
            "title": "Internal Server Error",
            "detail": str(exc),
        },
    )


@app.post("/schedule")
def schedule(item: dto.ScheduleRequestDTO) -> dto.ScheduleResponseDTO:
    """Schedule a task.

    ### Request body

    * `task_name` - This field specifies the name of the task that you want to schedule.
    The task must be previously registered in the `BACKTICK_TASKS` variable of the
    `settings.py` module.

    * `datetimes` - This field accepts a list of datetimes to schedule the task at. All
    datetimes provided should be in `UTC` format and must be in the future. The format
    of the datetime string should be `YYYY-MM-DDTHH:MM:SS+00:00` or
    `YYYY-MM-DDTHH:MM:SSZ`. Additionally, the datetimes should not be more than a month
    in the future.

    * `kwargs` - This field specifies a dictionary of keyword arguments that will be
    passed to the task when it is executed.

    ### Response body
    * `task_ids` - This field contains a list of task ids that were scheduled.
    * `message` - This field contains a message that indicates the status of the
    scheduled tasks.

    """
    return dispatch.submit_tasks(schedule_request_dto=item)


@app.post("/unschedule")
def unschedule(item: dto.UnscheduleRequestDTO) -> dto.UnscheduleResponseDTO:
    """Unschedule a task.

    ### Request body

    * `task_ids` - This field accepts a list of task ids that you want to unschedule.
    * `enqueue_dependents` - This field specifies whether or not to cancel the dependent
    tasks of the tasks that are being unscheduled.

    ### Response body

    * `task_ids` - This field contains a list of task ids that were unscheduled.
    * `message` - This field contains a message that indicates the status of the
    unscheduled tasks.
    """
    return dispatch.cancel_tasks(unschedule_request_dto=item)
