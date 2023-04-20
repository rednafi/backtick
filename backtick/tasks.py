"""Example tasks for backtick."""

import logging
import time

from rq import Retry

from . import settings, utils


@utils.task(
    queue=settings.BACKTICK_QUEUES["default"],
    connection=utils.get_redis(),
    timeout=60,
    result_ttl=60,
)
def do_something(*, how_long: int) -> None:
    """Do something for a while.

    Args:
        how_long (int): How long to do something for.

    Returns:
        None
    """
    logging.info("Starting to do something")
    time.sleep(how_long)
    logging.info("Finished doing something")


@utils.task(
    queue=settings.BACKTICK_QUEUES["default"],
    connection=utils.get_redis(),
    retry=Retry(max=3, interval=2),
    timeout=60,
    result_ttl=60,
)
def raise_exception() -> None:
    """Raise an exception.

    Args:
        schedule_dto (dto.ScheduleRequestDTO): The schedule dto.

    Returns:
        None
    """
    raise ValueError("This is an exception")
