from fastapi import FastAPI
from app.api.routes import router as api_router
from app.api.dev_api import dev_api_router as api_dev

app = FastAPI(title="Abide API", version="1.0")
app.include_router(api_router)
app.include_router(api_dev)
