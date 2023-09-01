from functional.settings import test_settings
from functional.utils.backoff import backoff
from redis.client import Redis


@backoff()
def wait_for_redis():
    client: Redis = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    if client.ping():
        return
    raise Exception("Redis is not ready...")


if __name__ == "__main__":
    wait_for_redis()
