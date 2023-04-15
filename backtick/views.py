"""The api endpoints live here."""

from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from . import dispatch, dto

app = FastAPI()


@app.exception_handler(Exception)
def exception_handler(request, exc):
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
    task_id = dispatch.dispatch_task(schedule_dto=item)
    return dto.ScheduleResponseDTO(task_id=task_id, message="Scheduled")


@app.post("/unschedule")
def unschedule(item: dto.UnscheduleRequestDTO) -> dto.UnscheduleResponseDTO:
    """Unschedule a task."""
    return dto.UnscheduleResponseDTO(task_id="123", message="Unscheduled")
