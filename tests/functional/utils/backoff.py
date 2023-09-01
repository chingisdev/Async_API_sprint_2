import logging

from tenacity import before_sleep_log, retry, wait_exponential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def backoff(wait_multiplier=1, wait_min=4, wait_max=10):
    """Wrap input function with exponential backoff retry logic."""

    def decorator(func):
        return retry(
            wait=wait_exponential(
                multiplier=wait_multiplier,
                min=wait_min,
                max=wait_max,
            ),
            before_sleep=before_sleep_log(logger, logging.INFO),
        )(func)

    return decorator
