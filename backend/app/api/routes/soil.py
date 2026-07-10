"""
Soil Analysis Routes
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.rag.rag_pipeline import run_rag
from app.core.security import get_current_user

router = APIRouter()


class SoilAnalysisRequest(BaseModel):
    ph: Optional[float] = None
    nitrogen: Optional[float] = None      # kg/ha
    phosphorus: Optional[float] = None    # kg/ha
    potassium: Optional[float] = None     # kg/ha
    organic_carbon: Optional[float] = None  # %
    soil_type: Optional[str] = None
    state: Optional[str] = None
    season: Optional[str] = None


@router.post("/analyze")
async def analyze_soil(req: SoilAnalysisRequest, current_user: dict = Depends(get_current_user)):
    parts = ["Analyze this soil data:"]
    if req.ph:            parts.append(f"pH={req.ph}")
    if req.nitrogen:      parts.append(f"N={req.nitrogen}kg/ha")
    if req.phosphorus:    parts.append(f"P={req.phosphorus}kg/ha")
    if req.potassium:     parts.append(f"K={req.potassium}kg/ha")
    if req.organic_carbon: parts.append(f"OC={req.organic_carbon}%")
    if req.soil_type:     parts.append(f"Type={req.soil_type}")

    query = " ".join(parts)
    query += ". Suggest suitable crops, required fertilizers, and soil improvement methods."

    result = run_rag(query=query, intent="soil_analysis", farmer_context=req.dict())
    return {
        "analysis": result["response"],
        "soil_data": req.dict(exclude_none=True),
        "sources": result["sources"],
    }
