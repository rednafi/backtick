"""Start the worker process."""


# Preload libraries
import argparse
import logging

from rq import Worker

from backtick import settings, utils


def main() -> None:
    """Run the worker."""
    parser = argparse.ArgumentParser()

    # Accept a flag to run the scheduler as well.
    parser.add_argument(
        "--with-scheduler", action="store_true", help="Run the scheduler as well."
    )
    # Accept a list of queues to listen to.
    parser.add_argument(
        "--queue-names", type=str, nargs="+", help="The name of the queue to listen to."
    )

    args = parser.parse_args()
    with_scheduler = args.with_scheduler
    queue_names = args.queue_names

    w = Worker(
        queues=queue_names if queue_names else settings.BACKTICK_QUEUES.values(),
        connection=utils.get_redis(),
    )
    logging.info("Starting worker, scheduler: %s", with_scheduler)
    w.work(with_scheduler=with_scheduler)


if __name__ == "__main__":
    main()
