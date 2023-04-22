import logging
from typing import cast

import rq
import rq.exceptions

from backtick import dto, settings, utils


def submit_tasks(
    *, schedule_request_dto: dto.ScheduleRequestDTO
) -> dto.ScheduleResponseDTO:
    """Schedule tasks on a worker.

    Args:
        schedule_dto (dto.ScheduleRequestDTO): The schedule request dto.

    Returns:
        dto.ScheduleResponseDTO: The schedule response dto.
    """

    # Incoming dto names
    task_name = schedule_request_dto.task_name
    datetimes = schedule_request_dto.datetimes
    kwargs = schedule_request_dto.kwargs

    task = cast(rq.job.Job, utils.discover_task(settings.BACKTICK_TASKS[task_name]))

    queue_name = task.queue
    connection = task.connection
    timeout = task.timeout
    result_ttl = task.result_ttl
    ttl = task.ttl
    queue_class = task.queue_class
    depends_on = task.depends_on
    at_front = task.at_front
    meta = task.meta
    description = task.description
    failure_ttl = task.failure_ttl
    retry = task.retry
    on_failure = task.on_failure
    on_success = task.on_success

    queue = queue_class(name=queue_name, connection=connection)
    if datetimes:
        job_ids = []

        for dt in datetimes:
            job = queue.enqueue_at(
                dt,
                task,
                kwargs=kwargs,
                timeout=timeout,
                result_ttl=result_ttl,
                ttl=ttl,
                depends_on=depends_on,
                at_front=at_front,
                meta=meta,
                description=description,
                failure_ttl=failure_ttl,
                retry=retry,
                on_failure=on_failure,
                on_success=on_success,
            )
            logging.info("Task %s scheduled at %s", job.id, dt)
            job_ids.append(job.id)
    else:
        job = queue.enqueue(
            task,
            kwargs=kwargs,
            timeout=timeout,
            result_ttl=result_ttl,
            ttl=ttl,
            depends_on=depends_on,
            at_front=at_front,
            meta=meta,
            description=description,
            failure_ttl=failure_ttl,
            retry=retry,
            on_failure=on_failure,
            on_success=on_success,
        )
        logging.info("Task %s scheduled", job.id)
        job_ids = [job.id]

    return dto.ScheduleResponseDTO(
        task_ids=job_ids, message="Tasks scheduled successfully"
    )


def cancel_tasks(
    *, unschedule_request_dto: dto.UnscheduleRequestDTO
) -> dto.UnscheduleResponseDTO:
    """Cancel a task.

    Args:
        unschedule_dto (dto.UnscheduleRequestDTO): The unschedule request dto.

    Returns:
        dto.UnscheduleResponseDTO: The unschedule response dto.
    """

    # Cancel running jobs
    task_ids = unschedule_request_dto.task_ids

    jobs = rq.job.Job.fetch_many(task_ids, connection=utils.get_redis())
    task_ids = []

    for job in jobs:
        logging.info("Task %s", job.id)
        rq.cancel_job(
            job.id,
            connection=job.connection,
            serializer=job.serializer,
            enqueue_dependents=unschedule_request_dto.enqueue_dependents,
        )
        task_ids.append(job.id)

    return dto.UnscheduleResponseDTO(
        task_ids=task_ids, message="Tasks unscheduled successfully"
    )
