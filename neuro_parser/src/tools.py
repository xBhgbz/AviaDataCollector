from functools import wraps
from random import random
import time

from loguru import logger


def backoff(
    start_sleep_time: float = 60 * 3,
    factor: int = 1.3,
    border_sleep_time: int = 60 * 5,
    max_tries: int = 5,
    exceptions: tuple = (Exception, )
):
    """Позволяет повторить попытку выполнить функцию max_tries количество раз"""

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            count_tries = 0
            while count_tries < max_tries:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    logger.info(f"Try N {count_tries}")
                    count_tries += 1
                    time.sleep(sleep_time)
                    sleep_time = min(sleep_time * factor + random(), border_sleep_time)
                except Exception:
                    raise
            raise RuntimeError(f"Function {func.__name__} failed after { max_tries}")

        return inner

    return func_wrapper