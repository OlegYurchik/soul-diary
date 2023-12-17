from typing import Any

from pydantic import conint
from pydantic_settings import BaseSettings, SettingsConfigDict


class WebSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ui_web_")

    port: conint(ge=1, le=65535) = 8000
    backend_data: dict[str, Any] = {
        "url": "http://localhost:8001",
    }
