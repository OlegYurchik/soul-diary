import fastapi

from soul_diary.backend.api.dependencies import database
from soul_diary.backend.database import DatabaseService
from soul_diary.backend.database.models import Sense, Session
from .dependencies import is_auth, sense
from .schemas import (
    CreateSenseRequest,
    SenseListResponse,
    SenseResponse,
    UpdateSenseRequest,
)


async def get_sense_list(
        database: DatabaseService = fastapi.Depends(database),
        user_session: Session = fastapi.Depends(is_auth),
) -> SenseListResponse:
    async with database.transaction() as session:
        senses = await database.get_senses(session=session, user=user_session.user)

    return SenseListResponse(data=senses)


async def create_sense(
        database: DatabaseService = fastapi.Depends(database),
        user_session: Session = fastapi.Depends(is_auth),
        data: CreateSenseRequest = fastapi.Body(),
) -> SenseResponse:
    async with database.transaction() as session:
        sense = await database.create_sense(
            session=session,
            user=user_session.user,
            data=data.data,
        )

    return SenseResponse.model_validate(sense)


async def get_sense(sense: Sense = fastapi.Depends(sense)) -> SenseResponse:
    return SenseResponse.model_validate(sense)


async def update_sense(
        database: DatabaseService = fastapi.Depends(database),
        sense: Sense = fastapi.Depends(sense),
        data: UpdateSenseRequest = fastapi.Body(),
) -> SenseResponse:
    async with database.transaction() as session:
        sense = await database.update_sense(
            session=session,
            sense=sense,
            data=data.data,
        )

    return SenseResponse.model_validate(sense)


async def delete_sense(
        database: DatabaseService = fastapi.Depends(database),
        sense: Sense = fastapi.Depends(sense),
):
    async with database.transaction() as session:
        await database.delete_sense(session=session, sense=sense)
