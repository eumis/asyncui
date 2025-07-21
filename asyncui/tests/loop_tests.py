import asyncio
import time
from functools import partial
from typing import Any

import pytest
from pytest import mark

from asyncui.loop import asynchronous, create_future, get_loop, run_async, run_loop, set_future_result


class RunLoopTests:

    def test_run_loop_returns_current_loop(self):
        """should return current event loop"""
        with run_loop() as loop:
            assert loop is not None
            assert isinstance(loop, asyncio.AbstractEventLoop)

    def test_run_loop_uses_passed_loop(self):
        """should return passed event loop"""
        loop = asyncio.new_event_loop()
        with run_loop(loop) as actual_loop:
            assert actual_loop is loop

    def test_get_loop_returns_current_loop(self):
        """should return current event loop"""
        with run_loop() as loop:
            current_loop = get_loop()
            assert current_loop == loop

    def test_get_loop_returns_passed_loop(self):
        """should return passed event loop"""
        loop = asyncio.new_event_loop()
        with run_loop(loop):
            assert loop is get_loop()

    def test_get_loop_raises_error(self):
        """should raises RuntimeError when no loop is running"""
        with pytest.raises(RuntimeError, match="Event loop is not run"):
            get_loop()


@asynchronous
async def async_decorated(value: Any) -> Any:
    return await async_return_value(value)


async def async_return_value(value: Any) -> Any:
    await asyncio.sleep(0.01)
    return value


def wait_result(future: asyncio.Future, timeout: float = 0.6) -> Any:
    result = None
    start = time.time()
    while time.time() - start < timeout:
        time.sleep(0.2)
        if future.done():
            result = future.result()
            break
    return result


class RunAsyncTests:

    @mark.parametrize(
        "test_fun, value",
        [
            (async_decorated, 42),
            (partial(run_async, async_return_value), "value"),
        ],
    )
    def test_returns_future(self, test_fun, value):
        """should return a future"""
        with run_loop():
            future = test_fun(value)

            actual = wait_result(future)

            assert isinstance(future, asyncio.Future)
            assert actual == value


class FutureTests:
    def test_create_future_returns_future(self):
        """should create a future"""
        with run_loop():
            future = create_future()

            assert isinstance(future, asyncio.Future)
            assert not future.done()

    @mark.parametrize("value", [42, "value"])
    def test_set_future_result(self, value):
        """should set future result"""
        with run_loop():
            future = create_future()

            set_future_result(future, value)

            wait_result(future)
            assert future.done()
            assert future.result() == value
