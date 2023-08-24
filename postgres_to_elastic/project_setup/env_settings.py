import logging

from pydantic_settings import BaseSettings

logging.basicConfig(level=logging.INFO)


class Settings(BaseSettings):
    postgres_host: str
    postgres_port: int
    postgres_password: str
    postgres_db: str
    postgres_user: str
    redis_host: str
    redis_port: int
    elastic_host: str
    elastic_port: int
    elastic_scheme: str
    repeat_time_seconds: int

    @property
    def elastic_url(
        self,
    ):
        return f"{self.elastic_scheme}://{self.elastic_host}:{self.elastic_port}"

    @property
    def database_url(
        self,
    ):
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def redis_url(
        self,
    ):
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    class Config:
        env_file = "../../.env.example"
