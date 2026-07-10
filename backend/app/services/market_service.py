"""
Market Price Service — AgMarkNet / data.gov.in API
"""
import httpx
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import date, timedelta

from app.core.config import settings

MOCK_PRICES = {
    "tomato": [{"market": "Bangalore", "price": 2350, "date": str(date.today()), "unit": "quintal"},
               {"market": "Mysore",    "price": 2200, "date": str(date.today()), "unit": "quintal"}],
    "onion":  [{"market": "Nashik",    "price": 1800, "date": str(date.today()), "unit": "quintal"}],
    "rice":   [{"market": "Local",     "price": 2100, "date": str(date.today()), "unit": "quintal"}],
    "wheat":  [{"market": "Delhi",     "price": 2275, "date": str(date.today()), "unit": "quintal"}],
    "potato": [{"market": "Agra",      "price": 1200, "date": str(date.today()), "unit": "quintal"}],
}


async def get_mandi_prices(
    commodity: str,
    state: Optional[str] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Fetch commodity prices from AgMarkNet API."""
    if not settings.AGMARKNET_API_KEY:
        return _mock_prices(commodity)

    url = settings.AGMARKNET_API_URL
    params = {
        "api-key": settings.AGMARKNET_API_KEY,
        "format": "json",
        "filters[commodity]": commodity.capitalize(),
        "limit": limit,
    }
    if state:
        params["filters[state]"] = state

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        records = data.get("records", [])
        return [
            {
                "market": r.get("market", "Unknown"),
                "state": r.get("state", ""),
                "district": r.get("district", ""),
                "commodity": r.get("commodity", commodity),
                "variety": r.get("variety", "Common"),
                "min_price": float(r.get("min_price", 0)),
                "max_price": float(r.get("max_price", 0)),
                "modal_price": float(r.get("modal_price", 0)),
                "date": r.get("arrival_date", str(date.today())),
                "unit": "quintal",
            }
            for r in records
        ]
    except Exception as e:
        logger.error(f"Market API error: {e}")
        return _mock_prices(commodity)


def _mock_prices(commodity: str) -> List[Dict[str, Any]]:
    """Return realistic mock data when API unavailable."""
    key = commodity.lower()
    return MOCK_PRICES.get(key, [
        {
            "market": "Local Market",
            "state": "Karnataka",
            "district": "Bangalore",
            "commodity": commodity,
            "variety": "Common",
            "min_price": 1500,
            "max_price": 2500,
            "modal_price": 2000,
            "date": str(date.today()),
            "unit": "quintal",
        }
    ])
