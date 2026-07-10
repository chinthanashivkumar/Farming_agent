"""
Language Detection & Translation Utilities
Uses deep_translator (pip install deep_translator) — more reliable than googletrans.
"""
import re
from loguru import logger

SUPPORTED_LANGS = {"en", "hi", "kn"}

LANG_PATTERNS = {
    "hi": re.compile(r"[\u0900-\u097F]"),
    "kn": re.compile(r"[\u0C80-\u0CFF]"),
}

# ASCII/Latin characters — used to detect English-looking text
_ASCII_PATTERN = re.compile(r"[A-Za-z]")


def detect_language(text: str) -> str:
    """Simple Unicode-range based language detection."""
    for lang, pattern in LANG_PATTERNS.items():
        if pattern.search(text):
            return lang
    return "en"


def looks_english(text: str) -> bool:
    """Return True if the response looks like English (mostly ASCII/Latin chars)."""
    if not text:
        return True
    ascii_chars = len(_ASCII_PATTERN.findall(text))
    return (ascii_chars / max(len(text), 1)) > 0.5


def _translator():
    """Return a GoogleTranslator instance (deep_translator)."""
    from deep_translator import GoogleTranslator
    return GoogleTranslator


def translate_to_english(text: str, source_lang: str) -> str:
    """Translate from source_lang to English."""
    if source_lang == "en":
        return text
    try:
        Translator = _translator()
        result = Translator(source=source_lang, target="en").translate(text)
        return result or text
    except Exception as e:
        logger.warning(f"Translation to English failed: {e}")
        return text  # fallback: return original


def translate_from_english(text: str, target_lang: str) -> str:
    """Translate English response to target_lang."""
    if target_lang == "en":
        return text
    try:
        Translator = _translator()
        result = Translator(source="en", target=target_lang).translate(text)
        return result or text
    except Exception as e:
        logger.warning(f"Translation from English failed: {e}")
        return text  # fallback: return English
