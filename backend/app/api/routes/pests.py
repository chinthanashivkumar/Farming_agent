"""
Pest & Disease Detection Routes
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from app.rag.rag_pipeline import run_rag
from app.core.security import get_current_user

router = APIRouter()


class PestRequest(BaseModel):
    symptoms: str
    crop: Optional[str] = None
    location: Optional[str] = None


@router.post("/diagnose")
async def diagnose_pest(req: PestRequest, current_user: dict = Depends(get_current_user)):
    query = f"Symptoms: {req.symptoms}"
    if req.crop:
        query = f"Crop: {req.crop}. {query}"
    query += ". Identify the pest or disease and suggest organic and chemical treatment, preventive measures, and safety precautions."

    result = run_rag(query=query, intent="pest_management", farmer_context={"crop": req.crop})
    return {"diagnosis": result["response"], "sources": result["sources"]}


@router.post("/diagnose-image")
async def diagnose_from_image(
    crop: str = Form(...),
    symptoms: str = Form(""),
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Image-based diagnosis — in production, integrate a vision model here.
    For now, we use text-based RAG with the provided crop + symptoms.
    """
    query = f"Crop: {crop}. Visual symptoms described: {symptoms or 'unknown spots, discoloration, wilting'}."
    query += " Identify probable pests or diseases and provide treatment."

    result = run_rag(query=query, intent="pest_management")
    return {
        "diagnosis": result["response"],
        "note": "Image analysis: Integrate a Vision LLM or plant disease CNN for production.",
        "sources": result["sources"],
    }
