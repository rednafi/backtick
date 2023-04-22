"""Example tasks for backtick."""

import logging
import time
from typing import Any

import httpx
from rq import Retry

from backtick import settings, utils


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
    """Raise an exception. The task will be retried 3 times with a 2 second interval.

    Args:
        None

    Returns:
        None
    """
    raise ValueError("This is an exception")


interval_with_backoff = [2**i for i in range(3)]


def on_success_callback(*args: Any, **kwargs: Any) -> None:
    """Callback for when a task succeeds.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        None
    """
    logging.info("From on_success callback!")


def on_failure_callback(*args: Any, **kwargs: Any) -> None:
    """Callback for when a task fails.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        None
    """
    logging.error("From on_failure callback!")


@utils.task(
    queue=settings.BACKTICK_QUEUES["default"],
    connection=utils.get_redis(),
    retry=Retry(max=len(interval_with_backoff), interval=interval_with_backoff),
    timeout=60,
    result_ttl=60,
    on_success=on_success_callback,
    on_failure=on_failure_callback,
)
def raise_exception_again() -> None:
    """Raise an exception. The task will be retried with exponential backoff.

    Args:
        None

    Returns:
        None
    """
    raise ValueError("This is an exception")


@utils.task(
    queue=settings.BACKTICK_QUEUES["default"],
    connection=utils.get_redis(),
    retry=Retry(max=3, interval=2),
    timeout=60,
    result_ttl=60,
)
def make_request(*, url: str, data: dict[str, Any] | None = None) -> None:
    """Make a request.

    Args:
        url (str): The URL to make a request to.
        data (dict[str, Any], optional): The data to send with the request.
        Defaults to None.

    Returns:
        None
    """
    with httpx.Client() as client:
        response = client.post(url, json=data)
        response.raise_for_status()
        logging.info("Making request to %s", url)
        logging.info("Response status code: %s", response.status_code)
        logging.info("Response text: %s", response.text)
