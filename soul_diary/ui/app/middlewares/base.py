from typing import Callable

import flet
from flet_route import Basket, Params


class BaseMiddleware:
    async def __call__(
            self,
            page: flet.Page,
            params: Params,
            basket: Basket,
            next_handler: Callable,
    ):
        raise NotImplementedError
