"""Base NLP engine abstraction."""

import logging
from typing import TYPE_CHECKING

from anonymize_api.core.config import NlpEngineType

if TYPE_CHECKING:
    from presidio_analyzer.nlp_engine import NlpEngine

logger = logging.getLogger(__name__)


def create_nlp_engine(engine_type: NlpEngineType, language: str = "de") -> "NlpEngine":
    """Factory function to create the appropriate NLP engine.

    Args:
        engine_type: The type of NLP engine to create.
        language: The language code for the engine.

    Returns:
        A configured NlpEngine instance.
    """
    if engine_type == NlpEngineType.SPACY:
        from anonymize_api.core.engines.spacy_engine import create_spacy_engine

        return create_spacy_engine(language)
    elif engine_type == NlpEngineType.TRANSFORMERS:
        from anonymize_api.core.engines.transformers_engine import (
            create_transformers_engine,
        )

        return create_transformers_engine(language)
    else:
        raise ValueError(f"Unknown NLP engine type: {engine_type}")
