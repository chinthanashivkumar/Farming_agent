"""
Smart Farming Advisor — FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from loguru import logger
import os

from app.core.config import settings
from app.core.database import init_db
from app.rag.vector_store import init_vector_store
from app.api.routes import (
    auth, chat, crops, soil,
    pests, fertilizer, irrigation, market, profile, speech
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🌱 Starting Smart Farming Advisor...")
    await init_db()
    await init_vector_store()
    logger.info("✅ Application ready.")
    yield
    logger.info("🛑 Shutting down Smart Farming Advisor.")


app = FastAPI(
    title="Smart Farming Advisor API",
    description="AI-powered RAG-based agricultural advisory platform for small-scale farmers",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# --- Middleware ---
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes ---
API_PREFIX = "/api/v1"
app.include_router(auth.router,        prefix=f"{API_PREFIX}/auth",       tags=["Authentication"])
app.include_router(chat.router,        prefix=f"{API_PREFIX}/chat",       tags=["AI Chat"])
app.include_router(crops.router,       prefix=f"{API_PREFIX}/crops",      tags=["Crop Recommendation"])
app.include_router(soil.router,        prefix=f"{API_PREFIX}/soil",       tags=["Soil Analysis"])
app.include_router(pests.router,       prefix=f"{API_PREFIX}/pests",      tags=["Pest & Disease"])
app.include_router(fertilizer.router,  prefix=f"{API_PREFIX}/fertilizer", tags=["Fertilizer"])
app.include_router(irrigation.router,  prefix=f"{API_PREFIX}/irrigation", tags=["Irrigation"])
app.include_router(market.router,      prefix=f"{API_PREFIX}/market",     tags=["Market Prices"])
app.include_router(profile.router,     prefix=f"{API_PREFIX}/profile",    tags=["Farmer Profile"])
app.include_router(speech.router,      prefix=f"{API_PREFIX}/speech",     tags=["Speech"])


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Smart Farming Advisor API is running 🌾"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "version": "1.0.0"}
