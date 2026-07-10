"""
Crop Recommendation Routes
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.rag.rag_pipeline import run_rag
from app.core.security import get_current_user

router = APIRouter()


class CropRequest(BaseModel):
    season: str               # "kharif" | "rabi" | "summer"
    soil_type: Optional[str] = None
    state: Optional[str] = None
    rainfall_mm: Optional[float] = None
    temperature_c: Optional[float] = None
    water_availability: Optional[str] = None  # "good" | "moderate" | "scarce"
    farm_size_acres: Optional[float] = None


@router.post("/recommend")
async def recommend_crops(
    req: CropRequest,
    current_user: dict = Depends(get_current_user),
):
    query = (
        f"Recommend crops for {req.season} season"
        + (f" in {req.state}" if req.state else "")
        + (f" with {req.soil_type} soil" if req.soil_type else "")
        + (f", rainfall {req.rainfall_mm}mm" if req.rainfall_mm else "")
        + (f", temperature {req.temperature_c}°C" if req.temperature_c else "")
        + (f", water availability: {req.water_availability}" if req.water_availability else "")
    )

    context = {
        "season": req.season,
        "state": req.state,
        "soil_type": req.soil_type,
        "rainfall_mm": req.rainfall_mm,
    }

    result = run_rag(query=query, intent="crop_recommendation", farmer_context=context)
    return {"recommendation": result["response"], "sources": result["sources"]}


@router.get("/seasons")
async def get_seasons():
    return {
        "seasons": [
            {"id": "kharif", "name": "Kharif (Jun–Oct)", "crops": ["Rice", "Maize", "Soybean", "Cotton", "Groundnut"]},
            {"id": "rabi",   "name": "Rabi (Nov–Mar)",   "crops": ["Wheat", "Barley", "Mustard", "Peas", "Gram"]},
            {"id": "summer", "name": "Summer (Apr–Jun)",  "crops": ["Sunflower", "Moong", "Watermelon", "Cucumber"]},
        ]
    }
