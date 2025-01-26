import pika
import random
import time
from functools import wraps

import requests
from loguru import logger


def backoff(
    start_sleep_time: float = 1,
    factor: int = 1.3,
    border_sleep_time: int = 5,
    max_tries: int = 10,
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
                except (pika.exceptions.ConnectionClosed, pika.exceptions.ChannelClosed):
                    logger.info(f"Try N {count_tries}")
                    count_tries += 1
                    time.sleep(sleep_time)
                    sleep_time = min(sleep_time * factor + random.random(), border_sleep_time)
                except Exception:
                    raise
            raise RuntimeError(f"Function {func.__name__} failed after { max_tries}")

        return inner

    return func_wrapper


def timer(func):
    """Таймер"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        logger.info("Execution time of %s: %s" % (func.__name__, str(execution_time)))
        return result
    return wrapper
