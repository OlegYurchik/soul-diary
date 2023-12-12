from facet import ServiceMixin

from .web import WebService, WebSettings, get_service as get_web_service


class UIService(ServiceMixin):
    def __init__(self, web: WebService):
        self._web = web

    @property
    def dependencies(self) -> list[ServiceMixin]:
        return [
            self._web,
        ]


def get_service() -> UIService:
    settings = WebSettings()
    web = get_web_service(settings=settings)
    return UIService(web=web)
