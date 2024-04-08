from fastapi import APIRouter
from .endpoints.items.items_router import router as items_router

router = APIRouter()
router.include_router(items_router, prefix="/items", tags=["items"])