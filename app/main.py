import logging
from logging import config as logging_config

import uvicorn as uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from app.api.routers import api_router
from app.core.config import settings
from app.core.logger import LOGGING
from app.events import on_shutdown, on_startup

logging_config.dictConfig(LOGGING)

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    on_startup=on_startup,
    on_shutdown=on_shutdown,
)


# Include API router
app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.PROJECT_HOST,
        port=settings.PROJECT_PORT,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=settings.DEBUG,
    )
