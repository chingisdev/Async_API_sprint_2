import logging
import time
from datetime import datetime, timedelta


def repeat_after_sleep(
    f,
):
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)

        if result.tzinfo:
            result = result.replace(tzinfo=None)

        if result > datetime.now() - timedelta(minutes=1):
            # Calculate the number of seconds to sleep
            sleep_seconds = 60
            logging.info("Sleeping for {sleep_seconds} seconds...".format(sleep_seconds=sleep_seconds))
            time.sleep(60)

    return wrapper
