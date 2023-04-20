import importlib
import inspect
from collections.abc import Callable
from typing import Any

import redis
from rq.defaults import DEFAULT_RESULT_TTL
from rq.job import Retry
from rq.queue import Queue
from rq.utils import backend_class

from . import settings

_cache = {}


def check_keyword_only_func(func: Callable) -> bool:
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


def check_func_kwargs_match_kwargs(func: Callable, kwargs: dict[str, Any]) -> bool:
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
    """Get a redis connection.

    Returns:
        redis.Redis: A redis connection
    """

    if "r" not in _cache:
        _cache["r"] = redis.Redis.from_url(settings.BACKTICK_REDIS_URL)
    return _cache["r"]


def discover_task(qualname: str) -> Callable[..., Any]:
    """
    Finds a function decorated with the @task decorator with the given fully-qualified
    name (e.g., 'my_module.my_function') and returns it. If no such function exists or
    there is an import error, raises an appropriate exception.
    """
    parts = qualname.split(".")
    mod_name = ".".join(parts[:-1])
    func_name = parts[-1]

    if not mod_name or not func_name:
        raise ValueError(
            f"Invalid fully qualified name: {qualname}. Must be of the form 'module.function'"
        )

    try:
        module = importlib.import_module(mod_name)
    except ModuleNotFoundError as e:
        raise ImportError(f"Failed to import module {mod_name}: {e}") from e

    if not (func := getattr(module, func_name, None)):
        raise ValueError(
            f"Callable {func_name} not found in module {mod_name}"
        ) from None

    if not (inspect.isfunction(func) or hasattr(func, "__call__")):
        raise TypeError(f"Object {func_name} is not a callable")

    if not getattr(func, "_is_task", None):
        raise ValueError(
            f"Callable {func_name} is not decorated with the @task decorator"
        )

    return func


class task:  # noqa
    queue_class = Queue

    def __init__(
        self,
        queue: Queue | str,
        connection: redis.Redis | None = None,
        timeout: int | None = None,
        result_ttl: int = DEFAULT_RESULT_TTL,
        ttl: int | None = None,
        queue_class: type[Queue] | None = None,
        depends_on: list[Any] | None = None,
        at_front: bool | None = None,
        meta: dict[Any, Any] | None = None,
        description: str | None = None,
        failure_ttl: int | None = None,
        retry: Retry | None = None,
        on_failure: Callable[..., Any] | None = None,
        on_success: Callable[..., Any] | None = None,
    ):
        self.queue = queue
        self.queue_class = backend_class(self, "queue_class", override=queue_class)
        self.connection = connection
        self.timeout = timeout
        self.result_ttl = result_ttl
        self.ttl = ttl
        self.meta = meta
        self.depends_on = depends_on
        self.at_front = at_front
        self.description = description
        self.failure_ttl = failure_ttl
        self.retry = retry
        self.on_success = on_success
        self.on_failure = on_failure

    def __call__(self, f: Callable[..., Any]) -> Callable[..., Any]:
        f.queue = self.queue  # type: ignore
        f.connection = self.connection  # type: ignore
        f.timeout = self.timeout  # type: ignore
        f.result_ttl = self.result_ttl  # type: ignore
        f.ttl = self.ttl  # type: ignore
        f.meta = self.meta  # type: ignore
        f.depends_on = self.depends_on  # type: ignore
        f.at_front = self.at_front  # type: ignore
        f.description = self.description  # type: ignore
        f.failure_ttl = self.failure_ttl  # type: ignore
        f.retry = self.retry  # type: ignore
        f.on_success = self.on_success  # type: ignore
        f.on_failure = self.on_failure  # type: ignore
        f.queue_class = self.queue_class  # type: ignore
        f._is_task = True  # type: ignore

        return f
