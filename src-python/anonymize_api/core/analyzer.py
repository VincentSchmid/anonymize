"""Presidio analyzer wrapper."""

import logging
from functools import lru_cache
from typing import Optional

from presidio_analyzer import AnalyzerEngine

from anonymize_api.core.config import NlpEngineType, settings
from anonymize_api.core.engines import create_nlp_engine
from anonymize_api.recognizers.swiss import get_swiss_recognizers

logger = logging.getLogger(__name__)

# Track the current engine type for cache invalidation
_current_engine_type: Optional[NlpEngineType] = None


@lru_cache(maxsize=1)
def _create_analyzer(engine_type: NlpEngineType) -> AnalyzerEngine:
    """Internal function to create analyzer with specific engine type."""
    logger.info(f"Creating analyzer with engine: {engine_type.value}")

    # Create the appropriate NLP engine
    nlp_engine = create_nlp_engine(
        engine_type=engine_type,
        language="de",
    )

    # Create analyzer with German support
    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine,
        supported_languages=["de"],
    )

    # Add Swiss-specific regex recognizers (always used regardless of engine)
    for recognizer in get_swiss_recognizers():
        analyzer.registry.add_recognizer(recognizer)
        logger.info(f"Added recognizer: {recognizer.supported_entities}")

    logger.info("Analyzer engine initialized successfully")
    return analyzer


def get_analyzer() -> AnalyzerEngine:
    """Get or create the Presidio analyzer engine.

    The analyzer is cached and reused across requests.
    Uses the configured NLP engine (spaCy or Transformers).
    """
    return _create_analyzer(settings.nlp_engine)


def switch_engine(engine_type: NlpEngineType) -> None:
    """Switch to a different NLP engine.

    This clears the analyzer cache and updates the settings.
    The new analyzer will be created on the next request.
    """
    global _current_engine_type

    if engine_type == settings.nlp_engine:
        logger.info(f"Engine already set to {engine_type.value}, no change needed")
        return

    logger.info(f"Switching NLP engine from {settings.nlp_engine.value} to {engine_type.value}")

    # Update settings
    settings.nlp_engine = engine_type

    # Clear the analyzer cache
    _create_analyzer.cache_clear()

    # Pre-create the new analyzer
    _create_analyzer(engine_type)

    _current_engine_type = engine_type
    logger.info(f"Successfully switched to {engine_type.value} engine")


def get_supported_entities() -> list[dict]:
    """Get list of supported entity types with descriptions."""
    analyzer = get_analyzer()
    recognizers = analyzer.registry.get_recognizers(language="de", all_fields=True)

    entities = {}
    for recognizer in recognizers:
        for entity in recognizer.supported_entities:
            if entity not in entities:
                entities[entity] = {
                    "type": entity,
                    "description": _get_entity_description(entity),
                    "is_swiss": entity.startswith("CH_"),
                }

    return list(entities.values())


def _get_entity_description(entity_type: str) -> str:
    """Get human-readable description for an entity type."""
    descriptions = {
        "PERSON": "Person names",
        "EMAIL_ADDRESS": "Email addresses",
        "PHONE_NUMBER": "Phone numbers",
        "LOCATION": "Locations and addresses",
        "DATE_TIME": "Dates and times",
        "IBAN_CODE": "IBAN bank account numbers",
        "CREDIT_CARD": "Credit card numbers",
        "IP_ADDRESS": "IP addresses",
        "URL": "URLs and web addresses",
        "CH_AHV": "Swiss AHV/AVS social security numbers",
        "CH_PHONE": "Swiss phone numbers (+41, 0XX)",
        "CH_POSTAL_CODE": "Swiss postal codes (PLZ)",
        "CH_IBAN": "Swiss IBAN numbers",
        "NRP": "National registration numbers",
        "MEDICAL_LICENSE": "Medical license numbers",
        "US_SSN": "US Social Security numbers",
        "US_PASSPORT": "US passport numbers",
        "UK_NHS": "UK NHS numbers",
    }
    return descriptions.get(entity_type, f"{entity_type} entities")
