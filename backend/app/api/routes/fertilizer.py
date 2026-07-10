"""
Fertilizer Recommendation Routes
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.rag.rag_pipeline import run_rag
from app.core.security import get_current_user

router = APIRouter()


class FertilizerRequest(BaseModel):
    crop: str
    growth_stage: Optional[str] = None    # "sowing" | "vegetative" | "flowering" | "fruiting"
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    soil_type: Optional[str] = None
    area_acres: Optional[float] = 1.0


@router.post("/recommend")
async def recommend_fertilizer(req: FertilizerRequest, current_user: dict = Depends(get_current_user)):
    query = f"Fertilizer recommendation for {req.crop}"
    if req.growth_stage:
        query += f" at {req.growth_stage} stage"
    if req.nitrogen:
        query += f". Soil N={req.nitrogen}, P={req.phosphorus}, K={req.potassium}"
    if req.area_acres:
        query += f". Farm area: {req.area_acres} acres"
    query += ". Provide quantity, application method, and timing."

    result = run_rag(query=query, intent="fertilizer", farmer_context=req.dict())
    return {"recommendation": result["response"], "sources": result["sources"]}
