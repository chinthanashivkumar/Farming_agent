"""
Market Prices Routes
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.services.market_service import get_mandi_prices
from app.core.security import get_current_user

router = APIRouter()


@router.get("/prices")
async def get_prices(
    commodity: str = Query(..., description="Crop name e.g. tomato, onion, wheat"),
    state: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    prices = await get_mandi_prices(commodity, state, limit)
    return {"commodity": commodity, "prices": prices, "count": len(prices)}


@router.get("/commodities")
async def list_commodities():
    return {
        "commodities": [
            "Tomato", "Onion", "Potato", "Rice", "Wheat", "Maize",
            "Soybean", "Cotton", "Sugarcane", "Groundnut", "Mustard",
            "Sunflower", "Chilli", "Turmeric", "Cumin",
        ]
    }
