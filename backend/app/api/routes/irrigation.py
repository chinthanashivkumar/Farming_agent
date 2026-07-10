"""
Irrigation Advisory Routes
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.rag.rag_pipeline import run_rag
from app.core.security import get_current_user

router = APIRouter()


class IrrigationRequest(BaseModel):
    crop: str
    growth_stage: Optional[str] = None
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None  # drip / flood / sprinkler
    soil_moisture_percent: Optional[float] = None
    rainfall_expected: Optional[bool] = False
    temperature_c: Optional[float] = None


@router.post("/schedule")
async def irrigation_schedule(req: IrrigationRequest, current_user: dict = Depends(get_current_user)):
    query = f"Irrigation schedule for {req.crop}"
    if req.growth_stage:
        query += f" at {req.growth_stage} stage"
    if req.soil_type:
        query += f" on {req.soil_type} soil"
    if req.irrigation_type:
        query += f" using {req.irrigation_type} irrigation"
    if req.soil_moisture_percent is not None:
        query += f". Current soil moisture: {req.soil_moisture_percent}%"
    if req.rainfall_expected:
        query += ". Rain is expected in 2 days."
    if req.temperature_c:
        query += f". Temperature: {req.temperature_c}°C"
    query += ". Provide a detailed irrigation schedule with water quantity and frequency."

    result = run_rag(query=query, intent="irrigation", farmer_context=req.dict())
    return {"schedule": result["response"], "sources": result["sources"]}
