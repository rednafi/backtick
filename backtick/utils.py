import inspect
from collections.abc import Callable
from typing import Any

import redis

from . import settings

Func = Callable[..., Any]
__cache = {}


def check_keyword_only_func(func: Func) -> bool:
    """Check that a function is keyword only

    Args:
        func (Func): A task function

    Returns:
        bool: True if the function is keyword only, False otherwise
    """

    sig = inspect.signature(func)
    return all(
        param.kind == inspect.Parameter.KEYWORD_ONLY
        for param in sig.parameters.values()
    )


def check_func_kwargs_match_kwargs(func: Func, kwargs: dict[str, Any]) -> bool:
    """Check that the kwargs match the function kwargs.

    Args:
        func (Func): A task function
        kwargs (dict[str, Any]): The kwargs to check

    Returns:
        bool: True if the kwargs match the function kwargs, False otherwise
    """
    sig = inspect.signature(func)
    func_params = sig.parameters

    for param_name in kwargs:
        if param_name not in func_params:
            return False

    for param_name, param in func_params.items():
        if param_name not in kwargs and param.default is inspect.Parameter.empty:
            return False

    return True


def get_redis() -> redis.Redis:
    """Get the redis connection.

    Returns:
        redis.Redis: The redis connection
    """
    if "r" not in __cache:
        __cache["r"] = redis.Redis.from_url(settings.BACKTICK_REDIS_URL)
    return __cache["r"]
