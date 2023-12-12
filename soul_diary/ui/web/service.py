from typing import Any

import flet_fastapi
import uvicorn
from facet import ServiceMixin

from soul_diary.ui.app.models import BackendType
from soul_diary.ui.app import SoulDiaryApp
from .settings import WebSettings


class UvicornServer(uvicorn.Server):
    def install_signal_handlers(self):
        pass


class WebService(ServiceMixin):
    def __init__(self, port: int = 8000, backend_data: dict[str, Any] | None = None):
        self._port = port
        self._backend_data = backend_data

    @property
    def port(self) -> int:
        return self._port

    async def start(self):
        app = flet_fastapi.app(SoulDiaryApp(
            # backend=BackendType.SOUL,
            # backend_data=self._backend_data,
            backend=BackendType.LOCAL,
        ).run)
        config = uvicorn.Config(app=app, host="0.0.0.0", port=self._port)
        server = UvicornServer(config)

        self.add_task(server.serve())


def get_service(settings: WebSettings) -> WebService:
    return WebService(port=settings.port, backend_data=settings.backend_data)
