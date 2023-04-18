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
    return dispatch.submit_tasks(schedule_request_dto=item)


@app.post("/unschedule")
def unschedule(item: dto.UnscheduleRequestDTO) -> dto.UnscheduleResponseDTO:
    """Unschedule a task."""
    return dispatch.cancel_tasks(unschedule_request_dto=item)
