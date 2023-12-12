import flet
from flet_route import Basket, Params

from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.models import BackendType
from soul_diary.ui.app.routes import AUTH, SENSE_LIST


async def middleware(page: flet.Page, params: Params, basket: Basket):
    local_storage = LocalStorage(client_storage=page.client_storage)
    auth_data = await local_storage.get_auth_data()
    if auth_data is None:
        await page.go_async(AUTH)
        return

    if auth_data.backend not in BackendType:
        await page.go_async(AUTH)
        return

    if page.route == AUTH:
        await page.go_async(SENSE_LIST)
