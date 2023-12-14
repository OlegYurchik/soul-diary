import fastapi
import uvicorn
from facet import ServiceMixin
from fastapi.middleware.cors import CORSMiddleware

from soul_diary.backend.database import DatabaseService, get_service as get_database_service
from . import router
from .settings import APISettings


class UvicornServer(uvicorn.Server):
    def install_signal_handlers(self):
        pass


class APIService(ServiceMixin):
    def __init__(self, database: DatabaseService, settings: APISettings, port: int = 8001):
        self._database = database
        self._settings = settings

        self._port = port

    @property
    def database(self) -> DatabaseService:
        return self._database

    @property
    def settings(self) -> APISettings:
        return self._settings

    def get_app(self) -> fastapi.FastAPI:
        app = fastapi.FastAPI()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app.service = self
        self.setup_app(app=app)

        return app

    def setup_app(self, app: fastapi.FastAPI):
        app.include_router(router.router)

    async def start(self):
        config = uvicorn.Config(app=self.get_app(), host="0.0.0.0", port=self._port)
        server = UvicornServer(config)

        self.add_task(server.serve())


def get_service() -> APIService:
    database_service = get_database_service()
    settings = APISettings()
    return APIService(
        database=database_service,
        settings=settings,
        port=settings.port,
    ) 
