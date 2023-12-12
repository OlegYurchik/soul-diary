from typing import Any

from pydantic import conint
from pydantic_settings import BaseSettings


class WebSettings(BaseSettings):
    port: conint(ge=1, le=65535) = 8000
    backend_data: dict[str, Any] = {
        "url": "http://localhost:8001",
    }


def get_settings() -> WebSettings:
    return WebSettings()
