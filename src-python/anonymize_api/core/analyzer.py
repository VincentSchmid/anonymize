"""Presidio analyzer wrapper."""

import logging
from functools import lru_cache

import spacy
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

from anonymize_api.core.config import settings
from anonymize_api.recognizers.swiss import get_swiss_recognizers

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_analyzer() -> AnalyzerEngine:
    """Get or create the Presidio analyzer engine.

    The analyzer is cached and reused across requests.
    """
    logger.info(f"Loading spaCy model: {settings.spacy_model}")

    # Ensure the spaCy model is available
    try:
        spacy.load(settings.spacy_model)
    except OSError:
        logger.info(f"Downloading spaCy model: {settings.spacy_model}")
        spacy.cli.download(settings.spacy_model)

    # Configure NLP engine for German
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": "de", "model_name": settings.spacy_model},
        ],
    }

    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()

    # Create analyzer with German support
    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine,
        supported_languages=["de"],
    )

    # Add Swiss-specific recognizers
    for recognizer in get_swiss_recognizers():
        analyzer.registry.add_recognizer(recognizer)
        logger.info(f"Added recognizer: {recognizer.supported_entities}")

    logger.info("Analyzer engine initialized successfully")
    return analyzer


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
