"""
Speech Service — STT and TTS
"""
import io
import base64
from typing import Optional
from loguru import logger

from app.core.config import settings


def text_to_speech(text: str, language: str = "en") -> str:
    """Convert text to speech, return base64-encoded MP3."""
    LANG_MAP = {"en": "en", "hi": "hi", "kn": "kn", "ta": "ta", "te": "te"}
    tts_lang = LANG_MAP.get(language, "en")

    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return ""


def speech_to_text(audio_bytes: bytes, language: str = "en-IN") -> str:
    """Transcribe audio bytes to text using Google Speech Recognition."""
    LANG_MAP = {
        "en": "en-IN",
        "hi": "hi-IN",
        "kn": "kn-IN",
        "ta": "ta-IN",
        "te": "te-IN",
    }
    recognizer_lang = LANG_MAP.get(language, "en-IN")

    try:
        import speech_recognition as sr
        from pydub import AudioSegment

        # Convert to WAV
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        wav_buf = io.BytesIO()
        audio.export(wav_buf, format="wav")
        wav_buf.seek(0)

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_buf) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data, language=recognizer_lang)
        return text

    except Exception as e:
        logger.error(f"STT error: {e}")
        return ""
