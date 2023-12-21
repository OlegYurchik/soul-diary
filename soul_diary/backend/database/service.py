import base64
import pathlib
import struct
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Type

import bcrypt
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from facet import ServiceMixin
from pydantic import BaseModel
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .models import Sense, Session, User
from .settings import DatabaseSettings


class CursorData(BaseModel):
    created_at: datetime
    sense_id: uuid.UUID


class DatabaseService(ServiceMixin):
    ENCODING = "utf-8"

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

    def cursor_encode(self, data: CursorData) -> str:
        datetime_bytes = bytes(struct.pack("d", data.created_at.timestamp()))
        sense_id_bytes = data.sense_id.bytes
        cursor_bytes = datetime_bytes + sense_id_bytes
        return base64.b64encode(cursor_bytes).decode(self.ENCODING)

    def cursor_decode(self, cursor: str) -> CursorData:
        cursor_bytes = base64.b64decode(cursor.encode(self.ENCODING))
        created_at = datetime.fromtimestamp(struct.unpack("d", cursor_bytes[:8])[0])
        sense_id = uuid.UUID(bytes=cursor_bytes[8:])
        return CursorData(created_at=created_at, sense_id=sense_id)

    def get_senses_filters(self, user: User) -> list:
        filters = [Sense.user == user]

        return filters

    async def get_senses_count(self, session: AsyncSession, user: User) -> int:
        filters = self.get_senses_filters(user=user)
        query = select(func.count(Sense.id)).where(*filters)

        count = await session.scalar(query)
        return count

    async def get_senses(
            self,
            session: AsyncSession,
            user: User,
            cursor: str | None = None,
            limit: int = 10,
    ) -> tuple[list[Sense], str | None, str | None]:
        filters = self.get_senses_filters(user=user)
        cursor_data = None if cursor is None else self.cursor_decode(cursor)

        current_filters = filters.copy()
        previous_sense = None
        if cursor_data is not None:
            current_filters.append(or_(
                Sense.created_at > cursor_data.created_at,
                and_(Sense.created_at == cursor_data.created_at, Sense.id > cursor_data.sense_id)
            ))
            query = (
                select(Sense).where(*current_filters)
                .order_by(Sense.created_at.asc()).offset(limit).limit(1)
            )
            result = await session.execute(query)
            previous_sense = result.scalars().first()

        current_filters = filters.copy()
        if cursor_data is not None:
            current_filters.append(or_(
                Sense.created_at < cursor_data.created_at,
                and_(Sense.created_at == cursor_data.created_at, Sense.id <= cursor_data.sense_id),
            ))
        query = (
            select(Sense).where(*current_filters)
            .order_by(Sense.created_at.desc()).limit(limit + 1)
        )
        result = await session.execute(query)
        senses = list(result.scalars().all())

        previous_cursor = None
        if previous_sense is not None:
            previous_cursor_data = CursorData(
                created_at=previous_sense.created_at,
                sense_id=previous_sense.id,
            )
            previous_cursor = self.cursor_encode(data=previous_cursor_data)

        next_cursor = None
        if len(senses) == limit + 1:
            next_cursor_data = CursorData(
                created_at=senses[-1].created_at,
                sense_id=senses[-1].id,
            )
            next_cursor = self.cursor_encode(data=next_cursor_data)

        return senses[:-1], previous_cursor, next_cursor

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
