from fastapi import APIRouter
from .endpoints.item_note_routes import router as item_note_router
from .endpoints.item_collection_routers import router as item_collection_router

router = APIRouter()
router.include_router(item_note_router, prefix="/notes", tags=["notes"])
router.include_router(item_collection_router, prefix="/collections", tags=["collections"])
