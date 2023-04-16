"""The background tasks live here."""

import logging
import time


def do_something(*, how_long: int) -> None:
    """Do something for a while.

    Args:
        schedule_dto (dto.ScheduleRequestDTO): The schedule dto.

    Returns:
        None
    """
    logging.info("Starting to do something")
    time.sleep(how_long)
    logging.info("Finished doing something")
