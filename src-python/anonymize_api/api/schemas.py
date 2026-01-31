"""Pydantic models for API requests and responses."""

from typing import Literal

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Request to analyze text for PII entities."""

    text: str = Field(..., min_length=1, description="Text to analyze")
    enabled_entities: list[str] | None = Field(
        None,
        description="Entity types to detect. If None, uses default entities.",
    )
    score_threshold: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score for entity detection",
    )


class AnonymizeRequest(BaseModel):
    """Request to anonymize text."""

    text: str = Field(..., min_length=1, description="Text to anonymize")
    enabled_entities: list[str] | None = Field(
        None,
        description="Entity types to anonymize. If None, uses default entities.",
    )
    anonymization_style: Literal["replace", "mask", "hash", "redact"] = Field(
        "replace",
        description="Style of anonymization to apply",
    )
    score_threshold: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score for entity detection",
    )


class DetectedEntity(BaseModel):
    """A detected PII entity."""

    entity_type: str = Field(..., description="Type of entity detected")
    text: str = Field(..., description="The detected text")
    start: int = Field(..., description="Start position in original text")
    end: int = Field(..., description="End position in original text")
    score: float = Field(..., description="Confidence score (0-1)")


class AnalyzeResponse(BaseModel):
    """Response from text analysis."""

    text: str = Field(..., description="The analyzed text")
    entities: list[DetectedEntity] = Field(
        default_factory=list,
        description="Detected entities",
    )


class AnonymizeResponse(BaseModel):
    """Response from text anonymization."""

    original_text: str = Field(..., description="The original input text")
    anonymized_text: str = Field(..., description="The anonymized output text")
    entities: list[DetectedEntity] = Field(
        default_factory=list,
        description="Entities that were anonymized",
    )
    anonymization_style: str = Field(..., description="Style used for anonymization")


class EntityInfo(BaseModel):
    """Information about a supported entity type."""

    type: str = Field(..., description="Entity type identifier")
    description: str = Field(..., description="Human-readable description")
    is_swiss: bool = Field(..., description="Whether this is a Swiss-specific entity")


class EntitiesResponse(BaseModel):
    """Response listing available entity types."""

    entities: list[EntityInfo] = Field(..., description="Available entity types")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether the spaCy model is loaded")
    version: str = Field(..., description="API version")


class ConfigResponse(BaseModel):
    """Current configuration response."""

    default_entities: list[str] = Field(..., description="Default enabled entities")
    spacy_model: str = Field(..., description="spaCy model name")


class ConfigUpdate(BaseModel):
    """Request to update configuration."""

    default_entities: list[str] | None = Field(
        None,
        description="New default entities list",
    )


class NlpEngineInfo(BaseModel):
    """Information about an NLP engine."""

    id: str = Field(..., description="Engine identifier (spacy or transformers)")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Description of the engine")
    model: str = Field(..., description="Model being used")


class NlpEngineResponse(BaseModel):
    """Response with current NLP engine and available engines."""

    current: str = Field(..., description="Currently active engine ID")
    engines: list[NlpEngineInfo] = Field(..., description="Available engines")


class NlpEngineUpdate(BaseModel):
    """Request to change the NLP engine."""

    engine: str = Field(..., description="Engine ID to switch to (spacy or transformers)")
