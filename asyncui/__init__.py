"""Library for asynchronous GUI programming"""

__version__ = '1.0.0'

from .loop import asynchronous, run_async, create_future, get_loop, run_loop, set_future_result
from .threading import use_executor, run_in_thread, thread
