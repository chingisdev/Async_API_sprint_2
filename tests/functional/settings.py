from pydantic import Field
from pydantic_settings import BaseSettings

from .testdata.es_mapping import ELASTIC_INDEX_SETTINGS


class TestSettings(BaseSettings):
    redis_host: str = Field("127.0.0.1")
    redis_port: int = Field(6379)

    elastic_host: str = Field("127.0.0.1")
    elastic_port: int = Field(9200)
    elastic_schema: str = Field("http")

    es_index_mapping: dict | None = ELASTIC_INDEX_SETTINGS

    service_host: str = Field()
    service_port: str = Field()

    @property
    def elastic_url(self):
        return f"{self.elastic_schema}://{self.elastic_host}:{self.elastic_port}"

    @property
    def service_url(self):
        return f"http://{self.service_host}:{self.service_port}"


test_settings = TestSettings()
