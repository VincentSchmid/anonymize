"""Swiss-specific entity recognizers for Presidio."""

from presidio_analyzer import Pattern, PatternRecognizer


class SwissAHVRecognizer(PatternRecognizer):
    """Recognizer for Swiss AHV/AVS social security numbers.

    Format: 756.XXXX.XXXX.XX (with or without dots)
    The number always starts with 756 (Switzerland country code).
    """

    PATTERNS = [
        Pattern(
            "AHV with dots",
            r"\b756\.\d{4}\.\d{4}\.\d{2}\b",
            0.95,
        ),
        Pattern(
            "AHV without dots",
            r"\b756\d{10}\b",
            0.85,
        ),
        Pattern(
            "AHV with spaces",
            r"\b756\s\d{4}\s\d{4}\s\d{2}\b",
            0.9,
        ),
    ]

    CONTEXT = [
        "ahv",
        "avs",
        "sozialversicherung",
        "sozialversicherungsnummer",
        "versichertennummer",
        "ahv-nummer",
        "avs-nummer",
    ]

    def __init__(self) -> None:
        super().__init__(
            supported_entity="CH_AHV",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="de",
        )


class SwissPhoneRecognizer(PatternRecognizer):
    """Recognizer for Swiss phone numbers.

    Formats:
    - +41 XX XXX XX XX
    - 0XX XXX XX XX
    - +41XXXXXXXXX
    - 0XXXXXXXXX
    """

    PATTERNS = [
        Pattern(
            "Swiss phone +41 with spaces",
            r"\+41\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}\b",
            0.9,
        ),
        Pattern(
            "Swiss phone 0 with spaces",
            r"\b0\d{2}\s?\d{3}\s?\d{2}\s?\d{2}\b",
            0.7,
        ),
        Pattern(
            "Swiss phone +41 compact",
            r"\+41\d{9}\b",
            0.85,
        ),
        Pattern(
            "Swiss phone 0 compact",
            r"\b0\d{9}\b",
            0.6,
        ),
    ]

    CONTEXT = [
        "telefon",
        "tel",
        "phone",
        "handy",
        "mobile",
        "natel",
        "festnetz",
        "anrufen",
        "kontakt",
    ]

    def __init__(self) -> None:
        super().__init__(
            supported_entity="CH_PHONE",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="de",
        )


class SwissPostalCodeRecognizer(PatternRecognizer):
    """Recognizer for Swiss postal codes (PLZ).

    Format: 4 digits, first digit 1-9 (no leading zero)
    Range: 1000-9999
    """

    PATTERNS = [
        Pattern(
            "Swiss PLZ",
            r"\b[1-9]\d{3}\b",
            0.3,  # Low base score, needs context
        ),
    ]

    CONTEXT = [
        "plz",
        "postleitzahl",
        "postal",
        "zip",
        "ort",
        "stadt",
        "gemeinde",
        "wohnort",
        "adresse",
    ]

    def __init__(self) -> None:
        super().__init__(
            supported_entity="CH_POSTAL_CODE",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="de",
        )


class SwissIBANRecognizer(PatternRecognizer):
    """Recognizer for Swiss IBAN numbers.

    Format: CH followed by 2 check digits and 17 alphanumeric characters
    Example: CH93 0076 2011 6238 5295 7
    """

    PATTERNS = [
        Pattern(
            "Swiss IBAN with spaces",
            r"\bCH\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d\b",
            0.95,
        ),
        Pattern(
            "Swiss IBAN compact",
            r"\bCH\d{2}[A-Z0-9]{17}\b",
            0.9,
        ),
        Pattern(
            "Swiss IBAN alphanumeric with spaces",
            r"\bCH\d{2}\s?[A-Z0-9]{4}\s?[A-Z0-9]{4}\s?[A-Z0-9]{4}\s?[A-Z0-9]{4}\s?[A-Z0-9]{1}\b",
            0.95,
        ),
    ]

    CONTEXT = [
        "iban",
        "konto",
        "bankkonto",
        "kontonummer",
        "bankverbindung",
        "zahlung",
        "überweisung",
    ]

    def __init__(self) -> None:
        super().__init__(
            supported_entity="CH_IBAN",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="de",
        )


def get_swiss_recognizers() -> list[PatternRecognizer]:
    """Get all Swiss-specific recognizers."""
    return [
        SwissAHVRecognizer(),
        SwissPhoneRecognizer(),
        SwissPostalCodeRecognizer(),
        SwissIBANRecognizer(),
    ]
