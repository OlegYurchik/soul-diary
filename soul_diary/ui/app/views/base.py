from contextlib import asynccontextmanager
from functools import partial, reduce
from typing import Any, Callable, Sequence

import flet
from flet_route import Basket, Params

from soul_diary.ui.app.middlewares.base import BaseMiddleware


def view(initial: bool = False, disabled: bool = False):
    def decorator(function: Callable):
        async def wrapper(self, page: flet.Page):
            await self.clear()

            await function(self, page=page)
            await page.update_async()

        wrapper._view_enabled = not disabled
        wrapper._view_initial = initial

        return wrapper
    return decorator


def setup_middlewares(function: Callable):
    async def wrapper(self, page: flet.Page, params: Params, basket: Basket) -> flet.View:
        entrypoint = partial(function, self)
        if self.middlewares:
            entrypoint = partial(self.middlewares[-1], next_handler=entrypoint)
            entrypoint = reduce(
                lambda entrypoint, function: partial(entrypoint, next_handler=function),
                self.middlewares[-2::-1],
                entrypoint,
            )
        return await entrypoint(page=page, params=params, basket=basket)

    return wrapper


class MetaView(type):
    def __init__(cls, name: str, bases: tuple[type], attrs: dict[str, Any]):
        super().__init__(name, bases, attrs)

        is_abstract = attrs.pop("is_abstract", False)
        if not is_abstract:
            cls.setup_class(attrs=attrs)

    def setup_class(cls, attrs: dict[str, Any]):
        initial_view = None
        for attr in attrs.values():
            view_enabled = getattr(attr, "_view_enabled", False)
            view_initial = getattr(attr, "_view_initial", False)
            if view_enabled and view_initial:
                if initial_view is not None:
                    raise ValueError(f"Initial view already defined: {initial_view.__name__}")
                initial_view = attr
        if initial_view is None:
            raise ValueError("Initial view must be defined")

        cls._initial_view = initial_view


class BaseView(metaclass=MetaView):
    is_abstract = True
    _initial_view: Callable | None

    def __init__(self, middlewares: Sequence[BaseMiddleware | Callable] = ()):
        self.middlewares = middlewares

        self.container: flet.Container
        self.stack: flet.Stack
        self.view: flet.View

    @setup_middlewares
    async def entrypoint(self, page: flet.Page, params: Params, basket: Basket) -> flet.View:
        self.container = flet.Container()
        self.stack = flet.Stack(controls=[self.container])
        self.view = flet.View(controls=[self.stack], route="/test")

        await self.setup()
        await self.clear()
        self.clear_data()
        await self.run_initial_view(page=page)
        return self.view

    async def setup(self):
        pass

    async def clear(self):
        pass

    def clear_data(self):
        pass

    @asynccontextmanager
    async def in_progress(self, page: flet.Page, tooltip: str | None = None):
        for control in self.stack.controls:
            control.disabled = True
        self.stack.controls.append(
            flet.Container(
                content=flet.ProgressRing(tooltip=tooltip),
                alignment=flet.alignment.center,
            ),
        )
        await page.update_async()

        yield

        self.stack.controls.pop()
        for control in self.stack.controls:
            control.disabled = False
        await page.update_async()

    async def run_initial_view(self, page: flet.Page):
        if self._initial_view is not None:
            await self._initial_view(page=page)
