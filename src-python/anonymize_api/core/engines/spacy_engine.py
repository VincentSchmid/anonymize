"""SpaCy-based NLP engine for Presidio."""

import logging

import spacy
from presidio_analyzer.nlp_engine import NlpEngine, NlpEngineProvider

from anonymize_api.core.config import settings

logger = logging.getLogger(__name__)


def create_spacy_engine(language: str = "de") -> NlpEngine:
    """Create a spaCy-based NLP engine.

    Args:
        language: The language code (default: German).

    Returns:
        A configured spaCy NlpEngine.
    """
    logger.info(f"Creating spaCy engine with model: {settings.spacy_model}")

    # Ensure the spaCy model is available
    try:
        spacy.load(settings.spacy_model)
    except OSError:
        logger.info(f"Downloading spaCy model: {settings.spacy_model}")
        spacy.cli.download(settings.spacy_model)

    # Configure NLP engine
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": language, "model_name": settings.spacy_model},
        ],
    }

    provider = NlpEngineProvider(nlp_configuration=configuration)
    engine = provider.create_engine()

    logger.info("spaCy engine created successfully")
    return engine
