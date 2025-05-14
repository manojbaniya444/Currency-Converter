"""Main application module."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import converter
from app.core.config import settings

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Context manager in app."""
    logger.info(f"Starting {settings.PROJECT_NAME} in {settings.DEV_MODE} mode")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A microservice for currency conversion",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(converter.converter_router)


@app.get("/health")
async def health() -> dict:
    """Server response checking."""
    return {
        "message": "response from the server",
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.DEV_MODE,
    }
