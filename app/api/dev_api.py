from fastapi import APIRouter
from app.api.routes import router as main_router


dev_api_router = APIRouter(prefix="/dev-api") #all routes are protected
dev_api_router.include_router(main_router)