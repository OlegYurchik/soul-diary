import fastapi

from . import handlers

router = fastapi.APIRouter()

router.add_api_route(path="/", methods=["GET"], endpoint=handlers.get_sense_list)
router.add_api_route(path="/", methods=["POST"], endpoint=handlers.create_sense)
router.add_api_route(path="/{sense_id}", methods=["GET"], endpoint=handlers.get_sense)
router.add_api_route(path="/{sense_id}", methods=["POST"], endpoint=handlers.update_sense)
router.add_api_route(path="/{sense_id}", methods=["DELETE"], endpoint=handlers.delete_sense)
