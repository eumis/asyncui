import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
from functools import partial
from typing import Any

from pytest import mark

from asyncui import run_in_thread, run_loop, thread
import asyncui


@thread
def run_in_thread_decorated(value: Any) -> Any:
    return return_value(value)


def return_value(value: Any) -> Any:
    return value


def wait_result(future: asyncio.Future, timeout: float = 0.5) -> Any:
    result = None
    start = time.time()
    while not future.done() and time.time() - start < timeout:
        time.sleep(0.1)
        result = future.result()
    return result


class CallAsyncTests:

    @mark.parametrize(
        "test_fun, value",
        [
            (run_in_thread_decorated, 42),
            (partial(run_in_thread, return_value), "value"),
        ],
    )
    def test_returns_future(self, test_fun, value):
        """should return a future"""
        with run_loop():
            with asyncui.use_executor(ThreadPoolExecutor()):
                future = test_fun(value)

                actual = wait_result(future)

                assert isinstance(future, asyncio.Future)
                assert actual == value
