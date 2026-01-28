"""Presidio anonymizer wrapper."""

import logging
from functools import lru_cache
from typing import Literal

from presidio_analyzer import RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

logger = logging.getLogger(__name__)

AnonymizationStyle = Literal["replace", "mask", "hash", "redact"]


@lru_cache(maxsize=1)
def get_anonymizer() -> AnonymizerEngine:
    """Get or create the Presidio anonymizer engine."""
    logger.info("Initializing anonymizer engine")
    return AnonymizerEngine()


def create_operators(
    style: AnonymizationStyle,
    entities: list[str],
) -> dict[str, OperatorConfig]:
    """Create operator configurations for the specified anonymization style.

    Args:
        style: The anonymization style to use
        entities: List of entity types to configure

    Returns:
        Dictionary mapping entity types to operator configurations
    """
    operators = {}

    for entity in entities:
        if style == "replace":
            operators[entity] = OperatorConfig(
                "replace",
                {"new_value": f"<{entity}>"},
            )
        elif style == "mask":
            operators[entity] = OperatorConfig(
                "mask",
                {
                    "type": "mask",
                    "masking_char": "*",
                    "chars_to_mask": 100,
                    "from_end": False,
                },
            )
        elif style == "hash":
            operators[entity] = OperatorConfig(
                "hash",
                {"hash_type": "sha256"},
            )
        elif style == "redact":
            operators[entity] = OperatorConfig("redact")

    return operators


def anonymize_text(
    text: str,
    analyzer_results: list[RecognizerResult],
    style: AnonymizationStyle = "replace",
) -> str:
    """Anonymize text using the specified style.

    Args:
        text: The original text to anonymize
        analyzer_results: Results from the Presidio analyzer
        style: The anonymization style to use

    Returns:
        The anonymized text
    """
    if not analyzer_results:
        return text

    anonymizer = get_anonymizer()

    # Get unique entity types from results
    entity_types = list({result.entity_type for result in analyzer_results})

    # Create operators for the style
    operators = create_operators(style, entity_types)

    result = anonymizer.anonymize(
        text=text,
        analyzer_results=analyzer_results,
        operators=operators,
    )

    return result.text
