"""API route handlers."""

import logging

from fastapi import APIRouter, HTTPException

from anonymize_api import __version__
from anonymize_api.api.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    AnonymizeRequest,
    AnonymizeResponse,
    ConfigResponse,
    ConfigUpdate,
    DetectedEntity,
    EntitiesResponse,
    EntityInfo,
    HealthResponse,
)
from anonymize_api.core.analyzer import get_analyzer, get_supported_entities
from anonymize_api.core.anonymizer import anonymize_text
from anonymize_api.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check if the service is healthy and the model is loaded."""
    try:
        # This will load the model if not already loaded
        analyzer = get_analyzer()
        model_loaded = analyzer is not None
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        model_loaded = False

    return HealthResponse(
        status="healthy" if model_loaded else "unhealthy",
        model_loaded=model_loaded,
        version=__version__,
    )


@router.get("/entities", response_model=EntitiesResponse)
async def list_entities() -> EntitiesResponse:
    """List all available entity types."""
    entities = get_supported_entities()
    return EntitiesResponse(
        entities=[EntityInfo(**e) for e in entities],
    )


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze text and return detected PII entities."""
    analyzer = get_analyzer()

    # Determine which entities to look for
    entities_to_analyze = request.enabled_entities or settings.default_entities

    try:
        results = analyzer.analyze(
            text=request.text,
            entities=entities_to_analyze,
            language="de",
            score_threshold=request.score_threshold,
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Convert results to response format
    detected_entities = [
        DetectedEntity(
            entity_type=result.entity_type,
            text=request.text[result.start : result.end],
            start=result.start,
            end=result.end,
            score=result.score,
        )
        for result in results
    ]

    return AnalyzeResponse(
        text=request.text,
        entities=detected_entities,
    )


@router.post("/anonymize", response_model=AnonymizeResponse)
async def anonymize(request: AnonymizeRequest) -> AnonymizeResponse:
    """Analyze and anonymize text."""
    analyzer = get_analyzer()

    # Determine which entities to look for
    entities_to_analyze = request.enabled_entities or settings.default_entities

    try:
        results = analyzer.analyze(
            text=request.text,
            entities=entities_to_analyze,
            language="de",
            score_threshold=request.score_threshold,
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Convert results to response format before anonymization
    detected_entities = [
        DetectedEntity(
            entity_type=result.entity_type,
            text=request.text[result.start : result.end],
            start=result.start,
            end=result.end,
            score=result.score,
        )
        for result in results
    ]

    # Anonymize the text
    try:
        anonymized = anonymize_text(
            text=request.text,
            analyzer_results=results,
            style=request.anonymization_style,
        )
    except Exception as e:
        logger.error(f"Anonymization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Anonymization failed: {str(e)}")

    return AnonymizeResponse(
        original_text=request.text,
        anonymized_text=anonymized,
        entities=detected_entities,
        anonymization_style=request.anonymization_style,
    )


@router.get("/config", response_model=ConfigResponse)
async def get_config() -> ConfigResponse:
    """Get current configuration."""
    return ConfigResponse(
        default_entities=settings.default_entities,
        spacy_model=settings.spacy_model,
    )


@router.put("/config", response_model=ConfigResponse)
async def update_config(update: ConfigUpdate) -> ConfigResponse:
    """Update configuration.

    Note: Changes are not persisted across restarts.
    """
    if update.default_entities is not None:
        settings.default_entities = update.default_entities

    return ConfigResponse(
        default_entities=settings.default_entities,
        spacy_model=settings.spacy_model,
    )
