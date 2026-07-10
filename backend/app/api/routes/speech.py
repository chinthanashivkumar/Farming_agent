"""
Speech Routes — STT and TTS
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends
from pydantic import BaseModel
from app.services.speech_service import text_to_speech, speech_to_text
from app.core.security import get_current_user

router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    language: str = "en"


@router.post("/tts")
async def tts(req: TTSRequest, current_user: dict = Depends(get_current_user)):
    """Convert text to speech, returns base64-encoded MP3."""
    audio_b64 = text_to_speech(req.text, req.language)
    return {"audio_base64": audio_b64, "format": "mp3"}


@router.post("/stt")
async def stt(
    language: str = Form("en"),
    audio: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Convert speech audio file to text."""
    audio_bytes = await audio.read()
    text = speech_to_text(audio_bytes, language)
    return {"transcript": text, "language": language}
