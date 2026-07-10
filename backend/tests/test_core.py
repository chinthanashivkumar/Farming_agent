"""
Backend Tests — Core RAG & API tests
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register
        reg = await client.post("/api/v1/auth/register", json={
            "name": "Test Farmer",
            "email": "test@farm.com",
            "password": "testpass123",
            "preferred_language": "en",
        })
        assert reg.status_code in (201, 400)  # 400 if already exists

        # Login
        login = await client.post("/api/v1/auth/login", data={
            "username": "test@farm.com",
            "password": "testpass123",
        })
        assert login.status_code == 200
        assert "access_token" in login.json()


def test_intent_detection():
    from app.utils.intent_detector import detect_intent
    assert detect_intent("what crop should I grow this monsoon") == "crop_recommendation"
    assert detect_intent("pest on my tomato plants, yellow spots") == "pest_management"
    assert detect_intent("today's tomato mandi price in Bangalore") == "market_prices"
    assert detect_intent("how much urea for wheat per acre") == "fertilizer"


def test_language_detection():
    from app.utils.language_utils import detect_language
    assert detect_language("What crop should I grow?") == "en"
    assert detect_language("मैं कौन सी फसल उगाऊं?") == "hi"
    assert detect_language("ನಾನು ಯಾವ ಬೆಳೆ ಬೆಳೆಯಬೇಕು?") == "kn"


def test_chunk_text():
    from app.rag.document_loader import chunk_text
    text = "word " * 600
    chunks = chunk_text(text, chunk_size=100, overlap=10)
    assert len(chunks) > 1
    assert all(len(c.split()) <= 100 for c in chunks)
