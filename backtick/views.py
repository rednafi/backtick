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
    """Schedule a task."""
    task_id = dispatch.submit_task(schedule_dto=item)
    return dto.ScheduleResponseDTO(task_id=task_id, message="Scheduled")


@app.post("/unschedule")
def unschedule(
    request: Request, item: dto.UnscheduleRequestDTO
) -> dto.UnscheduleResponseDTO:
    """Unschedule a task."""

    try:
        dispatch.cancel_task(task_id=item.task_id)
    except ValueError as exc:
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content={
                "type": request.url.path,
                "title": "Bad Request",
                "detail": str(exc),
            },
        )
    return dto.UnscheduleResponseDTO(task_id=item.task_id, message="Unscheduled")
