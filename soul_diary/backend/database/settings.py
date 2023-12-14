from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(prefix="backend_database_")

    dsn: AnyUrl = "sqlite+aiosqlite:///soul_diary.sqlite3"
