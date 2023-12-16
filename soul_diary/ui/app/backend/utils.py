from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.models import BackendType
from .base import BaseBackend
from .exceptions import NonAuthenticatedException
from .local import LocalBackend
from .soul import SoulBackend


BACKEND_MAPPING = {
    BackendType.LOCAL: LocalBackend,
    BackendType.SOUL: SoulBackend,
}


async def get_backend_client(local_storage: LocalStorage) -> BaseBackend:
    auth_data = await local_storage.get_auth_data()
    if auth_data is None:
        raise NonAuthenticatedException()

    backend_client_class = BACKEND_MAPPING.get(auth_data.backend, None)
    if backend_client_class is None:
        raise

    return backend_client_class(
        local_storage=local_storage,
        username=auth_data.username,
        encryption_key=auth_data.encryption_key,
        token=auth_data.token,
        **auth_data.backend_data,
    )
