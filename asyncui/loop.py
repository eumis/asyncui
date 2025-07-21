import asyncio
import os
import traceback
from asyncio import AbstractEventLoop, Future, events, tasks
from contextlib import contextmanager
from functools import partial, wraps
from threading import Thread
from typing import Any, Generator, Optional, Tuple

_ASYNC_LOOP: Optional[AbstractEventLoop] = None


@contextmanager
def run_loop(loop: Optional[AbstractEventLoop] = None) -> Generator[AbstractEventLoop, None, None]:
    """Run an asyncio event loop in a separate thread"""
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    if loop is None:
        loop = events.new_event_loop()
    global _ASYNC_LOOP
    try:
        _ASYNC_LOOP = loop
        loop_thread = Thread(target=partial(_run_loop, _ASYNC_LOOP))
        loop_thread.start()
        yield _ASYNC_LOOP
    finally:
        if _ASYNC_LOOP:
            _ASYNC_LOOP.call_soon_threadsafe(_ASYNC_LOOP.stop)
            _ASYNC_LOOP = None


def _run_loop(loop: AbstractEventLoop):
    if events._get_running_loop() is not None:
        raise RuntimeError("Event loop is already run")
    try:
        events.set_event_loop(loop)
        # loop.set_debug(environment.is_dev())
        loop.run_forever()
    finally:
        try:
            _cancel_all_tasks(loop)
            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            events.set_event_loop(None)
            loop.close()


def _cancel_all_tasks(loop: AbstractEventLoop):
    to_cancel = tasks.all_tasks(loop)
    if not to_cancel:
        return

    for task in to_cancel:
        task.cancel()

    loop.run_until_complete(tasks.gather(*to_cancel, return_exceptions=True))

    for task in to_cancel:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler(
                {
                    "message": "unhandled exception during asyncio.run() shutdown",
                    "exception": task.exception(),
                    "task": task,
                }
            )


def get_loop() -> AbstractEventLoop:
    """Get running asyncio event loop."""
    if _ASYNC_LOOP is None:
        raise RuntimeError("Event loop is not run")
    return _ASYNC_LOOP


def asynchronous(func):
    """Decorator to run function in async event loop"""
    if not asyncio.iscoroutinefunction(func):
        raise ValueError(f"{func} is expected to be coroutine function")

    @wraps(func)
    def decorated(*args, **kwargs) -> Future:
        return _run_async(func, *args, **kwargs)

    return decorated


def run_async(func, *args, **kwargs) -> Future:
    """Run function in async event loop"""
    if not asyncio.iscoroutinefunction(func):
        print("WARNING: func is not coroutine")
    return _run_async(func, *args, **kwargs)


def _run_async(func, *args, **kwargs) -> Future:
    loop = get_loop()
    future = asyncio.run_coroutine_threadsafe(_handle_async_errors(func, args, kwargs), loop)
    return asyncio.wrap_future(future, loop=loop)


async def _handle_async_errors(func, args: Tuple[Any, ...], kwargs: dict):
    try:
        return await func(*args, **kwargs)
    except BaseException as error:
        traceback.print_list(traceback.extract_stack())
        # handle_error(type(error), error, error.__traceback__)
        raise error


def create_future() -> Future:
    """Create a new Future object using the current event loop."""
    return get_loop().create_future()


def set_future_result(future: Future, result: Any):
    """Set future result in async loop thread"""
    if future._state == "FINISHED":
        return
    get_loop().call_soon_threadsafe(partial(future.set_result, result))
