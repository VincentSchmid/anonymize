"""Transformers-based NLP engine using tabularisai/eu-pii-safeguard model."""

import logging
import os

import spacy

# Import to register the hf_token_pipe component with spaCy
import spacy_huggingface_pipelines  # noqa: F401
from presidio_analyzer.nlp_engine import (
    NerModelConfiguration,
    NlpEngine,
    TransformersNlpEngine,
)

from anonymize_api.core.config import settings

logger = logging.getLogger(__name__)

# Mapping from eu-pii-safeguard model labels to Presidio entity types
# Based on the model's output labels (B-/I- prefixes are handled by Presidio)
LABEL_TO_ENTITY = {
    "ACCOUNTNUMBER": "ACCOUNT_NUMBER",
    "AMOUNT": "AMOUNT",
    "BIC": "BIC",
    "BITCOINADDRESS": "CRYPTO",
    "BUILDINGNUMBER": "BUILDING_NUMBER",
    "CITY": "LOCATION",
    "COMPANYNAME": "ORGANIZATION",
    "COUNTY": "LOCATION",
    "CREDITCARDCVV": "CREDIT_CARD_CVV",
    "CREDITCARDISSUER": "CREDIT_CARD_ISSUER",
    "CREDITCARDNUMBER": "CREDIT_CARD",
    "CURRENCY": "CURRENCY",
    "CURRENCYCODE": "CURRENCY_CODE",
    "CURRENCYNAME": "CURRENCY_NAME",
    "CURRENCYSYMBOL": "CURRENCY_SYMBOL",
    "DATE": "DATE_TIME",
    "DOB": "DATE_TIME",
    "EMAIL": "EMAIL_ADDRESS",
    "ETHEREUMADDRESS": "CRYPTO",
    "EYECOLOR": "PHYSICAL_ATTRIBUTE",
    "FIRSTNAME": "PERSON",
    "GENDER": "GENDER",
    "HEIGHT": "PHYSICAL_ATTRIBUTE",
    "IBAN": "IBAN_CODE",
    "IP": "IP_ADDRESS",
    "IPV4": "IP_ADDRESS",
    "IPV6": "IP_ADDRESS",
    "JOBAREA": "JOB_AREA",
    "JOBTITLE": "JOB_TITLE",
    "JOBTYPE": "JOB_TYPE",
    "LASTNAME": "PERSON",
    "LITECOINADDRESS": "CRYPTO",
    "MAC": "MAC_ADDRESS",
    "MASKEDNUMBER": "MASKED_NUMBER",
    "MIDDLENAME": "PERSON",
    "NAME": "PERSON",
    "NEARBYGPSCOORDINATE": "LOCATION",
    "ORDINALDIRECTION": "LOCATION",
    "PASSWORD": "PASSWORD",
    "PHONEIMEI": "PHONE_IMEI",
    "PHONENUMBER": "PHONE_NUMBER",
    "PIN": "PIN",
    "PREFIX": "TITLE",
    "SECONDARYADDRESS": "LOCATION",
    "SEX": "GENDER",
    "SSN": "US_SSN",
    "STATE": "LOCATION",
    "STREET": "LOCATION",
    "STREETADDRESS": "LOCATION",
    "SUFFIX": "TITLE",
    "TIME": "DATE_TIME",
    "URL": "URL",
    "USERAGENT": "USER_AGENT",
    "USERNAME": "USERNAME",
    "VEHICLEVIN": "VEHICLE_ID",
    "VEHICLEVRM": "VEHICLE_ID",
    "ZIPCODE": "POSTAL_CODE",
}


def create_transformers_engine(language: str = "de") -> NlpEngine:
    """Create a Transformers-based NLP engine using the configured model.

    The model is downloaded on first use (not at build time) and cached
    by HuggingFace's transformers library in ~/.cache/huggingface.

    Args:
        language: The language code (default: German).

    Returns:
        A configured TransformersNlpEngine.
    """
    model_name = settings.transformers_model
    logger.info(f"Creating Transformers engine with model: {model_name}")

    # Disable tokenizers parallelism to avoid fork issues
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    # Ensure the spaCy model is available (needed for tokenization)
    try:
        spacy.load(settings.spacy_model)
    except OSError:
        logger.info(f"Downloading spaCy model: {settings.spacy_model}")
        spacy.cli.download(settings.spacy_model)

    # Configure the NER model with custom label mapping
    ner_config = NerModelConfiguration(
        model_to_presidio_entity_mapping=LABEL_TO_ENTITY,
        aggregation_strategy="simple",
        alignment_mode="expand",
    )

    # Create the TransformersNlpEngine with custom label mapping
    # Uses spaCy for tokenization and transformers model for NER
    # The transformers model will be downloaded automatically by HuggingFace on first use
    engine = TransformersNlpEngine(
        models=[
            {
                "lang_code": language,
                "model_name": {
                    "spacy": settings.spacy_model,
                    "transformers": model_name,
                },
            }
        ],
        ner_model_configuration=ner_config,
    )

    logger.info("Transformers engine created successfully")
    return engine


def get_label_mapping() -> dict[str, str]:
    """Get the label to entity mapping for the transformers model."""
    return LABEL_TO_ENTITY.copy()
