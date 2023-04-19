"""Cancel all the tasks."""

import argparse
import logging

import rq
from rq.command import send_kill_horse_command
from rq.registry import ScheduledJobRegistry
from rq.worker import Worker, WorkerStatus

from backtick import utils


def cancel_running_tasks() -> None:
    """Cancel running jobs."""

    connection = utils.get_redis()

    workers = Worker.all(connection)
    for worker in workers:
        if worker.state == WorkerStatus.BUSY:
            send_kill_horse_command(connection, worker.name)


def cancel_scheduled_tasks() -> None:
    """Cancel scheduled jobs."""

    connection = utils.get_redis()
    queue = rq.Queue(connection=connection)

    registry = ScheduledJobRegistry(queue=queue)

    # This is how to remove a job from a registry
    for job_id in registry.get_job_ids():
        logging.info("Removing scheduled job %s", job_id)
        registry.remove(job_id, delete_job=True)


def cancel_all_tasks() -> None:
    """Cancel all jobs."""

    cancel_running_tasks()
    cancel_scheduled_tasks()


def main() -> None:
    """Run the script."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Cancel all tasks.")
    parser.add_argument("--running", action="store_true", help="Cancel running tasks.")
    parser.add_argument(
        "--scheduled", action="store_true", help="Cancel scheduled tasks."
    )

    args = parser.parse_args()
    is_all = args.all
    is_running = args.running
    is_scheduled = args.scheduled

    if is_all:
        cancel_all_tasks()

    elif is_running:
        cancel_running_tasks()

    elif is_scheduled:
        cancel_scheduled_tasks()

    else:
        parser.error("Invalid flag.")


if __name__ == "__main__":
    main()
