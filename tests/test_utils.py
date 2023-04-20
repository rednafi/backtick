import pytest
import redis
import rq

from backtick import utils

##########################################
# Test check_keyword_only_func
##########################################


def test_check_keyword_only_func_with_keyword_only_params():
    def my_func(*, a: int, b: str, c: float):
        pass

    assert utils.check_keyword_only_func(my_func) is True


def test_check_keyword_only_func_with_positional_params():
    def my_func(a: int, b: str, c: float):
        pass

    assert utils.check_keyword_only_func(my_func) is False


def test_check_keyword_only_func_with_mixed_params():
    def my_func(a: int, b: str, *, c: float):
        pass

    assert utils.check_keyword_only_func(my_func) is False


def test_check_keyword_only_func_with_no_params():
    def my_func():
        pass

    assert utils.check_keyword_only_func(my_func) is True


def test_check_keyword_only_func_with_callable_object():
    class MyClass:
        def __call__(self, *, a: int, b: str):
            pass

    my_obj = MyClass()
    assert utils.check_keyword_only_func(my_obj) is True


def test_check_keyword_only_func_with_invalid_input():
    with pytest.raises(TypeError):
        utils.check_keyword_only_func(None)


##########################################
# Test check_kwargs_match_func
##########################################


def test_check_func_kwargs_match_kwargs_with_matching_kwargs():
    def my_func(a: int, b: str, c: float = 0.0):
        pass

    kwargs = {"a": 1, "b": "hello"}
    assert utils.check_func_kwargs_match_kwargs(my_func, kwargs) is True


def test_check_func_kwargs_match_kwargs_with_missing_required_kwargs():
    def my_func(a: int, b: str, c: float):
        pass

    kwargs = {"a": 1}
    assert utils.check_func_kwargs_match_kwargs(my_func, kwargs) is False


def test_check_func_kwargs_match_kwargs_with_extra_kwargs():
    def my_func(a: int, b: str, c: float = 0.0):
        pass

    kwargs = {"a": 1, "b": "hello", "d": True}
    assert utils.check_func_kwargs_match_kwargs(my_func, kwargs) is False


def test_check_func_kwargs_match_kwargs_with_default_kwargs():
    def my_func(a: int, b: str, c: float = 0.0):
        pass

    kwargs = {"a": 1, "b": "hello", "c": 3.14}
    assert utils.check_func_kwargs_match_kwargs(my_func, kwargs) is True


def test_check_func_kwargs_match_kwargs_with_invalid_input():
    with pytest.raises(TypeError):
        utils.check_func_kwargs_match_kwargs(None, {})


def test_check_func_kwargs_match_kwargs_with_any_kwargs():
    def my_func(*args, **kwargs):
        pass

    kwargs = {"a": 1, "b": "hello"}
    assert utils.check_func_kwargs_match_kwargs(my_func, kwargs) is False


def test_check_func_kwargs_match_kwargs_with_no_kwargs():
    def my_func():
        pass

    kwargs = {}
    assert utils.check_func_kwargs_match_kwargs(my_func, kwargs) is True


##########################################
# Test get_redis
##########################################


def test_get_redis():
    redis_conn_1 = utils.get_redis()
    assert utils._cache["r"] == redis_conn_1


##########################################
# Test task decorator
##########################################


def test_task():
    # Arrange
    expected_queue = "my_queue"
    expected_connection = redis.Redis()
    expected_timeout = 60
    expected_result_ttl = 300
    expected_ttl = 3600
    expected_meta = {"key": "value"}
    expected_depends_on = [1, 2, 3]
    expected_at_front = True
    expected_description = "My task"
    expected_failure_ttl = 600
    expected_retry = rq.Retry(max=3, interval=10)

    def expected_on_success(x):
        return print("Success!")

    def expected_on_failure(x):
        return print("Failure!")

    # Act
    @utils.task(
        queue=expected_queue,
        connection=expected_connection,
        timeout=expected_timeout,
        result_ttl=expected_result_ttl,
        ttl=expected_ttl,
        meta=expected_meta,
        depends_on=expected_depends_on,
        at_front=expected_at_front,
        description=expected_description,
        failure_ttl=expected_failure_ttl,
        retry=expected_retry,
        on_success=expected_on_success,
        on_failure=expected_on_failure,
    )
    def foo_task(*, x):
        return x * 2

    # Assert
    assert foo_task.queue == expected_queue
    assert foo_task.connection == expected_connection
    assert foo_task.timeout == expected_timeout
    assert foo_task.result_ttl == expected_result_ttl
    assert foo_task.ttl == expected_ttl
    assert foo_task.meta == expected_meta
    assert foo_task.depends_on == expected_depends_on
    assert foo_task.at_front == expected_at_front
    assert foo_task.description == expected_description
    assert foo_task.failure_ttl == expected_failure_ttl
    assert foo_task.retry == expected_retry
    assert foo_task.on_success == expected_on_success
    assert foo_task.on_failure == expected_on_failure
    assert foo_task.queue_class == rq.Queue


##########################################
# Test discover_task
##########################################


# Define a dummy @task decorator for testing purposes
def task(func):
    func._is_task = True
    return func


# Define some test functions to use with the @task decorator
@task
def test_func_1():
    pass


def test_func_2():
    pass


@task
class TestClass:
    def __call__(self):
        pass


# Define the tests for the discover_task function
def test_discover_task_valid_qualname():
    # Test with a valid fully-qualified function name
    assert utils.discover_task("tests.test_utils.test_func_1") == test_func_1


def test_discover_task_invalid_qualname():
    # Test with an invalid fully-qualified function name
    with pytest.raises(
        ValueError,
        match="Callable invalid_func_name not found in module tests.test_utils",
    ):
        utils.discover_task("tests.test_utils.invalid_func_name")


def test_discover_task_import_error():
    # Test with a module that can't be imported
    with pytest.raises(ImportError, match="No module named 'nonexistent_module'"):
        utils.discover_task("nonexistent_module.test_function")


def test_discover_task_not_decorated_task():
    # Test with a callable object that is not decorated with the @task decorator
    with pytest.raises(
        ValueError,
        match="Callable test_func_2 is not decorated with the @task decorator",
    ):
        utils.discover_task("tests.test_utils.test_func_2")


def test_discover_task_class():
    # Test with a class that is decorated with the @task decorator
    assert utils.discover_task("tests.test_utils.TestClass") == TestClass
