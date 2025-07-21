import asyncio
from asyncio import Future
from concurrent.futures import Executor
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Generator, Optional, TypeVar

try:
    from typing import ParamSpec
except ImportError:
    from typing_extensions import ParamSpec

import asyncui

_EXECUTOR: Optional[Executor] = None


@contextmanager
def use_executor(executor: Executor) -> Generator[Executor, None, None]:
    global _EXECUTOR
    try:
        _EXECUTOR = executor
        yield executor
    finally:
        executor.shutdown()
        _EXECUTOR = None


R = TypeVar("R")
P = ParamSpec("P")


def run_in_thread(func: Callable[P, R], *args, **kwargs) -> Future[R]:
    """runs function in a thread and returns a Future"""
    if _EXECUTOR is None:
        raise ValueError("Executor is not set")
    future = _EXECUTOR.submit(func, *args, **kwargs)
    return asyncio.wrap_future(future, loop=asyncui.get_loop())


def thread(func: Callable[P, R]) -> Callable[P, Future[R]]:
    """Decorator to run a function in a thread."""

    @wraps(func)
    def decorated(*args, **kwargs) -> Future[R]:
        return run_in_thread(func, *args, **kwargs)

    return decorated
