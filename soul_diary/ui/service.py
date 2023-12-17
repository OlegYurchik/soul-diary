from facet import ServiceMixin

from .web import WebService, get_service as get_web_service


class UIService(ServiceMixin):
    def __init__(self, web: WebService):
        self._web = web

    @property
    def dependencies(self) -> list[ServiceMixin]:
        return [
            self._web,
        ]


def get_service() -> UIService:
    web = get_web_service()
    return UIService(web=web)
