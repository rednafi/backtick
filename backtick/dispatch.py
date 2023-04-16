import logging

import rq
import rq_scheduler

from . import dto, settings, utils


def submit_task(*, schedule_dto: dto.ScheduleRequestDTO) -> str:
    """Schedule a task on a worker.

    Args:
        task (function): The task to schedule.
        schedule_dto (dto.ScheduleRequestDTO): The schedule dto.

    Returns:
        str: The task id.
    """

    # Incoming dto names
    task_name_dto = schedule_dto.task_name
    queue_name_dto = schedule_dto.queue_name
    when_dto = schedule_dto.when
    cron_dto = schedule_dto.cron
    kwargs_dto = schedule_dto.kwargs

    task = settings.BACKTICK_TASKS[task_name_dto]
    queue_name = (
        settings.BACKTICK_QUEUES[queue_name_dto]
        if queue_name_dto
        else settings.BACKTICK_QUEUES["default"]
    )
    when = when_dto
    cron = cron_dto

    queue = rq.Queue(queue_name, connection=utils.get_redis())

    if not (when or cron):
        # Enqueue the job to be run immediately
        job = queue.enqueue(task, **kwargs_dto)

    elif when and not cron:
        # If 'when' is provided but not 'cron', schedule the job to run at 'when'
        scheduler = rq_scheduler.Scheduler(queue=queue, connection=utils.get_redis())
        job = scheduler.enqueue_at(when, task, **kwargs_dto)

    elif cron:
        # If both 'when' and 'cron' are provided, schedule the job to run using 'cron' schedule
        scheduler = rq_scheduler.Scheduler(queue=queue, connection=utils.get_redis())

        # fmt: off
        job = scheduler.cron(
            # A cron string (e.g. "0 0 * * 0")
            cron.cron_str,

            # The function to be queued
            func=task,

            # Keyword arguments passed into function when executed
            kwargs=kwargs_dto,

            # Repeat this number of times (None means repeat forever)
            repeat=cron.repeat or None,

            # Specify how long (in seconds) successful jobs and their results are kept.
            # Defaults to -1 (forever)
            result_ttl=cron.result_ttl or -1,

            # Specifies the maximum queued time (in seconds) before it's discarded.
            # Defaults to None (infinite TTL).
            ttl=cron.ttl or None,

            # Interpret hours in the local timezone
            use_local_timezone=False,
        )
        # fmt: on

    else:
        # When and cron are mutually exclusive. So this should never happen
        pass

    return job.id


def cancel_task(task_id: str) -> None:
    """Cancel a task.

    Args:
        task_id (str): The task id.
        queue_name (str): The queue name.
    """
    logging.info("Cancelling task %s", task_id)

    # Cancel running jobs

    try:
        job = rq.job.Job.fetch(task_id, connection=utils.get_redis())
    except rq.exceptions.NoSuchJobError:
        raise ValueError(f"Task {task_id} not found")

    # Cancel running jobs
    job.cancel()

    # Cancel scheduled jobs
    queue_name = settings.BACKTICK_QUEUES["default"]
    queue = rq.Queue(queue_name, connection=utils.get_redis())
    scheduler = rq_scheduler.Scheduler(queue=queue, connection=utils.get_redis())
    scheduler.cancel(job)
