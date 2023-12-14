import fastapi

from . import handlers, senses
from .dependencies import database


router = fastapi.APIRouter(
    dependencies=[fastapi.Depends(database)],
)

router.add_api_route(path="/signup", methods=["POST"], endpoint=handlers.sign_up)
router.add_api_route(path="/signin", methods=["POST"], endpoint=handlers.sign_in)
router.add_api_route(path="/logout", methods=["POST"], endpoint=handlers.logout)
router.add_api_route(path="/options", methods=["GET"], endpoint=handlers.options)
router.include_router(senses.router, prefix="/senses", tags=["Senses"])
