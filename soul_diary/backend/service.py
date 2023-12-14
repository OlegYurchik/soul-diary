from facet import ServiceMixin

from .api import APIService, get_service as get_api_service


class BackendService(ServiceMixin):
    def __init__(self, api: APIService):
        self._api = api

    @property
    def dependencies(self) -> list[ServiceMixin]:
        return [
            self._api,
        ]


def get_service() -> BackendService:
    api_service = get_api_service()
    return BackendService(api=api_service)
