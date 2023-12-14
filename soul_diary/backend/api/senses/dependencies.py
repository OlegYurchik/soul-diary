import uuid

import fastapi

from soul_diary.backend.api.dependencies import database, is_auth
from soul_diary.backend.api.exceptions import HTTPForbidden, HTTPNotFound
from soul_diary.backend.database import DatabaseService
from soul_diary.backend.database.models import Sense, Session


async def sense(
        database: DatabaseService = fastapi.Depends(database),
        user_session: Session = fastapi.Depends(is_auth),
        sense_id: uuid.UUID = fastapi.Path(),
) -> Sense:
    async with database.transaction() as session:
        sense = await database.get_sense(session=session, sense_id=sense_id)
    
    if sense is None:
        raise HTTPNotFound()
    if sense.user_id != user_session.user_id:
        raise HTTPForbidden()

    return sense
