"""Start the worker process."""

# Preload libraries
import argparse
import logging

from rq import Worker

from . import settings, utils


def main() -> None:
    """Run the worker."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--with-scheduler", action="store_true", help="Run the scheduler as well."
    )
    # Accept a list of queues to listen to.
    parser.add_argument(
        "--queue-name", type=str, nargs="+", help="The name of the queue to listen to."
    )

    args = parser.parse_args()
    with_scheduler = args.with_scheduler

    # Provide the worker with the list of queues (str) to listen to.
    w = Worker(
        queues=settings.BACKTICK_QUEUES.values(),
        connection=utils.get_redis(),
    )

    logging.info("Starting worker, scheduler: %s", with_scheduler)
    w.work(with_scheduler=with_scheduler)


if __name__ == "__main__":
    main()
