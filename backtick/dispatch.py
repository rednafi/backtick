import logging
import rq
import rq_scheduler

from . import dto, settings, utils


def dispatch_task(*, schedule_dto: dto.ScheduleRequestDTO) -> str:
    """Schedule a task on a worker.

    Args:
        task (function): The task to schedule.
        schedule_dto (dto.ScheduleRequestDTO): The schedule dto.

    Returns:
        str: The task id.
    """

    queue_name = settings.BACKTICK_QUEUES[schedule_dto.queue_name]
    task = settings.BACKTICK_TASKS[schedule_dto.task_name]
    when = schedule_dto.when
    logging.info("Scheduling task %s in queue %s at %s", task, queue_name, when.tzinfo)
    queue = rq.Queue(queue_name, connection=utils.get_redis())
    scheduler = rq_scheduler.Scheduler(queue=queue, connection=utils.get_redis())
    job= scheduler.enqueue_at(when, task, **schedule_dto.kwargs)

    return job.id
