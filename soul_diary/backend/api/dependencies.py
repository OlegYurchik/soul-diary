import fastapi
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from soul_diary.backend.api.exceptions import HTTPNotAuthenticated
from soul_diary.backend.api.settings import APISettings
from soul_diary.backend.database import DatabaseService
from soul_diary.backend.database.models import Session


async def database(request: fastapi.Request) -> DatabaseService:
    return request.app.service.database


async def settings(request: fastapi.Request) -> APISettings:
    return request.app.service.settings


async def is_auth(
        database: DatabaseService = fastapi.Depends(database),
        credentials: HTTPAuthorizationCredentials = fastapi.Depends(HTTPBearer()),
) -> Session:
    async with database.transaction() as session:
        user_session = await database.get_user_session(
            session=session,
            token=credentials.credentials,
        )

    if user_session is None:
        raise HTTPNotAuthenticated()

    return user_session
