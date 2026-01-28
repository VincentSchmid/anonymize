"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Anonymize API"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 14200

    # spaCy model for German
    spacy_model: str = "de_core_news_sm"

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
