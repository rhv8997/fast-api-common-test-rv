from functools import wraps
from time import perf_counter_ns

from loguru import logger


def timed(func):
    @wraps(func)
    def timed_wrapper(*args, **kwargs):
        start_time = perf_counter_ns()
        result = func(*args, **kwargs)
        end_time = perf_counter_ns()
        total_time = (end_time - start_time) / 1000000
        logger.debug(f"function {func.__name__}{args} {kwargs} took {total_time} ms")
        return result

    return timed_wrapper
