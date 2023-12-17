import asyncio
import pathlib
import subprocess

import typer

from . import web
from .service import get_service


def publish():
    current_path = pathlib.Path(__file__).parent
    root_path = current_path.parent.parent
    requirements_path = current_path / "requirements.txt"
    entrypoint_path = current_path / "entrypoint.py"
    dist_path = root_path / "dist"

    subprocess.call(["poetry", "export", "-f", "requirements.txt", "--with", "ui", "--with", "main",
                     "--without-hashes", "--output", str(requirements_path)])
    subprocess.call(["flet", "publish", "--pre", "--distpath", str(dist_path),
                     str(entrypoint_path)])


def run():
    ui_service = get_service()

    asyncio.run(ui_service.run())


def get_cli() -> typer.Typer:
    cli = typer.Typer()

    cli.command(name="run")(run)
    cli.command(name="publish")(publish)
    cli.add_typer(web.get_cli(), name="web")

    return cli
