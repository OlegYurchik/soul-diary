import fastapi
from sqlalchemy.exc import IntegrityError

from soul_diary.backend.api.settings import APISettings
from soul_diary.backend.api.dependencies import database, is_auth, settings
from soul_diary.backend.database import DatabaseService
from soul_diary.backend.database.models import Session
from .exceptions import (
    HTTPNotAuthenticated,
    HTTPRegistrationNotSupported,
    HTTPUserAlreadyExists,
)
from .schemas import CredentialsRequest, OptionsResponse, TokenResponse


async def options(settings: APISettings = fastapi.Depends(settings)) -> OptionsResponse:
    return OptionsResponse(registration_enabled=settings.registration_enabled)


async def sign_up(
        data: CredentialsRequest = fastapi.Body(...),
        settings: APISettings = fastapi.Depends(settings),
        database: DatabaseService = fastapi.Depends(database),
) -> TokenResponse:
    if not settings.registration_enabled:
        raise HTTPRegistrationNotSupported()

    try:
        async with database.transaction() as session:
            user = await database.create_user(
                session=session,
                username=data.username,
                password=data.password,
            )
    except IntegrityError:
        raise HTTPUserAlreadyExists()
    user_session = user.sessions[0]

    return TokenResponse(token=user_session.token)


async def sign_in(
        data: CredentialsRequest = fastapi.Body(...),
        database: DatabaseService = fastapi.Depends(database),
) -> TokenResponse:
    async with database.transaction() as session:
        user_session = await database.auth_user(
            session=session,
            username=data.username,
            password=data.password,
        )
    if user_session is None:
        raise HTTPNotAuthenticated()

    return TokenResponse(token=user_session.token)


async def logout(
        database: DatabaseService = fastapi.Depends(database),
        user_session: Session = fastapi.Depends(is_auth),
):
    async with database.transaction() as session:
        await database.logout_user(session=session, user_session=user_session)
