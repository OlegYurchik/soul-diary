import asyncio
import typer

from .service import get_service


def run():
    web_service = get_service()

    asyncio.run(web_service.run())


def get_cli() -> typer.Typer:
    cli = typer.Typer()

    cli.command(name="run")(run)

    return cli
