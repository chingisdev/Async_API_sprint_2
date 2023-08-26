import time

from functional.settings import test_settings
from redis.client import Redis

if __name__ == "__main__":
    redis_client: Redis = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    while True:
        if redis_client.ping():
            break
        time.sleep(1)
