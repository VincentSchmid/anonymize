"""Application configuration."""

from enum import Enum

from pydantic_settings import BaseSettings


class NlpEngineType(str, Enum):
    """Supported NLP engine types."""

    SPACY = "spacy"
    TRANSFORMERS = "transformers"


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Anonymize API"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 14200

    # NLP engine type: "spacy" or "transformers"
    # Default to spacy for better compatibility with bundled app
    nlp_engine: NlpEngineType = NlpEngineType.SPACY

    # spaCy model for German (used by spacy engine and for tokenization in transformers)
    spacy_model: str = "de_core_news_sm"

    # Transformers model for NER
    transformers_model: str = "tabularisai/eu-pii-safeguard"

    # Default enabled entity types
    default_entities: list[str] = [
        "PERSON",
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "LOCATION",
        "DATE_TIME",
        "IBAN_CODE",
        "CH_AHV",
        "CH_PHONE",
        "CH_POSTAL_CODE",
        "CH_IBAN",
    ]

    class Config:
        env_prefix = "ANONYMIZE_"


settings = Settings()
