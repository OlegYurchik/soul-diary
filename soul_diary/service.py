from facet import ServiceMixin

from .backend import BackendService, get_service as get_backend_service
from .ui import UIService, get_service as get_ui_service


class SoulDiaryService(ServiceMixin):
    def __init__(self, backend: BackendService, ui: UIService):
        self._backend = backend
        self._ui = ui

    @property
    def dependencies(self) -> list[ServiceMixin]:
        return [
            self._backend,
            self._ui,
        ]


def get_service() -> SoulDiaryService:
    backend_service = get_backend_service()
    ui_service = get_ui_service()
    return SoulDiaryService(backend=backend_service, ui=ui_service)
