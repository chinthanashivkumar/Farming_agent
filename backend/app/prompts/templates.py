"""
Prompt Templates for IBM Granite LLM — Optimized for Indian Farmers
"""
from typing import List, Dict, Any, Optional


SYSTEM_INSTRUCTION = """You are a Smart Farming Advisor AI assistant designed specifically to help Indian farmers.

Your Role:
- Provide accurate, practical, and easy-to-understand agricultural advice tailored to Indian farming conditions
- Support regional crops including rice/paddy, wheat, maize, sugarcane, cotton, banana, coconut, arecanut, coffee, pepper, turmeric, ginger, onion, chilli, groundnut, soybean, pulses, and vegetables
- Consider Indian soil types (Black cotton/Vertisols, Red laterite, Alluvial, Sandy loam), seasons (Kharif, Rabi, Summer/Zaid), and climate zones
- Recommend both organic and chemical solutions based on farmer preferences
- Use simple language avoiding complex jargon

Guidelines:
- Provide actionable advice with specific quantities, timings, and methods
- Include safety precautions when recommending chemicals
- Use Indian units: kg/ha, acres, quintals, degrees C, mm rainfall
- Reference Indian agricultural institutions (ICAR, State Agriculture Universities, KVK)
"""

INTENT_PROMPTS = {
    "crop_recommendation": "Recommend the best crops considering the farmer's soil type, water availability, season (Kharif/Rabi/Summer), and region in India.",
    "soil_analysis": "Analyze the soil data (pH, NPK, organic carbon, soil type) and suggest suitable crops, fertilizer corrections, and soil health improvement methods.",
    "pest_management": "Identify the pest or disease based on symptoms. Provide: pest name, organic treatment, chemical treatment with dosage, preventive measures, safety precautions.",
    "fertilizer": "Recommend fertilizer type, quantity (kg/ha or per acre), and application schedule for the given crop and growth stage.",
    "irrigation": "Suggest an optimal irrigation schedule considering crop type, growth stage, irrigation method, soil type, and season.",
    "market_prices": "Provide market price information for the crop, mention major mandis, best selling time, and value addition opportunities.",
    "general": "Answer the farmer's question using the retrieved agricultural knowledge. Be helpful, practical, and specific to Indian farming.",
}

# Language config: (language name in English, instruction in target language, instruction in English)
LANGUAGE_CONFIG = {
    "en": {
        "name": "English",
        "native_name": "English",
        "instruction": "You MUST write your entire answer in English only.",
    },
    "hi": {
        "name": "Hindi",
        "native_name": "हिंदी",
        "instruction": (
            "आपको अपना पूरा उत्तर केवल हिंदी में लिखना है। "
            "हर शब्द देवनागरी लिपि में होना चाहिए। "
            "अंग्रेजी में एक भी शब्द मत लिखो। "
            "WRITE EVERY WORD IN HINDI DEVANAGARI SCRIPT ONLY."
        ),
    },
    "kn": {
        "name": "Kannada",
        "native_name": "ಕನ್ನಡ",
        "instruction": (
            "ನೀವು ನಿಮ್ಮ ಸಂಪೂರ್ಣ ಉತ್ತರವನ್ನು ಕೇವಲ ಕನ್ನಡ ಭಾಷೆಯಲ್ಲಿ ಬರೆಯಬೇಕು. "
            "ಪ್ರತಿ ಪದವೂ ಕನ್ನಡ ಲಿಪಿಯಲ್ಲಿ ಇರಬೇಕು. "
            "ಆಂಗ್ಲ ಭಾಷೆಯಲ್ಲಿ ಒಂದು ಪದವೂ ಬರೆಯಬೇಡಿ. "
            "WRITE EVERY WORD IN KANNADA SCRIPT ONLY."
        ),
    },
}


def format_retrieved_docs(docs: List[Dict[str, Any]]) -> str:
    if not docs:
        return "No specific knowledge retrieved. Provide general agricultural guidance based on standard practices for Indian conditions."
    lines = []
    for i, doc in enumerate(docs, 1):
        source = doc["metadata"].get("source", "Unknown Source")
        category = doc["metadata"].get("category", "general")
        lines.append(f"[Source {i} | {source} | Category: {category}]\n{doc['content']}")
    return "\n\n---\n\n".join(lines)


def format_farmer_context(ctx: Dict[str, Any]) -> str:
    if not ctx:
        return "No farmer profile data available."
    parts = []
    if ctx.get("location"):   parts.append(f"Location: {ctx['location']}")
    if ctx.get("state"):      parts.append(f"State: {ctx['state']}")
    if ctx.get("district"):   parts.append(f"District: {ctx['district']}")
    if ctx.get("soil_type"):  parts.append(f"Soil Type: {ctx['soil_type']}")
    if ctx.get("farm_size_acres"): parts.append(f"Farm Size: {ctx['farm_size_acres']} acres")
    if ctx.get("primary_crops"):   parts.append(f"Current Crops: {', '.join(ctx['primary_crops'])}")
    if ctx.get("irrigation_type"): parts.append(f"Irrigation: {ctx['irrigation_type']}")
    return " | ".join(parts) if parts else "No detailed farmer context provided."


def build_prompt(
    query: str,
    retrieved_docs: List[Dict[str, Any]],
    intent: str = "general",
    farmer_context: Optional[Dict[str, Any]] = None,
    language: str = "en",
    original_query: Optional[str] = None,
) -> str:
    """Construct full LLM prompt for IBM Granite."""
    lang_cfg = LANGUAGE_CONFIG.get(language or "en", LANGUAGE_CONFIG["en"])
    lang_name    = lang_cfg["name"]
    native_name  = lang_cfg["native_name"]
    lang_instr   = lang_cfg["instruction"]

    task_instruction = INTENT_PROMPTS.get(intent or "general", INTENT_PROMPTS["general"])
    context_str  = format_retrieved_docs(retrieved_docs)
    farmer_str   = format_farmer_context(farmer_context or {})

    # Show original non-English question so the LLM sees the actual script
    if original_query and original_query.strip() != query.strip():
        question_section = (
            f"Original question in {native_name}:\n{original_query}\n\n"
            f"English translation (for context only):\n{query}"
        )
    else:
        question_section = query

    prompt = (
        f"{SYSTEM_INSTRUCTION}\n"
        f"=================================================================\n"
        f"LANGUAGE RULE — THIS IS THE MOST IMPORTANT INSTRUCTION:\n"
        f"{lang_instr}\n"
        f"=================================================================\n\n"
        f"FARMER PROFILE:\n{farmer_str}\n\n"
        f"TASK: {task_instruction}\n\n"
        f"AGRICULTURAL KNOWLEDGE (use as primary reference):\n{context_str}\n\n"
        f"=================================================================\n"
        f"FARMER'S QUESTION:\n{question_section}\n\n"
        f"=================================================================\n"
        f"YOUR ANSWER (in {lang_name} / {native_name} script — every single word):\n"
    )
    return prompt.strip()
