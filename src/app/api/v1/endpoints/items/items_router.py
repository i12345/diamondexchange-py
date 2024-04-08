from fastapi import APIRouter
from .item_note_routes import router as item_note_router
from .item_collection_routes import router as item_collection_router

router = APIRouter()
router.include_router(item_note_router, prefix="/notes", tags=["notes"])
router.include_router(item_collection_router, prefix="/collections", tags=["collections"])
