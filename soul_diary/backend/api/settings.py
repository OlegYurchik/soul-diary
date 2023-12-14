from pydantic import conint
from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="backend_api_")

    port: conint(ge=1, le=65535) = 8001

    registration_enabled: bool = True
