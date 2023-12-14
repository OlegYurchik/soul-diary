import asyncio
from functools import partial
from typing import Any

import flet
from pydantic import AnyHttpUrl

from soul_diary.ui.app.backend.exceptions import IncorrectCredentialsException, UserAlreadyExistsException
from soul_diary.ui.app.backend.soul import SoulBackend
from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.models import BackendType, Options
from soul_diary.ui.app.routes import AUTH, SENSE_LIST
from soul_diary.ui.app.views.exceptions import SoulServerIncorrectURL
from .base import BaseView, view


class AuthView(BaseView):
    def __init__(
            self,
            local_storage: LocalStorage,
            backend: BackendType | None = None,
            backend_data: dict[str, Any] | None = None,
    ):
        self.top_container: flet.Container
        self.center_container: flet.Container
        self.bottom_container: flet.Container

        self.initial_backend = self.backend = backend
        self.initial_backend_data = self.backend_data = backend_data or {}
        self.backend_registration_enabled: bool = True
        self.username: str | None = None
        self.password: str | None = None

        super().__init__(local_storage=local_storage)

    async def clear(self):
        self.top_container.content = None
        self.center_container.content = None
        self.bottom_container.content = None

    def clear_data(self):
        self.backend = self.initial_backend
        self.backend_data = self.initial_backend_data
        self.username = None
        self.password = None

    async def setup(self):
        self.top_container = flet.Container(alignment=flet.alignment.center)
        self.center_container = flet.Container(alignment=flet.alignment.center)
        self.bottom_container = flet.Container(alignment=flet.alignment.center)

        self.container.content = flet.Column(
            controls=[self.top_container, self.center_container, self.bottom_container],
            width=300,
        )
        self.container.alignment = flet.alignment.center

        self.view.route = AUTH
        self.view.vertical_alignment = flet.MainAxisAlignment.CENTER

    @view(initial=True)
    async def entrypoint_view(self, page: flet.Page):
        if self.initial_backend == BackendType.SOUL:
            async def connect():
                async with self.in_progress(page=page):
                    options = await self.connect_to_soul_server()
                self.backend_registration_enabled = options.registration_enabled
                await self.credentials_view(page=page)

            loop = asyncio.get_running_loop()
            loop.create_task(connect())
        elif self.initial_backend == BackendType.LOCAL:
            await self.credentials_view(page=page)
        else:
            await self.backend_view(page=page)

    @view()
    async def backend_view(self, page: flet.Page):
        label = flet.Text("Выберите сервер")
        self.top_container.content = label

        backend_dropdown = flet.Dropdown(
            label="Бэкенд",
            options=[
                flet.dropdown.Option(text="Локально", key=BackendType.LOCAL.value),
                flet.dropdown.Option(text="Soul Diary сервер", key=BackendType.SOUL.value),
            ],
            value=None if self.backend is None else self.backend.value,
            on_change=self.callback_change_backend,
        )
        self.center_container.content = backend_dropdown

        connect_button = flet.ElevatedButton(
            "Выбрать",
            width=300,
            height=50,
            on_click=partial(self.callback_choose_backend, dropdown=backend_dropdown),
        )
        self.bottom_container.content = connect_button

    @view()
    async def soul_server_data_view(self, page: flet.Page):
        label = flet.Text("Soul Diary сервер")
        backend_button = flet.IconButton(
            icon=flet.icons.ARROW_BACK,
            on_click=self.callback_go_backend,
        )
        self.top_container.content = flet.Row(
            controls=[backend_button, label],
            width=300,
            alignment=flet.MainAxisAlignment.START,
        )

        url_field = flet.TextField(
            width=300,
            label="URL",
            value=self.backend_data.get("url"),
            on_change=self.callback_change_soul_server_url,
        )
        self.center_container.content = url_field

        connect_button = flet.ElevatedButton(
            "Подключиться",
            width=300,
            height=50,
            on_click=partial(self.callback_soul_server_connect, url_field=url_field),
        )
        self.bottom_container.content = connect_button

    @view()
    async def credentials_view(self, page: flet.Page):
        controls = []
        if self.initial_backend is None:
            backend_data_button = flet.IconButton(
                icon=flet.icons.ARROW_BACK,
                on_click=self.callback_go_backend_data,
            )
            controls.append(backend_data_button)
        self.top_container.content = flet.Row(
            controls=controls,
            width=300,
            alignment=flet.MainAxisAlignment.START,
        )

        username_field = flet.TextField(
            label="Логин",
            on_change=self.callback_change_username,
        )
        password_field = flet.TextField(
            label="Пароль",
            password=True,
            can_reveal_password=True,
            on_change=self.callback_change_password,
        )
        self.center_container.content = flet.Column(
            controls=[username_field, password_field],
            width=300,
        )

        signin_button = flet.Container(
            content=flet.ElevatedButton(
                text="Войти",
                width=300,
                height=50,
                on_click=partial(
                    self.callback_signin,
                    username_field=username_field,
                    password_field=password_field,
                ),
            ),
            alignment=flet.alignment.center,
        )
        signup_button = flet.Container(
            content=flet.ElevatedButton(
                text="Зарегистрироваться",
                width=300,
                height=50,
                disabled=not self.backend_registration_enabled,
                on_click=partial(
                    self.callback_signup,
                    username_field=username_field,
                    password_field=password_field,
                ),
            ),
            alignment=flet.alignment.center,
        )

        self.bottom_container.content = flet.Column(controls=[signin_button, signup_button])

    async def callback_change_backend(self, event: flet.ControlEvent):
        self.backend = BackendType(event.control.value)
        event.control.error_text = None
        await event.page.update_async()

    async def callback_choose_backend(self, event: flet.ControlEvent, dropdown: flet.Dropdown):
        if self.backend == BackendType.LOCAL:
            await self.credentials_view(page=event.page)
        elif self.backend == BackendType.SOUL:
            await self.soul_server_data_view(page=event.page)
        else:
            dropdown.error_text = "Выберите тип бекенда"
            await event.page.update_async()

    async def callback_change_soul_server_url(self, event: flet.ControlEvent):
        try:
            AnyHttpUrl(event.control.value or "")
        except:
            event.control.error_text = "Некорректный URL"
            self.backend_data["url"] = None
        else:
            event.control.error_text = None
            self.backend_data["url"] = event.control.value
        await event.page.update_async()

    async def callback_soul_server_connect(
            self,
            event: flet.ControlEvent,
            url_field: flet.TextField,
    ):
        if self.backend == BackendType.SOUL:
            async with self.in_progress(page=event.page):
                try:
                    options = await self.connect_to_soul_server()
                except SoulServerIncorrectURL:
                    url_field.error_text = "Некорректный URL"
                except:
                    url_field.error_text = "Невозможно подключиться к серверу"
                    await event.page.update_async()
                else:
                    self.backend_registration_enabled = options.registration_enabled
        else:
            await self.credentials_view(page=event.page)

    async def connect_to_soul_server(self) -> Options:
        try:
            backend_url = AnyHttpUrl(self.backend_data.get("url"))
        except ValueError:
            raise SoulServerIncorrectURL()
        
        backend_client = SoulBackend(
            local_storage=self.local_storage,
            url=str(backend_url),
        )
        return await backend_client.get_options()
        
    async def callback_change_username(self, event: flet.ControlEvent):
        self.username = event.control.value

    async def callback_change_password(self, event: flet.ControlEvent):
        self.password = event.control.value

    async def callback_signin(
            self,
            event: flet.ControlEvent,
            username_field: flet.TextField,
            password_field: flet.TextField,
    ):
        if not self.username:
            username_field.error_text = "Заполните имя пользователя"
        if not self.password:
            password_field.error_text = "Заполните пароль"
        if not self.username or not self.password:
            await event.page.update_async()
            return

        backend_client_class = self.BACKEND_MAPPING.get(self.backend)
        if backend_client_class is None:
            raise
        backend_client = backend_client_class(
            local_storage=self.local_storage,
            **self.backend_data,
        )

        async with self.in_progress(page=event.page):
            try:
                await backend_client.login(username=self.username, password=self.password)
            except IncorrectCredentialsException:
                password_field.error_text = "Неверные имя пользователя и пароль"
                await event.page.update_async()
                return

        await event.page.go_async(SENSE_LIST)

    async def callback_signup(
            self,
            event: flet.ControlEvent,
            username_field: flet.TextField,
            password_field: flet.TextField,
    ):
        if not self.username:
            username_field.error_text = "Заполните имя пользователя"
        if not self.password:
            password_field.error_text = "Заполните пароль"
        if not self.username or not self.password:
            await event.page.update_async()
            return

        backend_client_class = self.BACKEND_MAPPING.get(self.backend)
        if backend_client_class is None:
            raise
        backend_client = backend_client_class(
            local_storage=self.local_storage,
            **self.backend_data,
        )

        async with self.in_progress(page=event.page):
            try:
                await backend_client.registration(username=self.username, password=self.password)
            except UserAlreadyExistsException:
                username_field.error_text = "Пользователь с таким именем уже существует"
                await event.page.update_async()
                return

        await event.page.go_async(SENSE_LIST)

    async def callback_go_backend(self, event: flet.ControlEvent):
        await self.backend_view(page=event.page)

    async def callback_go_backend_data(self, event: flet.ControlEvent):
        if self.backend == BackendType.SOUL:
            await self.soul_server_data_view(page=event.page)
        elif self.backend == BackendType.LOCAL:
            await self.backend_view(page=event.page)
