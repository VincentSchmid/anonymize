"""FastAPI application entry point."""

import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from anonymize_api import __version__
from anonymize_api.api.routes import router
from anonymize_api.core.analyzer import get_analyzer
from anonymize_api.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - load models on startup."""
    logger.info("Starting Anonymize API...")
    logger.info(f"Version: {__version__}")
    logger.info(f"Host: {settings.host}:{settings.port}")

    # Pre-load the analyzer and models
    logger.info("Loading spaCy model and initializing analyzer...")
    try:
        get_analyzer()
        logger.info("Analyzer initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize analyzer: {e}")
        raise

    yield

    logger.info("Shutting down Anonymize API...")


app = FastAPI(
    title=settings.app_name,
    description="Swiss document anonymization API using Microsoft Presidio",
    version=__version__,
    lifespan=lifespan,
)

# Configure CORS for Tauri frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:1420",  # Vite dev server
        "tauri://localhost",  # Tauri app (macOS)
        "https://tauri.localhost",  # Tauri app (macOS alternative)
        "http://tauri.localhost",  # Tauri app (Windows)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


def main():
    """Run the API server."""
    # Use app object directly instead of string import for PyInstaller compatibility
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
