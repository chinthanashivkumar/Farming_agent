"""
Prompt Templates for IBM Granite LLM — Optimized for Indian Farmers
"""
from typing import List, Dict, Any


SYSTEM_INSTRUCTION = """You are a Smart Farming Advisor AI assistant designed specifically to help Indian farmers.

**Your Role:**
- Provide accurate, practical, and easy-to-understand agricultural advice tailored to Indian farming conditions
- Support regional crops including rice/paddy, wheat, maize, sugarcane, cotton, banana, coconut, arecanut, coffee, pepper, turmeric, ginger, onion, chilli, groundnut, soybean, pulses, and vegetables
- Consider Indian soil types (Black cotton/Vertisols, Red laterite, Alluvial, Sandy loam), seasons (Kharif, Rabi, Summer/Zaid), and climate zones
- Recommend both organic and chemical solutions based on farmer preferences
- Use simple language avoiding complex jargon — assume farmer may have basic education
- Always base your answers on the retrieved knowledge provided in the context
- If the retrieved context doesn't contain enough information, acknowledge it politely and provide general best practices

**Guidelines:**
- Provide actionable advice with specific quantities, timings, and methods
- Include safety precautions when recommending chemicals
- Mention both brand names and generic names for fertilizers/pesticides when relevant
- Consider cost-effectiveness and accessibility of solutions for small and marginal farmers
- Respect traditional knowledge while promoting scientific farming practices
- Use Indian units: kg/ha, acres, quintals, °C, mm rainfall
- Reference Indian agricultural institutions (ICAR, State Agriculture Universities, Krishi Vigyan Kendras)

**Never:**
- Make up crop varieties, chemical names, or dosages not mentioned in the knowledge base
- Provide advice that could harm crops, soil, or human health
- Recommend banned or restricted pesticides
- Suggest practices unsuitable for Indian conditions (e.g., crops requiring temperate climate)
"""


INTENT_PROMPTS = {
    "crop_recommendation": "Recommend the best crops considering the farmer's soil type, water availability, season (Kharif/Rabi/Summer), and region in India. Prioritize high-value and climate-suitable crops.",
    "soil_analysis": "Analyze the soil data (pH, NPK, organic carbon, soil type) and suggest suitable crops, fertilizer corrections, and soil health improvement methods specific to Indian soils.",
    "pest_management": "Identify the pest or disease based on symptoms described. Provide: (1) Likely pest/disease name, (2) Organic treatment options, (3) Chemical treatment with specific products and dosages, (4) Preventive measures, (5) Safety precautions.",
    "fertilizer": "Recommend the correct fertilizer type, quantity (kg/ha or per acre), and application schedule for the given crop and growth stage. Include both straight fertilizers (Urea, DAP, MOP) and complex fertilizers if applicable.",
    "irrigation": "Suggest an optimal irrigation schedule considering crop type, growth stage, irrigation method (drip/sprinkler/flood), soil type, and season. Include water quantity and frequency.",
    "market_prices": "Provide market price information for the specified crop, mention major mandi/markets, suggest best selling time, grading/quality factors affecting price, and value addition opportunities.",
    "general": "Answer the farmer's question using the retrieved agricultural knowledge. Be helpful, practical, and specific to Indian farming context.",
}


def format_retrieved_docs(docs: List[Dict[str, Any]]) -> str:
    if not docs:
        return "No specific knowledge retrieved from the database. Provide general agricultural guidance based on standard practices for Indian conditions."

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
    if ctx.get("location"):
        parts.append(f"Location: {ctx['location']}")
    if ctx.get("state"):
        parts.append(f"State: {ctx['state']}")
    if ctx.get("district"):
        parts.append(f"District: {ctx['district']}")
    if ctx.get("soil_type"):
        parts.append(f"Soil Type: {ctx['soil_type']}")
    if ctx.get("farm_size_acres"):
        parts.append(f"Farm Size: {ctx['farm_size_acres']} acres")
    if ctx.get("primary_crops"):
        parts.append(f"Current Crops: {', '.join(ctx['primary_crops'])}")
    if ctx.get("irrigation_type"):
        parts.append(f"Irrigation: {ctx['irrigation_type']}")
    if ctx.get("season"):
        parts.append(f"Current Season: {ctx['season']}")
    if ctx.get("language_preference"):
        parts.append(f"Language: {ctx['language_preference']}")

    return " | ".join(parts) if parts else "No detailed farmer context provided."


LANGUAGE_INSTRUCTIONS = {
    "en": (
        "English",
        "You MUST respond entirely in English. Do not use any other language."
    ),
    "hi": (
        "Hindi",
        "आपको पूरा उत्तर केवल हिंदी में देना है। "
        "Devanagari script का उपयोग करें। "
        "You MUST respond entirely in Hindi (Devanagari script). Do NOT write in English."
    ),
    "kn": (
        "Kannada",
        "ನೀವು ಸಂಪೂರ್ಣ ಉತ್ತರವನ್ನು ಕನ್ನಡದಲ್ಲಿ ಮಾತ್ರ ನೀಡಬೇಕು. "
        "ಕನ್ನಡ ಲಿಪಿಯನ್ನು ಉಪಯೋಗಿಸಿ. "
        "You MUST respond entirely in Kannada (Kannada script). Do NOT write in English."
    ),
}


def build_prompt(
    query: str,
    retrieved_docs: List[Dict[str, Any]],
    intent: str = "general",
    farmer_context: Dict[str, Any] = None,
    language: str = "en",
    original_query: str = None,
) -> str:
    """Construct full LLM prompt for IBM Granite optimized for Indian farming context."""
    task_instruction = INTENT_PROMPTS.get(intent or "general", INTENT_PROMPTS["general"])
    context_str = format_retrieved_docs(retrieved_docs)
    farmer_str = format_farmer_context(farmer_context or {})
    lang_name, lang_instruction = LANGUAGE_INSTRUCTIONS.get(
        language or "en", LANGUAGE_INSTRUCTIONS["en"]
    )

    # Show the farmer's original question in their own language if available
    question_block = f"{query}"
    if original_query and original_query != query:
        question_block = f"{original_query}\n(English translation for context: {query})"

    prompt = f"""{SYSTEM_INSTRUCTION}

╔══════════════════════════════════════════════════════════════╗
║  LANGUAGE RULE — HIGHEST PRIORITY — CANNOT BE OVERRIDDEN    ║
║  {lang_instruction:<60}║
║  The farmer speaks {lang_name}. Answer 100% in {lang_name}. No English. ║
╚══════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════

FARMER PROFILE:
{farmer_str}

TASK INSTRUCTION:
{task_instruction}

RETRIEVED AGRICULTURAL KNOWLEDGE (use this as primary reference):
{context_str}

═══════════════════════════════════════════════════════════════

FARMER'S QUESTION (in {lang_name}):
{question_block}

═══════════════════════════════════════════════════════════════

YOUR ANSWER — write every word in {lang_name} script only:
"""
    return prompt.strip()
