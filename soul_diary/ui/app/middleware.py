import flet
from flet_route import Basket, Params

from soul_diary.ui.app.backend.local import LocalBackend
from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.models import BackendType
from soul_diary.ui.app.routes import AUTH, SENSE_LIST


async def middleware(page: flet.Page, params: Params, basket: Basket):
    if getattr(page.app, "backend_client", None) is not None:
        if page.route == AUTH:
            await page.go_async(SENSE_LIST)
        return

    local_storage = LocalStorage(client_storage=page.client_storage)
    auth_data = await local_storage.get_auth_data()
    if auth_data is None:
        await page.go_async(AUTH)
        return
    
    if auth_data.backend == BackendType.LOCAL:
        backend_client_class = LocalBackend
    else:
        await page.go_async(AUTH)
        return

    page.app.backend_client = backend_client_class(
        local_storage=local_storage,
        username=auth_data.username,
        encryption_key=auth_data.encryption_key,
        token=auth_data.token,
        **auth_data.backend_data,
    )
    if page.route == AUTH:
        await page.go_async(SENSE_LIST)
