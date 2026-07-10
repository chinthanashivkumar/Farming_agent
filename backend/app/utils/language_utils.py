"""
Language Detection & Translation Utilities
"""
import re
from loguru import logger

SUPPORTED_LANGS = {"en", "hi", "kn", "ta", "te"}

LANG_PATTERNS = {
    "hi": re.compile(r"[\u0900-\u097F]"),
    "kn": re.compile(r"[\u0C80-\u0CFF]"),
    "ta": re.compile(r"[\u0B80-\u0BFF]"),
    "te": re.compile(r"[\u0C00-\u0C7F]"),
}


def detect_language(text: str) -> str:
    """Simple Unicode-range based language detection."""
    for lang, pattern in LANG_PATTERNS.items():
        if pattern.search(text):
            return lang
    return "en"


def translate_to_english(text: str, source_lang: str) -> str:
    """Translate from source_lang to English using Google Translate (free tier)."""
    if source_lang == "en":
        return text
    try:
        from googletrans import Translator
        translator = Translator()
        result = translator.translate(text, src=source_lang, dest="en")
        return result.text
    except Exception as e:
        logger.warning(f"Translation to English failed: {e}")
        return text  # fallback: return original


def translate_from_english(text: str, target_lang: str) -> str:
    """Translate English response to target_lang."""
    if target_lang == "en":
        return text
    try:
        from googletrans import Translator
        translator = Translator()
        result = translator.translate(text, src="en", dest=target_lang)
        return result.text
    except Exception as e:
        logger.warning(f"Translation from English failed: {e}")
        return text  # fallback: return English
