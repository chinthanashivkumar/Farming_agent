"""
Intent Detection Utility
"""
import re
from typing import Optional

INTENT_KEYWORDS = {
    "crop_recommendation": [
        "crop", "grow", "plant", "sow", "cultivate", "which crop", "best crop",
        "kharif", "rabi", "monsoon", "season", "yield", "harvest crop",
    ],
    "soil_analysis": [
        "soil", "ph", "nitrogen", "phosphorus", "potassium", "organic carbon",
        "nutrient", "loam", "clay", "sandy", "soil test", "soil health",
    ],
    "pest_management": [
        "pest", "disease", "insect", "bug", "fungus", "rot", "blight", "spot",
        "wilt", "aphid", "worm", "larvae", "caterpillar", "virus", "bacteria",
        "spray", "pesticide", "fungicide", "herbicide", "control", "treatment",
    ],
    "fertilizer": [
        "fertilizer", "urea", "dap", "npk", "compost", "manure", "nutrient",
        "dose", "application", "top dress", "basal", "micronutrient",
    ],
    "irrigation": [
        "water", "irrigat", "drip", "sprinkler", "flood", "moisture",
        "schedule", "how much water", "irrigation plan",
    ],
    "market_prices": [
        "price", "mandi", "market", "rate", "sell", "profit", "income",
        "tomato price", "onion price", "commodity", "quintal", "kg price",
    ],
}


def detect_intent(query: str) -> Optional[str]:
    """Detect the query intent based on keyword matching."""
    query_lower = query.lower()
    scores = {}

    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in query_lower)
        if score > 0:
            scores[intent] = score

    if not scores:
        return "general"

    return max(scores, key=scores.get)
