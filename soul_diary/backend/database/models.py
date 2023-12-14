import random
import string
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    password: Mapped[str] = mapped_column(String(72))

    senses: Mapped[list["Sense"]] = relationship(back_populates="user")
    sessions: Mapped[list["Session"]] = relationship(back_populates="user")

    __table_args__ = (
        Index("users__id_idx", "id", postgresql_using="hash"),
        Index("users__username_idx", "username", postgresql_using="hash"),
    )


class Session(Base):
    __tablename__ = "sessions"

    token: Mapped[str] = mapped_column(
        primary_key=True,
        default=lambda: "".join(random.choice(string.hexdigits) for _ in range(32)),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    user: Mapped[User] = relationship(back_populates="sessions", lazy=False)

    __table_args__ = (
        Index("sessions__token_idx", "token", postgresql_using="hash"),
        Index("sessions__user_id_idx", "user_id", postgresql_using="btree"),
    )


class Sense(Base):
    __tablename__ = "senses"

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    data: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="senses", lazy=False)

    __table_args__ = (
        Index("senses__id_idx", "id", postgresql_using="hash"),
        Index("senses__user_id_idx", "user_id", postgresql_using="btree"),
        Index("senses__created_at_idx", "created_at", postgresql_using="btree"),
    )
