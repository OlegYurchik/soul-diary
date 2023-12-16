from functools import partial
from typing import Any

import flet

from soul_diary.ui.app.backend.exceptions import (
    IncorrectCredentialsException,
    UserAlreadyExistsException,
)
from soul_diary.ui.app.backend.utils import BACKEND_MAPPING
from soul_diary.ui.app.controls.utils import in_progress
from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.models import BackendType
from soul_diary.ui.app.pages.base import BasePage, callback_error_handle
from soul_diary.ui.app.routes import SENSE_LIST


class LoginPage(BasePage):
    def __init__(
            self,
            view: flet.View,
            local_storage: LocalStorage,
            backend: BackendType,
            backend_registration_enabled: bool,
            backend_data: dict[str, Any] | None = None, 
            username: str | None = None,
            password: str | None = None,
            can_return_back: bool = True,
    ):
        self.local_storage = local_storage
        self.backend = backend
        self.backend_registration_enabled = backend_registration_enabled
        self.backend_data = backend_data
        self.username = username
        self.password = password
        self.can_return_back = can_return_back

        super().__init__(view=view)

    def build(self) -> flet.Container:
        controls = []
        if self.can_return_back:
            return_back_button = flet.IconButton(
                icon=flet.icons.ARROW_BACK,
                on_click=self.callback_return_back,
            )
            controls.append(return_back_button)
        top_row = flet.Row(
            controls=controls,
            width=300,
            alignment=flet.MainAxisAlignment.START,
        )

        username_field = flet.TextField(
            label="Логин",
            value=self.username,
            on_change=self.callback_change_username,
        )
        password_field = flet.TextField(
            label="Пароль",
            password=True,
            can_reveal_password=True,
            on_change=self.callback_change_password,
        )
        signin_button = flet.ElevatedButton(
            text="Войти",
            width=300,
            height=50,
            on_click=partial(
                self.callback_signin,
                username_field=username_field,
                password_field=password_field,
            ),
        )
        signup_button = flet.ElevatedButton(
            text="Зарегистрироваться",
            width=300,
            height=50,
            disabled=not self.backend_registration_enabled,
            on_click=partial(
                self.callback_signup,
                username_field=username_field,
                password_field=password_field,
            ),
        )
        return flet.Container(
            content=flet.Column(
                controls=[top_row, username_field, password_field, signin_button, signup_button],
                width=300,
            ),
            alignment=flet.alignment.center,
        )

    @callback_error_handle
    async def callback_return_back(self, event: flet.ControlEvent):
        await self.local_storage.add_shared_data(username=self.username)

        if self.backend == BackendType.LOCAL:
            from .backend import BackendPage

            backend = await self.local_storage.get_shared_data(key="backend")
            if backend is not None:
                backend = BackendType(backend)
            await BackendPage(
                view=self.view,
                local_storage=self.local_storage,
                backend=backend,
            ).apply()
        elif self.backend == BackendType.SOUL:
            from .soul_server import SoulServerPage

            backend_data = await self.local_storage.get_shared_data("backend_data")
            if backend_data is None:
                backend_data = {}
            await SoulServerPage(
                view=self.view,
                local_storage=self.local_storage,
                url=backend_data.get("url"),
            ).apply()

    @callback_error_handle
    async def callback_change_username(self, event: flet.ControlEvent):
        self.username = event.control.value

    @callback_error_handle
    async def callback_change_password(self, event: flet.ControlEvent):
        self.password = event.control.value

    @callback_error_handle
    async def callback_signup(
            self,
            event: flet.ControlEvent,
            username_field: flet.TextField,
            password_field: flet.TextField,
    ):
        if not self.username:
            username_field.error_text = "Заполните имя пользователя"
            await username_field.update_async()
        if not self.password:
            password_field.error_text = "Заполните пароль"
            await password_field.update_async()
        if not self.username or not self.password:
            return

        backend_client_class = BACKEND_MAPPING[self.backend]
        backend_data = await self.local_storage.get_shared_data("backend_data")
        if backend_data is None:
            backend_data = self.backend_data or {}
        backend_client = backend_client_class(
            local_storage=self.local_storage,
            **backend_data,
        )

        async with in_progress(page=event.page):
            try:
                await backend_client.registration(username=self.username, password=self.password)
            except UserAlreadyExistsException:
                username_field.error_text = "Пользователь с таким именем уже существует"
                password_field.error_text = None
                await username_field.update_async()
                await password_field.update_async()
                return

        await self.local_storage.clear_shared_data()
        await event.page.go_async(SENSE_LIST)

    @callback_error_handle
    async def callback_signin(
            self,
            event: flet.ControlEvent,
            username_field: flet.TextField,
            password_field: flet.TextField,
    ):
        if not self.username:
            username_field.error_text = "Заполните имя пользователя"
            await username_field.update_async()
        if not self.password:
            password_field.error_text = "Заполните пароль"
            await password_field.update_async()
        if not self.username or not self.password:
            return

        backend_client_class = BACKEND_MAPPING[self.backend]
        backend_data = await self.local_storage.get_shared_data("backend_data")
        if backend_data is None:
            backend_data = self.backend_data or {} 
        backend_client = backend_client_class(
            local_storage=self.local_storage,
            **backend_data,
        )

        async with in_progress(page=event.page):
            try:
                await backend_client.login(username=self.username, password=self.password)
            except IncorrectCredentialsException:
                username_field.error_text = None
                password_field.error_text = "Неверные имя пользователя и пароль"
                await username_field.update_async()
                await password_field.update_async()
                return

        await self.local_storage.clear_shared_data()
        await event.page.go_async(SENSE_LIST)
