import pathlib
import uuid
from contextlib import asynccontextmanager
from typing import Type

import bcrypt
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from facet import ServiceMixin
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .models import Sense, Session, User
from .settings import DatabaseSettings


class DatabaseService(ServiceMixin):
    def __init__(self, dsn: str):
        self._dsn = dsn
        self._engine = create_async_engine(self._dsn, pool_recycle=60)
        self._sessionmaker = async_sessionmaker(self._engine, expire_on_commit=False)

    def get_alembic_config(self) -> AlembicConfig:
        migrations_path = pathlib.Path(__file__).parent / "migrations"

        config = AlembicConfig()
        config.set_main_option("script_location", str(migrations_path))
        config.set_main_option("sqlalchemy.url", self._dsn.replace("%", "%%"))

        return config

    def get_models(self) -> list[Type[DeclarativeBase]]:
        return [User, Sense]

    @asynccontextmanager
    async def transaction(self):
        async with self._sessionmaker() as session:
            async with session.begin():
                yield session

    def migrate(self):
        alembic_command.upgrade(self.get_alembic_config(), "head")

    def rollback(self, revision: str | None = None):
        revision = revision or "-1"

        alembic_command.downgrade(self.get_alembic_config(), revision)

    def show_migrations(self):
        alembic_command.history(self.get_alembic_config())

    def create_migration(self, message: str | None = None):
        alembic_command.revision(
            self.get_alembic_config(), message=message, autogenerate=True,
        )

    async def create_user(self, session: AsyncSession, username: str, password: str) -> User:
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")
        user = User(username=username, password=hashed_password)
        user_session = Session(user=user)
        user.sessions.append(user_session)

        session.add_all([user, user_session])

        return user

    async def auth_user(
            self,
            session: AsyncSession,
            username: str,
            password: str,
    ) -> Session | None:
        query = select(User).where(User.username == username)

        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            return None

        user_session = Session(user=user)
        session.add(user_session)

        return user_session

    async def logout_user(self, session: AsyncSession, user_session: Session):
        await session.delete(user_session)

    async def get_user_session(self, session: AsyncSession, token: str) -> Session | None:
        query = select(Session).where(Session.token == token)

        result = await session.execute(query)
        user_session = result.scalar_one_or_none()

        return user_session

    async def get_senses(self, session: AsyncSession, user: User) -> list[Sense]:
        query = select(Sense).where(Sense.user == user).order_by(Sense.created_at.desc())

        result = await session.execute(query)
        senses = result.scalars().all()

        return list(senses)

    async def create_sense(self, session: AsyncSession, user: User, data: str) -> Sense:
        sense = Sense(user=user, data=data)

        session.add(sense)

        return sense

    async def get_sense(self, session: AsyncSession, sense_id: uuid.UUID) -> Sense | None:
        query = select(Sense).where(Sense.id == sense_id)

        result = await session.execute(query)
        sense = result.scalar_one_or_none()

        return sense

    async def update_sense(self, session: AsyncSession, sense: Sense, data: str) -> Sense:
        sense.data = data

        session.add(sense)
        
        return sense

    async def delete_sense(self, session: AsyncSession, sense: Sense):
        await session.delete(sense)


def get_service() -> DatabaseService:
    settings = DatabaseSettings()
    return DatabaseService(dsn=str(settings.dsn))
