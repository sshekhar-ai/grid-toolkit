import functools
import logging
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def retry(
    times: int = 3,
    delay: float = 1.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable:
    """Call the decorated function up to `times` times, sleeping `delay` seconds between tries."""
    if times < 1:
        raise ValueError("times must be at least 1")

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == times:
                        raise
                    logger.warning(
                        "%s failed (attempt %d/%d): %s", func.__name__, attempt, times, e
                    )
                    time.sleep(delay)

        return wrapper

    return decorator


@contextmanager
def timed(label: str) -> Iterator[None]:
    """Log how long the `with` block took."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info("%s took %.3fs", label, elapsed)
