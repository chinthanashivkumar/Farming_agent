"""
Smart Farming Advisor — Simple Backend
Just 4 pip packages: fastapi, uvicorn, python-dotenv, httpx

Run:
    pip install fastapi uvicorn python-dotenv httpx
    python main.py
"""

import os, time, math
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

WATSONX_API_KEY    = os.getenv("WATSONX_API_KEY", "")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")
WATSONX_URL        = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

# ── Knowledge base — Indian crops focus ─────────────────────────────────────
KB = {
    "crop": """
Kharif (Jun-Oct): Paddy/Rice, Maize, Soybean, Cotton, Groundnut, Bajra, Arhar, Turmeric, Ginger, Chilli (transplant).
Rabi (Nov-Mar): Wheat, Barley, Mustard, Gram, Onion (Rabi), Sunflower, Rabi Paddy (South India).
Summer (Apr-Jun): Sunflower, Moong, Watermelon, Cucumber, Sweet Corn, Vegetables.
Plantation crops (perennial): Arecanut, Coconut, Coffee, Black Pepper, Banana, Mango.
Spice crops: Turmeric, Ginger, Chilli, Pepper — high value, good demand.
Laterite soil (coastal Karnataka/Kerala): Arecanut, Coconut, Coffee, Pepper, Cashew, Rubber.
Black cotton soil: Cotton, Sorghum, Wheat, Sugarcane, Onion.
Alluvial soil (river plains): Wheat, Rice, Sugarcane, Vegetables.
Sandy loam: Groundnut, Maize, Turmeric, Ginger, Vegetables.
""",
    "pest": """
Arecanut Koleroga (Phytophthora): Bunches turn black, premature drop in monsoon. Spray Bordeaux mixture 1% in June-July. Drench with Metalaxyl+Mancozeb 3g/L.
Coconut Red Palm Weevil: Bore holes, frass in trunk, yellow crown. Inject Chlorpyrifos 2ml/L into holes. Use 4 pheromone traps per hectare.
Paddy Blast: Spindle-shaped grey lesions. Apply Tricyclazole 0.6g/L at 25 and 45 days after transplanting.
Banana Panama Wilt: Yellowing from bottom leaves, pseudostem splits. No chemical cure — use wilt-resistant varieties, apply Trichoderma.
Chilli Thrips: Curled leaves, silvery streaks. Spray Spinosad 0.3ml/L or Abamectin 0.5ml/L.
Turmeric Rhizome Rot: Yellow wilting, rotting collar. Treat rhizomes with Metalaxyl before planting. Ensure proper drainage.
Maize Fall Armyworm: Ragged whorl, caterpillars inside. Spray Emamectin benzoate 0.4g/L into whorl at 15-18 days.
Aphids (all crops): Curled yellow leaves, sticky honeydew. Neem oil 3ml/L or Imidacloprid 0.3ml/L.
Coffee Leaf Rust: Yellowish orange powdery pustules. Spray Copper oxychloride 3g/L or Propiconazole.
Black Pepper Phytophthora: Yellowing and wilting. Drench with Metalaxyl 2g/L. Improve drainage.
Safety: Always wear gloves and mask. Spray early morning 6-9 AM. Never spray before expected rain.
""",
    "fertilizer": """
Arecanut (bearing palm/year): Urea 200g + SSP 130g + MOP 130g + FYM 12kg per palm. Apply June and September. Borax 25g/palm.
Coconut (per palm/year): Urea 1.3kg + SSP 2kg + MOP 2kg + FYM 50kg. Apply June and December in circular trench.
Banana (per plant): Urea 250g + DAP 100g + MOP 300g + FYM 10kg. In 4 splits over 9 months. Drip fertigation is best.
Paddy (per hectare): NPK 120:60:60 kg/ha. Full P+K at transplanting. Split N: 25% basal, 50% at 21 days, 25% at panicle initiation.
Sugarcane (per hectare): NPK 250:115:115 kg/ha in 3 splits. FYM 25t/ha. Drip saves 40% water.
Turmeric (per hectare): NPK 150:50:100 kg/ha + FYM 30t/ha. Mulch after planting.
Chilli (per hectare): NPK 100:50:50 kg/ha. Boron 0.2% spray at flowering improves fruit set.
Maize (per hectare): NPK 150:75:37.5 kg/ha. Urea in 3 splits: sowing, 30 days, 60 days.
Coffee (per plant/year): Urea 250g + SSP 150g + MOP 200g + FYM 5kg. Apply June and September.
Black Pepper (per vine): NPK 50:50:150g + FYM 5kg + Neem cake 1kg. Apply before and after monsoon.
Ginger (per hectare): NPK 75:50:75 kg/ha + FYM 30t/ha. ZnSO4 25kg/ha.
Onion (per hectare): NPK 100:50:75 kg/ha + Sulphur 25kg/ha. Avoid N after bulb formation.
Urea=46%N, DAP=18-46-0, SSP=0-16-0+Sulfur, MOP=0-0-60, NPK 17:17:17 is balanced.
""",
    "irrigation": """
Arecanut: 15-20 litres per palm per day in summer (March-May). Drip irrigation critical. Basin irrigation in other months.
Coconut: 40-200 litres per palm per week in dry season. Drip or basin. Mulching with coir pith saves water.
Banana: 8-10 mm/day. Critical at bunch development and shooting stages. Drip fertigation gives best yield.
Paddy: Maintain 3-5 cm standing water. Allow to dry periodically (AWD method). Drain 2 weeks before harvest.
Sugarcane: Drip gives 40% water saving and 25% yield increase. 8-10 litres per plant per day.
Turmeric/Ginger: Requires good drainage — rhizome rot in waterlogged conditions. 4-5 irrigations in dry area.
Coffee: Blossom shower irrigation (250 litres/plant) in Feb-March triggers flowering. Shade and mulch reduce water need.
Black Pepper: Light irrigation during dry season. Excess water causes collar rot. 2-3 irrigations in Feb-March.
Drip saves 40-60% water vs flood. PM Krishi Sinchai Yojana gives 45-55% subsidy on drip systems.
Best time to irrigate: 5-9 AM or 5-7 PM. Skip if 10+ mm rain forecast in 24 hours.
""",
    "soil": """
Laterite soil (coastal): pH 4.5-5.5, acidic. Apply lime 3-4 t/ha. Regular FYM essential. Good for arecanut, coconut, coffee.
Black cotton soil: pH 7.5-8.5, alkaline. Apply gypsum 2-3 t/ha. Raised beds for drainage. Good for cotton, sugarcane.
Optimal pH: 6.0-7.0 for most crops. 5.5-6.5 for arecanut, coconut, coffee, pepper, turmeric, ginger.
Low Nitrogen < 280 kg/ha: Add urea or FYM. Green manuring with Dhaincha or Sunhemp helps.
Low Phosphorus < 10 kg/ha: Apply DAP or SSP at sowing.
Low Potassium < 110 kg/ha: Apply MOP during fruiting/bunch development.
Low Organic Carbon < 0.5%: Add FYM 15t/ha or vermicompost 3-5t/ha. Neem cake 500kg/ha.
Get free Soil Health Card from KVK or government Agriculture Department.
""",
    "market": """
Arecanut: Rs 36,000-52,000/quintal. Best market: Shivamogga APMC (largest in India). CAMPCO cooperative offers fair price.
Coconut copra: Rs 8,500-12,000/quintal. Markets: Udupi, Coimbatore, Thrissur. Value addition: virgin coconut oil.
Banana (G9): Rs 900-1,600/quintal. Hoskote, Bangalore markets. Contract farming available.
Paddy: MSP Rs 2,183/quintal. Government procurement by FCI and state agencies.
Turmeric: Rs 7,000-20,000/quintal. Best market: Erode (TN), Nizamabad (TS). Sell 3-6 months after harvest for better price.
Black Pepper: Rs 40,000-65,000/quintal. Best market: Kochi, Kozhikode. Spices Board India helps connect to exporters.
Chilli (Teja dry): Rs 8,000-22,000/quintal. Guntur APMC market. Grade properly for premium.
Onion: Rs 1,000-2,800/quintal. Nashik APMC. Price volatile — consider FPO or cooperative selling.
Coffee (Cherry): Rs 5,000-8,000/quintal. Coffee Board India, Coorg/Chikkamagaluru markets.
Ginger (Dry): Rs 15,000-35,000/quintal. Calicut, Cochin markets.
Check live prices: agmarknet.nic.in or e-NAM app. Kisan Call Centre: 1800-180-1551.
""",
    "schemes": """
PM-KISAN (Pradhan Mantri Kisan Samman Nidhi): Rs 6,000/year to all small and marginal farmers in 3 equal installments.
Eligibility: Land-holding farmers with valid Aadhaar. Register at pmkisan.gov.in or nearest CSC.
PMFBY (Pradhan Mantri Fasal Bima Yojana): Crop insurance at subsidized premium (2% for Kharif, 1.5% for Rabi).
Covers natural disaster, drought, flood, pest/disease losses. Apply before sowing through bank or CSC.
PM Krishi Sinchai Yojana (PMKSY): Drip and sprinkler system at 45-55% subsidy. Small farmers get 55% subsidy.
Apply through state Horticulture Department or Agriculture Department office.
Soil Health Card: Free soil testing and card from Agriculture Department or KVK (Krishi Vigyan Kendra).
Test once every 2 years. Get NPK status and recommended fertilizer doses for your specific soil.
Kisan Credit Card (KCC): Short-term crop loans at 4% interest rate (up to Rs 3 lakh). Apply at any bank.
National Agriculture Market (e-NAM): Online mandi platform. Sell to any market across India. Better prices.
Rashtriya Krishi Vikas Yojana (RKVY): State-wise agriculture development grants. Contact state agriculture department.
Karnataka Raitha Siri Scheme: Annual Rs 2,000 bonus per acre for paddy farmers (Karnataka specific).
Sericulture schemes: Mulberry cultivation support in Karnataka, Andhra Pradesh, Tamil Nadu.
FPO (Farmer Producer Organizations): Join to get collective bargaining power, better market prices, input subsidies.
Kisan Call Centre: 1800-180-1551 (Free, 24x7). Get expert advice in local language.
"""
}

# ── Government Schemes data ──────────────────────────────────────────────────
SCHEMES = [
    {
        "id": "pm-kisan",
        "name": "PM-KISAN",
        "full_name": "Pradhan Mantri Kisan Samman Nidhi",
        "benefit": "₹6,000/year",
        "description": "Annual income support in 3 installments of ₹2,000 each directly to farmer bank account.",
        "eligibility": "All land-holding farmers with valid Aadhaar and land records",
        "how_to_apply": "pmkisan.gov.in · Nearest CSC center · Bank branch",
        "category": "income",
        "icon": "💰"
    },
    {
        "id": "pmfby",
        "name": "PMFBY",
        "full_name": "PM Fasal Bima Yojana",
        "benefit": "Crop Insurance",
        "description": "Subsidized crop insurance: 2% premium for Kharif, 1.5% for Rabi crops. Full sum insured on loss.",
        "eligibility": "All farmers growing notified crops. Loanee farmers enrolled automatically.",
        "how_to_apply": "Bank branch · CSC · pmfby.gov.in",
        "category": "insurance",
        "icon": "🛡️"
    },
    {
        "id": "pmksy",
        "name": "PM Krishi Sinchai Yojana",
        "full_name": "Pradhan Mantri Krishi Sinchai Yojana",
        "benefit": "45–55% subsidy on drip/sprinkler",
        "description": "Subsidy on micro-irrigation systems. Small farmers get 55% subsidy, others get 45%.",
        "eligibility": "All farmers. Apply before purchase of equipment.",
        "how_to_apply": "State Horticulture/Agriculture Dept · pmksy.gov.in",
        "category": "subsidy",
        "icon": "💧"
    },
    {
        "id": "soil-health-card",
        "name": "Soil Health Card",
        "full_name": "Soil Health Card Scheme",
        "benefit": "Free soil testing",
        "description": "Free soil test and recommendations every 2 years. Know your soil's NPK, pH, and micronutrients.",
        "eligibility": "All farmers",
        "how_to_apply": "Nearest KVK · Agriculture Dept. office · soilhealth.dac.gov.in",
        "category": "advisory",
        "icon": "🪱"
    },
    {
        "id": "kcc",
        "name": "Kisan Credit Card",
        "full_name": "Kisan Credit Card (KCC)",
        "benefit": "Crop loan at 4% interest",
        "description": "Short-term crop loans up to ₹3 lakh at 4% per annum (with interest subvention). No collateral up to ₹1.6 lakh.",
        "eligibility": "All farmers, sharecroppers, oral lessees",
        "how_to_apply": "Any nationalized bank · Regional Rural Bank · Co-operative bank",
        "category": "finance",
        "icon": "🏦"
    },
    {
        "id": "enam",
        "name": "e-NAM",
        "full_name": "National Agriculture Market",
        "benefit": "Better mandi prices",
        "description": "Online platform to sell crops across India. Transparent price discovery. No middlemen.",
        "eligibility": "All farmers. Requires Aadhaar + bank account.",
        "how_to_apply": "enam.gov.in · Nearest APMC office · Kisan Suvidha app",
        "category": "market",
        "icon": "📱"
    },
    {
        "id": "rkvy",
        "name": "RKVY",
        "full_name": "Rashtriya Krishi Vikas Yojana",
        "benefit": "Agriculture development grants",
        "description": "Infrastructure, machinery, storage, and processing unit grants through state agriculture departments.",
        "eligibility": "Individual farmers and FPOs. Project-based applications.",
        "how_to_apply": "State Agriculture Department · District Collector office",
        "category": "subsidy",
        "icon": "🏗️"
    },
    {
        "id": "fpo",
        "name": "FPO Support",
        "full_name": "Farmer Producer Organization",
        "benefit": "₹18 lakh grant per FPO",
        "description": "Form or join an FPO for collective bargaining, bulk input purchase, and better market prices.",
        "eligibility": "Minimum 300 farmers to form an FPO",
        "how_to_apply": "NABARD · SFAC · State Agriculture Dept",
        "category": "collective",
        "icon": "👥"
    }
]

# ── Intent detection — Indian crops aware ─────────────────────────────────
def detect_intent(msg: str) -> str:
    m = msg.lower()
    # Explicit prefixes from the frontend — check these first before keyword matching
    if "crop recommendation request" in m:
        return "crop"
    if "soil analysis request" in m:
        return "soil"
    if any(w in m for w in ["scheme", "subsidy", "pm-kisan", "pmkisan", "pmfby", "fasal bima", "krishi sinchai", "kcc", "kisan credit", "enam", "e-nam", "soil health card", "government help", "govt scheme", "fpo", "rkvy", "nabard", "insurance"]):
        return "schemes"
    if any(w in m for w in ["koleroga", "blast", "blight", "wilt", "rot", "weevil", "borer", "aphid", "thrips", "mite", "whitefly", "caterpillar", "bollworm", "armyworm", "mildew", "insect", "bug", "larvae", "frass", "spots on", "holes in", "yellow leaves", "brown leaves", "disease", "pest", "symptom", "spray pesticide", "fungicide", "leaf rust"]):
        return "pest"
    if any(w in m for w in ["urea", "dap", "mop", "ssp", "npk", "fertilizer", "manure", "compost", "fym", "fertigation"]):
        return "fertilizer"
    if any(w in m for w in ["irrigat", "drip", "sprinkler", "flood irrigat", "water schedule", "how much water", "when to water", "soil moisture", "waterlog", "litre per", "basin irrigation"]):
        return "irrigation"
    if any(w in m for w in ["price", "mandi", "market", "sell", "rate", "quintal", "profit", "income", "agmarknet", "msp", "minimum support", "apmc", "campco"]):
        return "market"
    if any(w in m for w in ["soil", "ph", "organic carbon", "nitrogen level", "potassium level", "soil type", "soil test"]):
        return "soil"
    if any(w in m for w in ["crop", "grow", "plant", "sow", "cultivat", "harvest", "season", "kharif", "rabi", "summer crop", "which crop", "best crop", "recommend crop", "yield", "arecanut", "coconut", "banana", "paddy", "rice", "sugarcane", "coffee", "pepper", "turmeric", "ginger", "chilli", "maize", "onion"]):
        return "crop"
    return "general"


# ── Demo answers — each intent gets a UNIQUE, specific answer ────────────────
def demo_answer(message: str) -> str:
    intent = detect_intent(message)
    msg    = message.lower()

    if intent == "schemes":
        if any(w in msg for w in ["pm-kisan", "pmkisan", "6000", "income support"]):
            return (
                "💰 **PM-KISAN — Pradhan Mantri Kisan Samman Nidhi:**\n\n"
                "✅ **Benefit:** ₹6,000 per year in 3 installments of ₹2,000 each\n"
                "👨‍🌾 **Who gets it:** All land-holding farmers with valid Aadhaar\n"
                "📝 **How to apply:**\n"
                "• Visit **pmkisan.gov.in** online\n"
                "• Go to nearest **CSC (Common Service Centre)**\n"
                "• Carry: Aadhaar + bank passbook + land documents\n\n"
                "📞 Helpline: **155261** · Check status at pmkisan.gov.in"
            )
        if any(w in msg for w in ["pmfby", "fasal bima", "insurance", "crop insurance"]):
            return (
                "🛡️ **PMFBY — Pradhan Mantri Fasal Bima Yojana:**\n\n"
                "✅ **Benefit:** Crop insurance at very low premium:\n"
                "• Kharif crops (Paddy, Maize, etc.) → **2% premium only**\n"
                "• Rabi crops (Wheat, Onion, etc.) → **1.5% premium only**\n"
                "• Rest paid by Government!\n\n"
                "📝 **How to apply:**\n"
                "• Apply at your **bank branch** before sowing season\n"
                "• Also at CSC center or pmfby.gov.in\n"
                "• **Loanee farmers** enrolled automatically\n\n"
                "⚠️ Covers: Drought, flood, pest attack, hailstorm, disease losses."
            )
        if any(w in msg for w in ["drip", "sinchai", "irrigation subsidy", "pmksy"]):
            return (
                "💧 **PM Krishi Sinchai Yojana (PMKSY):**\n\n"
                "✅ **Benefit:**\n"
                "• Small & marginal farmers: **55% subsidy** on drip/sprinkler system\n"
                "• Other farmers: **45% subsidy**\n\n"
                "💰 Drip system for 1 acre costs ₹35,000–₹55,000 — you pay only half!\n\n"
                "📝 **How to apply:**\n"
                "• Visit state **Horticulture Department** office\n"
                "• Carry: Aadhaar + land documents + bank account\n"
                "• pmksy.gov.in for details\n\n"
                "💡 Drip irrigation saves 40–60% water and increases yield by 20–30%."
            )
        if any(w in msg for w in ["kcc", "kisan credit", "loan", "credit"]):
            return (
                "🏦 **Kisan Credit Card (KCC):**\n\n"
                "✅ **Benefit:** Crop loans at **4% per annum** interest\n"
                "💳 Up to **₹3 lakh** without collateral\n\n"
                "📝 **How to apply:**\n"
                "• Visit any **nationalized bank**, RRB, or Co-operative bank\n"
                "• Carry: Aadhaar + land documents + passport photo\n"
                "• Approval usually within 2 weeks\n\n"
                "✅ Covers: Crop inputs, maintenance, post-harvest expenses\n"
                "📞 Bank helpline or **Kisan Call Centre: 1800-180-1551**"
            )
        return (
            "📋 **Government Schemes for Indian Farmers:**\n\n"
            "💰 **PM-KISAN** — ₹6,000/year income support → pmkisan.gov.in\n"
            "🛡️ **PMFBY** — Crop insurance at 2% premium → pmfby.gov.in\n"
            "💧 **PMKSY** — 45–55% subsidy on drip irrigation → pmksy.gov.in\n"
            "🪱 **Soil Health Card** — Free soil test → soilhealth.dac.gov.in\n"
            "🏦 **Kisan Credit Card** — Crop loans at 4% → Any bank\n"
            "📱 **e-NAM** — Sell crops online at better price → enam.gov.in\n"
            "👥 **FPO** — Join farmer group for better market prices\n\n"
            "📞 **Kisan Call Centre: 1800-180-1551** (Free, 24×7 in local language)"
        )

    if intent == "soil":
        # Parse pH value if provided in the message
        ph_val = None
        for token in msg.replace("="," ").replace(":"," ").split():
            try:
                v = float(token)
                if 1 < v < 14:
                    ph_val = v
                    break
            except: pass

        # Parse NPK
        n_val = p_val = k_val = oc_val = None
        import re
        n_m = re.search(r'nitrogen.*?(\d+\.?\d*)\s*kg', msg)
        p_m = re.search(r'phosphorus.*?(\d+\.?\d*)\s*kg', msg)
        k_m = re.search(r'potassium.*?(\d+\.?\d*)\s*kg', msg)
        oc_m = re.search(r'organic carbon.*?(\d+\.?\d*)', msg)
        if n_m: n_val = float(n_m.group(1))
        if p_m: p_val = float(p_m.group(1))
        if k_m: k_val = float(k_m.group(1))
        if oc_m: oc_val = float(oc_m.group(1))

        lines = ["🪱 **Soil Test Analysis Result:**\n"]

        # pH section
        if ph_val:
            if ph_val < 5.5:
                lines.append(f"🔴 **pH {ph_val} — Too Acidic**\n• Apply **Agricultural Lime** 2–3 bags (100 kg each) per acre\n• Wait 2–3 weeks after liming before sowing\n• Good for: Paddy can still grow, but apply lime first")
            elif ph_val > 7.5:
                lines.append(f"🟡 **pH {ph_val} — Alkaline**\n• Apply **Gypsum** 1–2 bags per acre to reduce pH\n• Add FYM 10 kg/tree or 5 t/acre to improve structure")
            else:
                lines.append(f"🟢 **pH {ph_val} — Optimal!** Most crops grow well at this pH ✅")
        else:
            lines.append("📊 **pH:** Not provided — get a Soil Health Card for free pH testing")

        # NPK section
        lines.append("\n📋 **NPK Status & Correction:**")
        if n_val is not None:
            if n_val < 280:   lines.append(f"• 🔴 Nitrogen {n_val} kg/ha = LOW → Apply **Urea 50 kg/acre** or FYM 2 trolleys")
            elif n_val < 560: lines.append(f"• 🟡 Nitrogen {n_val} kg/ha = MEDIUM → Apply **Urea 25 kg/acre** at sowing")
            else:             lines.append(f"• 🟢 Nitrogen {n_val} kg/ha = HIGH — No Urea needed now")
        else:
            lines.append("• Nitrogen: Not tested → Typical correction: Urea 40–50 kg/acre")
        if p_val is not None:
            if p_val < 10:    lines.append(f"• 🔴 Phosphorus {p_val} kg/ha = LOW → Apply **DAP 1 bag (50 kg)/acre** at sowing")
            elif p_val < 25:  lines.append(f"• 🟡 Phosphorus {p_val} kg/ha = MEDIUM → Apply **SSP 1 bag/acre**")
            else:             lines.append(f"• 🟢 Phosphorus {p_val} kg/ha = HIGH — No DAP needed")
        if k_val is not None:
            if k_val < 110:   lines.append(f"• 🔴 Potassium {k_val} kg/ha = LOW → Apply **MOP 25 kg/acre** at fruiting stage")
            elif k_val < 280: lines.append(f"• 🟡 Potassium {k_val} kg/ha = MEDIUM → Apply **MOP 15 kg/acre**")
            else:             lines.append(f"• 🟢 Potassium {k_val} kg/ha = HIGH — MOP not required")
        if oc_val is not None:
            if oc_val < 0.5:  lines.append(f"• 🔴 Organic Carbon {oc_val}% = LOW → Add **Vermicompost 500 kg/acre** + FYM 2 t/acre every year")
            elif oc_val < 0.75: lines.append(f"• 🟡 Organic Carbon {oc_val}% = MEDIUM → Add FYM 1 t/acre")
            else:             lines.append(f"• 🟢 Organic Carbon {oc_val}% = GOOD ✅")

        lines.append("\n💡 *Get a **free Soil Health Card** from your nearest KVK (Krishi Vigyan Kendra). Test every 2 years.*")
        return "\n".join(lines)

    if intent == "pest":
        if any(w in msg for w in ["koleroga", "arecanut", "areca", "bunch rot", "phytophthora"]):
            return (
                "🌿 **Arecanut Koleroga (Fruit Rot):**\n\n"
                "**What you see:** Bunches turning black, premature fruit drop during monsoon\n\n"
                "✅ **Treatment:**\n"
                "• 🌿 **Bordeaux mixture 1%** — spray on bunches + stalk (June-July)\n"
                "• 💊 **Metalaxyl + Mancozeb 3g/L** — drench at base if severe\n"
                "• ✂️ Remove and burn infected bunches immediately\n\n"
                "🛡️ **Prevention:** Spray Bordeaux mixture *before monsoon starts* (May)\n"
                "⚠️ Best spray time: 6–9 AM. Wear mask and gloves.\n"
                "📞 Contact: Arecanut Research Station, Vitla (Karnataka)"
            )
        if any(w in msg for w in ["aphid", "sticky", "yellow leaves", "curled"]):
            return (
                "🐛 **Looks like APHIDS!**\n\n"
                "**What you see:** Curled yellow leaves, sticky liquid on leaves\n\n"
                "✅ **Simple Treatment:**\n"
                "• 🌿 **Natural:** Mix **3ml neem oil** in 1 litre water, spray on leaves (bottom side too)\n"
                "• 💊 **Chemical:** **Imidacloprid** — 0.3 ml in 1 litre water\n"
                "• 🚿 Spray with strong water jet to wash them off\n\n"
                "⚠️ **Safety:** Wear gloves. Spray in early morning (6–9 AM).\n"
                "🔁 Repeat after 7 days if still present."
            )
        if any(w in msg for w in ["blast", "grey lesion", "spindle", "neck rot"]):
            return (
                "🌾 **Paddy Blast Disease:**\n\n"
                "**What you see:** Spindle-shaped grey or brown lesions on leaves, grey neck at panicle\n\n"
                "✅ **Treatment:**\n"
                "• 💊 **Tricyclazole 75 WP** — 0.6g/L water. Spray at 25 and 45 days after transplanting.\n"
                "• 💊 **Carbendazim** — 1g/L as alternative\n"
                "• ✂️ Remove infected tillers\n\n"
                "🛡️ **Prevention:**\n"
                "• Use blast-resistant varieties (Samba Masuri, BPT-5204)\n"
                "• Avoid excess Nitrogen fertilizer\n"
                "• Do NOT waterlog — maintain alternate wetting and drying"
            )
        if any(w in msg for w in ["bollworm", "hole", "boll", "cotton", "frass"]):
            return (
                "🐛 **Looks like BOLLWORM!**\n\n"
                "✅ **Simple Treatment:**\n"
                "• 🟢 **Organic:** Spray **Bt (Bacillus thuringiensis)** — safe for humans\n"
                "• 💊 **Chemical:** **Emamectin benzoate** — 0.4g per litre water\n"
                "• 🪤 Put **pheromone traps** in field to catch adult moths\n\n"
                "⚠️ **Safety:** Do not spray during flowering. Wear mask while spraying."
            )
        if any(w in msg for w in ["weevil", "coconut weevil", "red palm"]):
            return (
                "🥥 **Coconut Red Palm Weevil:**\n\n"
                "**What you see:** Bore holes in trunk, frass oozing, yellow drooping crown\n\n"
                "✅ **Treatment:**\n"
                "• 💊 **Inject Chlorpyrifos 2ml/L** into bore holes using syringe. Seal with mud.\n"
                "• 🪤 Install **4 pheromone traps per hectare** to catch adults\n"
                "• 🌿 Fill holes with **Carbaryl 10% dust + sand**\n\n"
                "⚠️ **Severe infestation:** Fell and destroy infested palms. Burning is best.\n"
                "🛡️ **Prevention:** Keep crown clean. Apply Chlorpyrifos 0.1% to crown area."
            )
        # Generic pest answer
        return (
            "🐛 **Pest & Disease Guide for Farmers:**\n\n"
            "**Common Indian Crop Problems & Quick Fix:**\n\n"
            "🌿 **Arecanut Koleroga** → Bordeaux mixture 1% spray before monsoon\n"
            "🥥 **Coconut Weevil** → Chlorpyrifos injection + pheromone traps\n"
            "🌾 **Paddy Blast** → Tricyclazole 0.6g/L at 25 + 45 days\n"
            "🍌 **Banana Wilt** → Remove infected plants, plant Trichoderma\n"
            "🌶️ **Chilli Thrips** → Spinosad 0.3ml/L or Abamectin\n"
            "🍂 **Turmeric Rhizome Rot** → Metalaxyl seed treatment\n"
            "🌽 **Maize Armyworm** → Emamectin 0.4g/L into whorl\n\n"
            "⚠️ **Always:** Wear gloves + mask. Spray early morning 6–9 AM."
        )

    if intent == "fertilizer":
        crop_hint = ""
        for crop in ["arecanut","coconut","banana","paddy","rice","sugarcane","turmeric","ginger","chilli","maize","onion","wheat","tomato","cotton","potato","pepper","coffee"]:
            if crop in msg:
                doses = {
                    "arecanut":  "**200g Urea + 130g SSP + 130g MOP + 12kg FYM** per palm per year. Apply in June and September splits.",
                    "coconut":   "**1.3kg Urea + 2kg SSP + 2kg MOP + 50kg FYM** per palm per year. Apply June and December.",
                    "banana":    "**250g Urea + 100g DAP + 300g MOP + 10kg FYM** per plant. Give in 4 splits. Drip fertigation is best.",
                    "paddy":     "NPK **120:60:60** kg/ha → Full P+K at transplanting. N in 3 splits: 25%+50%+25%",
                    "rice":      "NPK **120:60:60** kg/ha → Full P+K at transplanting. N in 3 splits: 25%+50%+25%",
                    "sugarcane": "NPK **250:115:115** kg/ha in 3 splits. FYM 25t/ha basal. Drip fertigation recommended.",
                    "turmeric":  "NPK **150:50:100** kg/ha + FYM 30t/ha. Apply Borax 10kg/ha + ZnSO4 25kg/ha.",
                    "ginger":    "NPK **75:50:75** kg/ha + FYM 30t/ha. Apply ZnSO4 25kg/ha. Mulch after planting.",
                    "chilli":    "NPK **100:50:50** kg/ha. Boron spray 0.2% at flowering. Drip fertigation improves yield.",
                    "maize":     "NPK **150:75:37** kg/ha. Urea in 3 splits at sowing, 30 days, 60 days.",
                    "onion":     "NPK **100:50:75** kg/ha + Sulphur 25kg/ha. Avoid N after bulb formation.",
                    "wheat":     "NPK **120:60:40** kg/ha → Half Urea at sowing + rest at first irrigation (21 days)",
                    "tomato":    "NPK **200:120:120** kg/ha + FYM 25t/ha + Boron 0.2% spray at flowering",
                    "cotton":    "NPK **150:75:75** kg/ha → Stop excess N after boll formation",
                    "potato":    "NPK **150:80:100** kg/ha. Full dose at planting. Earthing up at 30 days.",
                    "pepper":    "**NPK 50:50:150g** per vine (bearing). Apply FYM 5kg + Neem cake 1kg per vine.",
                    "coffee":    "**Urea 250g + SSP 150g + MOP 200g** per plant per year. Apply June and September.",
                }
                crop_hint = f"\n\n🌾 **For {crop.capitalize()}:**\n{doses.get(crop,'')}"
                break
        return (
            "🧪 **Fertilizer Guide:**\n\n"
            "📦 **What each fertilizer does:**\n"
            "• **Urea** = Gives Nitrogen (N) → Makes plant grow GREEN and tall\n"
            "• **DAP** = Gives N + Phosphorus (P) → Helps roots grow strong\n"
            "• **MOP** = Gives Potassium (K) → Makes fruits bigger and tastier\n"
            "• **FYM/Compost** = Improves soil health naturally\n"
            + crop_hint +
            "\n\n⚠️ **Golden Rule:** Do a soil test first. Too much fertilizer = wasted money + harms soil.\n"
            "💡 Apply in 2–3 split doses. Never apply before heavy rain."
        )

    if intent == "irrigation":
        # Give a full dedicated plan for each important crop
        if any(w in msg for w in ["arecanut","areca","supari","betel nut"]):
            return (
                "💧 **Arecanut Irrigation Plan:**\n\n"
                "📅 **Monthly schedule:**\n"
                "• **Nov–Feb (cool/dry):** 15–20 litres per palm every **3–4 days**\n"
                "• **Mar–May (summer):** 20–25 litres per palm **every day** or alternate day\n"
                "• **Jun–Oct (monsoon):** No irrigation needed if rainfall > 50mm/week\n\n"
                "💧 **Best method:** Drip irrigation at base of palm — saves 50% water\n"
                "• Drip flow rate: 4–8 litres/hour per emitter\n"
                "• Basin irrigation: Make 1m wide, 15cm deep basin around palm\n\n"
                "⚠️ **Critical stages needing most water:**\n"
                "• Bunch development (Mar–May) — never let soil dry completely\n"
                "• Nut filling stage — maintain soil moisture at 60–70%\n\n"
                "💡 **Mulching:** Apply 10–15 kg coir pith or dry leaves around base. Saves 40% water.\n"
                "🏛️ **Subsidy:** PM Krishi Sinchai Yojana gives 55% subsidy on drip systems."
            )
        if any(w in msg for w in ["coconut","nariyal","tengu","copra"]):
            return (
                "💧 **Coconut Irrigation Plan:**\n\n"
                "📅 **Seasonal schedule:**\n"
                "• **Dec–Feb:** 40–50 litres per palm every **5–6 days**\n"
                "• **Mar–May (peak summer):** 100–200 litres per palm every **3–4 days**\n"
                "• **Jun–Oct (monsoon):** No irrigation if rain is adequate\n\n"
                "💧 **Methods:**\n"
                "• Basin: 1.5m radius, 20cm deep basin around trunk\n"
                "• Drip: 2 emitters at 1m from trunk, 8 litres/hour each\n"
                "• Pot irrigation (coastal): bury pot near roots, fill weekly\n\n"
                "⚠️ **Signs of water stress:** Yellow leaves, reduced nut size, premature nut drop\n"
                "💡 Mulch with coir pith 20–25 kg per palm to retain moisture."
            )
        if any(w in msg for w in ["paddy","rice"]):
            return (
                "💧 **Paddy / Rice Irrigation Plan:**\n\n"
                "📅 **Stage-wise water management:**\n"
                "• **Transplanting:** Keep 2–3 cm standing water for 7 days\n"
                "• **Tillering (day 10–30):** 3–5 cm standing water — critical stage!\n"
                "• **Panicle initiation (day 50–60):** 5 cm water — never let dry\n"
                "• **Flowering/heading:** 3–5 cm water continuously\n"
                "• **Grain filling:** Reduce to 2 cm, then allow to dry\n"
                "• **2 weeks before harvest:** Drain field completely\n\n"
                "💡 **AWD method (saves 30% water):**\n"
                "• Install perforated pipe 20cm deep in field\n"
                "• Irrigate only when water level drops 15cm below surface\n\n"
                "⚠️ Total water needed: 1200–1800mm per crop season"
            )
        if any(w in msg for w in ["banana","kela","bale","plantain"]):
            return (
                "💧 **Banana Irrigation Plan:**\n\n"
                "📅 **Stage-wise schedule:**\n"
                "• **Planting to 3 months:** 8 litres per plant every **2–3 days**\n"
                "• **Vegetative (3–7 months):** 10–12 litres per plant daily\n"
                "• **Bunch shooting (critical):** 15 litres per plant daily — never skip!\n"
                "• **Bunch development to harvest:** 12 litres per plant daily\n\n"
                "💧 **Best method:** Drip irrigation — 2 emitters per plant at 30cm from base\n"
                "• Saves 40% water vs flood irrigation\n"
                "• Can do fertigation (fertilizer + water together)\n\n"
                "⚠️ **Critical:** Water stress at shooting reduces bunch weight by 30–40%\n"
                "💡 Mulch with dry leaves/sugarcane trash to save moisture."
            )
        if any(w in msg for w in ["sugarcane","ganna"]):
            return (
                "💧 **Sugarcane Irrigation Plan:**\n\n"
                "📅 **Stage-wise schedule:**\n"
                "• **Germination (0–30 days):** Light irrigation every 7–10 days\n"
                "• **Tillering (1–3 months):** Every 10–12 days\n"
                "• **Grand growth (3–7 months):** Every 7–10 days — maximum water need\n"
                "• **Maturity (7–10 months):** Every 15–20 days, reduce gradually\n\n"
                "💧 **Drip irrigation:**\n"
                "• 8–10 litres per plant per day via inline drip\n"
                "• 40% water saving vs furrow irrigation\n"
                "• 25% higher yield with drip + fertigation\n\n"
                "⚠️ Total water: 1500–2000mm per season\n"
                "🏛️ **Subsidy:** PMKSY gives 55% subsidy on drip for sugarcane."
            )
        if any(w in msg for w in ["turmeric","haldi"]):
            return (
                "💧 **Turmeric Irrigation Plan:**\n\n"
                "📅 **Schedule:**\n"
                "• **After planting (May–Jun):** Irrigate immediately after planting\n"
                "• **Vegetative phase:** Every **7–10 days** in dry weather\n"
                "• **Rhizome development (Aug–Oct):** Every **5–7 days** — critical!\n"
                "• **Monsoon:** No irrigation if adequate rain\n\n"
                "⚠️ **Most important:** Turmeric must NOT be waterlogged — causes rhizome rot!\n"
                "• Grow on raised beds (15–20cm) for good drainage\n"
                "• Total irrigations needed: 15–20 times in 8-month crop\n\n"
                "💡 Apply thick mulch (sugarcane trash/dry leaves) after planting — saves 60% water."
            )
        if any(w in msg for w in ["coffee"]):
            return (
                "💧 **Coffee Irrigation Plan:**\n\n"
                "📅 **Schedule:**\n"
                "• **Blossom shower (Feb–Mar):** 1–2 heavy irrigations of 250 litres/plant to trigger flowering\n"
                "• **Berry development (Apr–Jun):** 1 irrigation every 10–15 days\n"
                "• **Monsoon (Jun–Sep):** No irrigation needed\n"
                "• **Post-monsoon (Oct–Nov):** Stop irrigation to harden berries for harvest\n\n"
                "💧 **Method:** Overhead sprinkler or basin. Drip not preferred.\n"
                "⚠️ Over-irrigation causes root rot and berry drop\n"
                "💡 Coffee shade trees reduce water need by 30–40%."
            )
        if any(w in msg for w in ["pepper","black pepper","kali mirch"]):
            return (
                "💧 **Black Pepper Irrigation Plan:**\n\n"
                "📅 **Schedule:**\n"
                "• **Dry season (Dec–May):** 2–3 irrigations per month — 10 litres per vine\n"
                "• **Flowering (Feb–Apr):** Regular moisture critical for spike setting\n"
                "• **Monsoon (Jun–Oct):** No irrigation — ensure drainage around standards\n\n"
                "⚠️ **Do NOT over-irrigate** — waterlogging causes Phytophthora collar rot\n"
                "• Grow on well-drained slopes or raised mounds\n"
                "💡 Mulch with dry leaves to retain moisture in dry season."
            )
        if any(w in msg for w in ["chilli","mirchi","capsicum"]):
            return (
                "💧 **Chilli Irrigation Plan:**\n\n"
                "📅 **Stage-wise schedule:**\n"
                "• **Transplanting:** Irrigate immediately after transplanting\n"
                "• **Establishment (0–30 days):** Every **4–5 days**\n"
                "• **Flowering (45–60 days):** Every **3–4 days** — critical stage!\n"
                "• **Fruit setting & filling:** Every **4–5 days**\n"
                "• **Before harvest:** Reduce irrigation to improve colour and drying\n\n"
                "💧 **Best method:** Drip irrigation — 3–4 litres per plant per day\n"
                "⚠️ Water stress at flowering causes blossom drop and fruit abortion\n"
                "💡 Boron spray 0.2% at flowering improves fruit set."
            )
        if any(w in msg for w in ["onion","pyaz"]):
            return (
                "💧 **Onion Irrigation Plan:**\n\n"
                "📅 **Stage-wise schedule:**\n"
                "• **After transplanting:** Light irrigation every **4–5 days**\n"
                "• **Bulb development (45–90 days):** Every **5–7 days** — critical!\n"
                "• **3 weeks before harvest:** Stop all irrigation to allow skin to form\n\n"
                "💧 Sprinkler irrigation gives best results for onion\n"
                "⚠️ Over-irrigation causes purple blotch disease and neck rot\n"
                "⚠️ Do NOT irrigate after bulb maturity — causes double bulbs"
            )
        # Generic irrigation guide for any other crop
        crop_name = ""
        for c in ["maize","wheat","cotton","soybean","groundnut","tomato","potato","ginger"]:
            if c in msg: crop_name = c.capitalize(); break
        generic_tip = f" For **{crop_name}**:" if crop_name else ""
        return (
            f"💧 **Irrigation Guide{generic_tip}**\n\n"
            "⏰ **Best time to irrigate:** Early morning (5–8 AM) or evening (5–7 PM)\n\n"
            "📊 **Frequency by soil type:**\n"
            "• Sandy soil → Every **3–4 days**\n"
            "• Loamy soil → Every **5–6 days**\n"
            "• Clay soil  → Every **7–8 days**\n\n"
            "📋 **Critical growth stages needing most water:**\n"
            "• Germination/transplanting — always irrigate immediately\n"
            "• Flowering stage — never let soil dry out\n"
            "• Fruit/grain filling — maintain 60–70% soil moisture\n\n"
            "💡 **Tips:**\n"
            "• Drip irrigation saves **40–60%** water vs flood\n"
            "• Mulching reduces water loss by 30–40%\n"
            "• Skip irrigation if 10+ mm rain expected\n"
            "• Finger test: push finger 5cm into soil — if dry, irrigate now\n\n"
            "🏛️ PMKSY gives 55% subsidy on drip systems — apply at Horticulture Dept."
        )

    if intent == "market":
        crop_hint = ""
        prices = {
            "arecanut": ("₹36,000–₹52,000", "Best market: Shivamogga APMC (Karnataka). CAMPCO cooperative offers fair prices. Peak price: March–June."),
            "coconut":  ("₹8,500–₹12,000 (copra)", "Markets: Udupi, Coimbatore, Thrissur. Value addition as virgin coconut oil fetches premium."),
            "banana":   ("₹900–₹1,600", "Hoskote, Bangalore APMC. G9 variety preferred. Contract farming available."),
            "paddy":    ("₹2,183 (MSP)", "Government MSP procurement. Sell at FCI or state agency. Check APMC for premium varieties."),
            "rice":     ("₹2,183 (MSP)", "Government MSP available. Check APMC for Samba Masuri (BPT-5204) premium."),
            "turmeric": ("₹7,000–₹20,000", "Best market: Erode (TN), Nizamabad (TS). Sell 3–6 months after harvest for better price."),
            "pepper":   ("₹40,000–₹65,000", "Markets: Kochi, Kozhikode (Kerala). Spices Board India helps export. Organic fetches 2–3x premium."),
            "ginger":   ("₹15,000–₹35,000 (dry)", "Sell dried ginger for better price. Calicut, Cochin markets. Export quality commands premium."),
            "chilli":   ("₹8,000–₹22,000", "Guntur APMC (AP) is largest chilli market. Grade Teja variety separately for best price."),
            "onion":    ("₹1,000–₹2,800", "Nashik APMC. Price very volatile. FPO collective selling gives better price."),
            "sugarcane":("FRP ₹315/qt (2023-24)", "Sell to sugar factory linked to your area. FRP (Fair and Remunerative Price) is guaranteed."),
            "wheat":    ("₹2,275 (MSP)", "Government MSP available. Sell at FCI or registered mandi."),
            "coffee":   ("₹5,000–₹8,000 (cherry)", "Coffee Board India, Coorg/Chikkamagaluru markets. Organic certification fetches premium."),
            "tomato":   ("₹500–₹5,000", "Highly volatile. Sell Feb–May for best price. Bangalore APMC. Consider contract farming."),
            "cotton":   ("₹6,500/qt MSP", "Cotton Corporation of India or APMC mandi. Grade Bt cotton separately."),
            "soybean":  ("₹4,600/qt MSP", "Best selling Oct–Dec. Avoid immediate post-harvest sale."),
        }
        for crop, (price, tip) in prices.items():
            if crop in msg:
                crop_hint = f"\n\n📍 **{crop.capitalize()} price:** {price}/quintal\n💡 {tip}"
                break
        return (
            "📊 **Indian APMC Market Prices:**\n\n"
            "🏪 **Key prices** *(indicative — check agmarknet.nic.in for live rates)*:\n"
            "• 🌿 Arecanut: **₹36,000–₹52,000**/qt (Shivamogga)\n"
            "• 🥥 Coconut copra: **₹8,500–₹12,000**/qt\n"
            "• 🍌 Banana (G9): **₹900–₹1,600**/qt\n"
            "• 🌾 Paddy: **₹2,183** (MSP)\n"
            "• 🍂 Turmeric: **₹7,000–₹20,000**/qt (Erode)\n"
            "• 🌶️ Chilli: **₹8,000–₹22,000**/qt (Guntur)\n"
            "• 🫒 Pepper: **₹40,000–₹65,000**/qt (Kochi)\n"
            + crop_hint +
            "\n\n📱 **Check live prices:**\n"
            "• agmarknet.nic.in · e-NAM app · Kisan Suvidha app\n"
            "• 📞 Kisan Call Centre: **1800-180-1551** (Free)"
        )

    if intent == "crop":
        # Extract season and state from the structured message
        season_in_msg = ""
        state_in_msg  = ""
        for s in ["kharif","rabi","summer","plantation"]:
            if s in msg: season_in_msg = s; break
        for st in ["karnataka","kerala","tamil nadu","andhra pradesh","telangana","maharashtra","madhya pradesh","uttar pradesh","punjab","west bengal","assam","odisha","gujarat","rajasthan","bihar"]:
            if st in msg: state_in_msg = st.title(); break

        # State-specific crop recommendations
        if "karnataka" in msg or "laterite" in msg:
            if "plantation" in msg or "perennial" in msg:
                return (
                    "🌿 **Best Plantation Crops for Karnataka:**\n\n"
                    "1. **Arecanut (Supari)** 🌿 — Best crop for coastal & Malnad Karnataka\n"
                    "   • Yield: 2–4 kg dry/palm/year · Price: ₹36,000–₹52,000/qt · Market: Shivamogga APMC\n"
                    "   • ⚠️ Risk: Koleroga in monsoon — spray Bordeaux mixture before June\n\n"
                    "2. **Coconut** 🥥 — Excellent for coastal Karnataka\n"
                    "   • Yield: 80–150 nuts/palm/year · Price: ₹10,500/qt copra · Market: Udupi APMC\n"
                    "   • 💡 Intercrop with banana & turmeric for extra income\n\n"
                    "3. **Coffee (Robusta)** ☕ — Best for Kodagu, Chikkamagaluru, Sakleshpur\n"
                    "   • Yield: 500–800 kg/acre · Price: ₹5,000–₹8,000/qt cherry\n"
                    "   • 💡 Coffee Board India gives export support and premium prices\n\n"
                    "4. **Black Pepper** 🫒 — High value spice, grows with coffee/coconut\n"
                    "   • Yield: 2–4 kg dry/vine · Price: ₹40,000–₹65,000/qt · Market: Kochi\n\n"
                    "5. **Banana (G9)** 🍌 — Short-duration 11 months, good returns\n"
                    "   • Yield: 25–35 kg/bunch · Price: ₹900–₹1,600/qt · Market: Hoskote APMC"
                )
            return (
                "🌾 **Best Crops for Karnataka (Kharif + Rabi):**\n\n"
                "🌧️ **Kharif season (June–Oct):**\n"
                "• **Paddy (BPT-5204, Samba Masuri)** — MSP ₹2,183/qt. SRI method saves 40% water.\n"
                "• **Ragi (Finger Millet)** — Drought resistant. Price ₹3,000–₹4,000/qt.\n"
                "• **Maize (Hybrid)** — Yield 4–6 t/ha. Good demand from poultry feed industry.\n"
                "• **Turmeric** — High value. Price ₹7,000–₹20,000/qt at Erode/Nizamabad.\n\n"
                "❄️ **Rabi season (Oct–Feb):**\n"
                "• **Onion** — Good profit but volatile price. Sell at Bangalore APMC.\n"
                "• **Sunflower** — Low water requirement. MSP available.\n"
                "• **Groundnut** — Good for sandy loam. MSP ₹5,850/qt.\n\n"
                "🌿 **Plantation (perennial):**\n"
                "• Arecanut, Coconut, Coffee, Pepper, Banana — select **Plantation** tab for details."
            )

        if "kerala" in msg:
            return (
                "🌿 **Best Crops for Kerala:**\n\n"
                "1. **Coconut** 🥥 — State crop. 150–200 nuts/palm. Copra ₹10,500/qt.\n"
                "2. **Rubber** — Long-term investment. Latex ₹180–220/kg.\n"
                "3. **Black Pepper** 🫒 — Spice garden staple. ₹40,000–₹65,000/qt at Kochi.\n"
                "4. **Arecanut** — Wayanad, Palakkad. ₹36,000–₹52,000/qt.\n"
                "5. **Banana (Nendran)** 🍌 — Premium variety. ₹40–50/kg retail.\n"
                "6. **Ginger** 🫚 — Dry ginger ₹15,000–₹35,000/qt. Good export demand.\n\n"
                "💡 *Kerala farmers benefit from spice export. Contact Spices Board India for export registration.*"
            )

        if any(s in msg for s in ["andhra pradesh","telangana","guntur"]):
            return (
                "🌾 **Best Crops for Andhra Pradesh / Telangana:**\n\n"
                "1. **Chilli (Teja/Byadagi)** 🌶️ — Highest value. ₹8,000–₹22,000/qt at Guntur APMC.\n"
                "2. **Paddy** — MSP ₹2,183/qt. Kharif and Rabi both seasons.\n"
                "3. **Cotton** — Black cotton soil. MSP ₹6,500/qt.\n"
                "4. **Turmeric** — Nizamabad is major market. ₹7,000–₹20,000/qt.\n"
                "5. **Groundnut** — Sandy loam soils. MSP ₹5,850/qt.\n"
                "6. **Banana** — Krishna, Guntur districts. G9 variety best.\n\n"
                "📞 *Contact ANGRAU (Acharya NG Ranga Agricultural University) for variety advice.*"
            )

        if any(s in msg for s in ["maharashtra","nashik","pune"]):
            return (
                "🌾 **Best Crops for Maharashtra:**\n\n"
                "1. **Onion** 🧅 — Nashik is India's largest market. ₹1,000–₹2,800/qt.\n"
                "2. **Sugarcane** 🎋 — FRP ₹315/qt guaranteed at sugar mills.\n"
                "3. **Soybean** — Kharif. MSP ₹4,600/qt. Low input cost.\n"
                "4. **Cotton (Bt)** — Vidarbha region. MSP ₹6,500/qt.\n"
                "5. **Pomegranate** — Solapur, Nashik. Premium market ₹40–80/kg.\n"
                "6. **Grapes** — Nashik region. Export quality fetches premium.\n\n"
                "💡 *Nashik APMC is India's largest onion market. Sell in February–April for best price.*"
            )

        # Generic season-based response
        month = time.localtime().tm_mon
        if "plantation" in msg or "perennial" in msg:
            return (
                "🌿 **Plantation / Perennial Crops (All India):**\n\n"
                "1. **Arecanut** 🌿 — Karnataka, Kerala, Assam · ₹36,000–₹52,000/qt\n"
                "2. **Coconut** 🥥 — Coastal India · ₹10,500/qt copra\n"
                "3. **Coffee** ☕ — Coorg, Chikkamagaluru, Wayanad · ₹5,000–₹8,000/qt\n"
                "4. **Black Pepper** 🫒 — Kerala, Karnataka · ₹40,000–₹65,000/qt\n"
                "5. **Banana (G9)** 🍌 — Pan India · ₹900–₹1,600/qt\n"
                "6. **Mango (Alphonso)** 🥭 — Maharashtra, Goa · ₹60–₹120/kg\n\n"
                "💡 *Select your state above for more specific plantation crop advice.*"
            )
        if 6 <= month <= 10:
            season, crops_list = "Kharif (Monsoon — Jun to Oct)", [
                ("🌾 Paddy","Best for rice-growing states · MSP ₹2,183/qt"),
                ("🌽 Maize","Hybrid varieties · Yield 5–8 t/ha · Good poultry demand"),
                ("🍂 Turmeric","High value spice · ₹7,000–₹20,000/qt at Erode"),
                ("🫚 Ginger","Wet areas · Dry ginger ₹15,000–₹35,000/qt"),
                ("🌶️ Chilli","AP/Telangana · ₹8,000–₹22,000/qt at Guntur"),
                ("🥜 Groundnut","Sandy loam · MSP ₹5,850/qt"),
            ]
        elif month >= 11 or month <= 3:
            season, crops_list = "Rabi (Winter — Nov to Mar)", [
                ("🌾 Wheat","North India · MSP ₹2,275/qt · Best in Punjab/UP"),
                ("🧅 Onion","Nashik APMC · Sell Feb–Apr for best price"),
                ("🌱 Gram (Chickpea)","Low water · MSP ₹5,440/qt"),
                ("🌻 Sunflower","Drought tolerant · Good oil crop"),
                ("🫘 Mustard","Rajasthan/MP · MSP ₹5,650/qt"),
                ("🌾 Rabi Paddy","South India (Karnataka/TN) · Fine varieties"),
            ]
        else:
            season, crops_list = "Summer/Zaid (Apr to Jun)", [
                ("🍉 Watermelon","Fast crop 60–70 days · ₹5–15/kg"),
                ("🥒 Cucumber","Low cost · Quick return"),
                ("🌽 Sweet Corn","50–60 days · Good demand"),
                ("🫘 Moong (Green Gram)","Drought tolerant · MSP ₹8,558/qt"),
                ("🌻 Sunflower","Summer variety · 90 days"),
            ]
        result = f"🌾 **Recommended Crops — {season}:**\n\n"
        for name, tip in crops_list:
            result += f"• **{name}** — {tip}\n"
        result += "\n📋 *Select your state and soil type for more specific advice.*"
        return result

    return (
        "🌿 **Namaste! I am your Kisan AI Farming Advisor.**\n\n"
        "Ask me anything about Indian crops:\n\n"
        "🌿 **Arecanut/Supari** — Koleroga treatment, fertilizer, price\n"
        "🥥 **Coconut** — Pest control, irrigation, copra market\n"
        "🌾 **Paddy/Rice** — SRI method, fertilizer schedule, blast disease\n"
        "🍌 **Banana** — Panama wilt, bunch care, G9 variety\n"
        "🍂 **Turmeric/Ginger** — Rhizome rot, drying, market price\n"
        "🌶️ **Chilli** — Thrips, Byadagi variety, Guntur market\n"
        "☕ **Coffee/Pepper** — Leaf rust, Koleroga, Kodagu farming\n"
        "📋 **Schemes** — PM-KISAN, PMFBY, Drip subsidy, Kisan Credit Card\n"
        "📊 **Market** — APMC prices, best time to sell\n"
        "Type your question in simple words — I will help! 😊"
    )


# ── Smart Answer Engine — works without IBM key ───────────────────────────────
def smart_answer(message: str) -> str:
    """
    Comprehensive keyword-based answer engine.
    Covers every common farmer question with specific, actionable answers.
    """
    intent = detect_intent(message)
    m = message.lower()

    # ── SCHEMES ──────────────────────────────────────────────────────────────
    if intent == "schemes":
        return demo_answer(message)   # demo_answer has good scheme answers

    # ── MARKET ───────────────────────────────────────────────────────────────
    if intent == "market":
        return demo_answer(message)   # demo_answer has good market answers

    # ── PEST & DISEASE ────────────────────────────────────────────────────────
    if intent == "pest":
        # ── Arecanut ──
        if any(w in m for w in ["koleroga","areca","supari","bunch rot","mahali"]):
            return (
                "🌿 **Arecanut Koleroga (Phytophthora Fruit Rot):**\n\n"
                "**Symptoms:** Bunches turn black, premature fruit drop, brown rot on stalk — mostly during monsoon.\n\n"
                "✅ **Treatment:**\n"
                "• Spray **Bordeaux mixture 1%** on bunches + stalk — June & July\n"
                "• Severe cases: Drench base with **Metalaxyl + Mancozeb 3g/L** water\n"
                "• Remove & burn all infected bunches immediately\n\n"
                "🛡️ **Prevention:** Spray Bordeaux before monsoon starts (May end)\n"
                "⏰ **Best spray time:** 6–9 AM · Wear gloves + mask\n"
                "📞 Help: Arecanut Research Station, Vitla, Karnataka"
            )
        # ── Coconut weevil ──
        if any(w in m for w in ["coconut weevil","red palm","weevil","bore hole"]):
            return (
                "🥥 **Coconut Red Palm Weevil:**\n\n"
                "**Symptoms:** Bore holes in trunk with brown frass, yellow drooping crown, wilting top leaves.\n\n"
                "✅ **Treatment:**\n"
                "• Inject **Chlorpyrifos 2ml/L** water into bore holes using syringe — seal with mud after\n"
                "• Install **4 pheromone traps per hectare** to catch adult weevils\n"
                "• Fill holes with **Carbaryl 10% dust + sand mixture**\n\n"
                "⚠️ **Severe attack:** Fell & burn infested palms to stop spread\n"
                "🛡️ **Prevention:** Keep crown clean, apply Chlorpyrifos 0.1% to crown monthly"
            )
        # ── Paddy blast ──
        if any(w in m for w in ["blast","paddy blast","grey lesion","neck rot","rice blast"]):
            return (
                "🌾 **Paddy Blast Disease:**\n\n"
                "**Symptoms:** Spindle-shaped grey/brown lesions on leaves; grey neck at panicle (neck rot).\n\n"
                "✅ **Treatment:**\n"
                "• Spray **Tricyclazole 75 WP — 0.6g per litre** water\n"
                "• Apply at **25 days** and **45 days** after transplanting\n"
                "• Alternative: **Carbendazim 1g/L** water\n\n"
                "🛡️ **Prevention:**\n"
                "• Use blast-resistant varieties (Samba Masuri BPT-5204, IR-64)\n"
                "• Avoid excess Nitrogen fertilizer\n"
                "• Do NOT keep waterlogged — use AWD (alternate wet & dry)"
            )
        # ── Banana wilt / Panama ──
        if any(w in m for w in ["banana wilt","panama","fusarium","pseudostem split"]):
            return (
                "🍌 **Banana Panama Wilt (Fusarium Wilt):**\n\n"
                "**Symptoms:** Yellowing starts from bottom leaves, pseudostem turns brown inside, splits.\n\n"
                "⚠️ **No chemical cure exists for Panama wilt.**\n\n"
                "✅ **Management:**\n"
                "• Remove and destroy infected plants immediately — do NOT compost\n"
                "• Apply **Trichoderma viride 50g per plant** in soil at planting\n"
                "• Use **wilt-resistant varieties** — Grand Naine (G9), Nendran, Robusta\n"
                "• Do NOT plant banana in same field for 2–3 seasons\n\n"
                "💡 G9 (Grand Naine) is Panama-resistant and gives best yield."
            )
        # ── Chilli thrips / mites ──
        if any(w in m for w in ["thrips","chilli pest","mite","curl","silver"]):
            return (
                "🌶️ **Chilli Thrips & Mite Management:**\n\n"
                "**Symptoms:** Curled/cupped leaves, silvery streaks on leaves, tiny insects visible.\n\n"
                "✅ **Treatment:**\n"
                "• **Spinosad 45 SC — 0.3ml per litre** water (organic option)\n"
                "• **Abamectin 1.9 EC — 0.5ml per litre** water (for mites)\n"
                "• **Imidacloprid 17.8 SL — 0.3ml per litre** (for heavy infestation)\n\n"
                "🔁 Alternate chemicals each spray to prevent resistance\n"
                "⏰ Spray at **6–9 AM** · Spray **bottom side of leaves** too\n"
                "🛡️ **Prevention:** Use yellow sticky traps (5 per acre)"
            )
        # ── Turmeric rhizome rot ──
        if any(w in m for w in ["turmeric rot","rhizome rot","collar rot","ginger rot"]):
            return (
                "🍂 **Turmeric / Ginger Rhizome Rot:**\n\n"
                "**Symptoms:** Yellow wilting from base, rotting at collar, foul smell from soil.\n\n"
                "✅ **Treatment:**\n"
                "• Drench soil with **Metalaxyl + Mancozeb 3g/L** water around affected plants\n"
                "• Remove infected plants with surrounding soil\n\n"
                "🛡️ **Prevention (most important):**\n"
                "• Treat seed rhizomes with **Metalaxyl 2g/L** before planting (30 min soak)\n"
                "• Grow on **raised beds (15–20cm)** — rhizome rot starts in waterlogged soil\n"
                "• Apply **Trichoderma 50g per pit** at planting\n"
                "• Ensure proper field drainage — never let water stagnate"
            )
        # ── Maize armyworm ──
        if any(w in m for w in ["armyworm","fall armyworm","maize pest","whorl","caterpillar"]):
            return (
                "🌽 **Maize Fall Armyworm (Spodoptera frugiperda):**\n\n"
                "**Symptoms:** Ragged/torn whorl leaves, caterpillars inside whorl, frass (powdery droppings) visible.\n\n"
                "✅ **Treatment:**\n"
                "• Apply **Emamectin benzoate 5 SG — 0.4g per litre** INTO the whorl\n"
                "• Apply at **15–18 days** after germination when caterpillars are small\n"
                "• Mix sand + insecticide and drop into whorl for better contact\n\n"
                "🌿 **Organic option:** Spray **Bt (Bacillus thuringiensis) 2g/L** — safe, effective\n"
                "⏰ Spray early morning · Repeat after 7 days if needed"
            )
        # ── Aphids ──
        if any(w in m for w in ["aphid","sticky","honeydew","yellow curl"]):
            return (
                "🐛 **Aphid Management (All Crops):**\n\n"
                "**Symptoms:** Clusters of tiny insects on new shoots/leaves, sticky honeydew, curled yellow leaves.\n\n"
                "✅ **Treatment:**\n"
                "• 🌿 **Organic:** Neem oil **3ml per litre** water + soap — spray on leaves & stem\n"
                "• 💊 **Chemical:** **Imidacloprid 0.3ml per litre** water\n"
                "• Strong water jet spray to wash them off\n\n"
                "🔁 **Repeat after 7 days** if still present\n"
                "⚠️ Wear gloves · spray early morning 6–9 AM"
            )
        # ── Coffee leaf rust ──
        if any(w in m for w in ["coffee rust","leaf rust","orange pustule","coffee disease"]):
            return (
                "☕ **Coffee Leaf Rust (Hemileia vastatrix):**\n\n"
                "**Symptoms:** Yellowish-orange powdery pustules on underside of leaves, premature leaf drop.\n\n"
                "✅ **Treatment:**\n"
                "• Spray **Copper oxychloride 3g per litre** water — cover leaf undersides\n"
                "• Systemic: **Propiconazole 1ml per litre** for severe attack\n"
                "• Spray at **onset of monsoon** (June) and after (September)\n\n"
                "🛡️ **Prevention:**\n"
                "• Maintain shade — excess sunlight increases rust severity\n"
                "• Avoid over-fertilizing with Nitrogen\n"
                "📞 Coffee Board India helpline: 080-25362161"
            )
        # ── Pepper phytophthora ──
        if any(w in m for w in ["pepper disease","pepper wilt","pepper rot","phytophthora pepper"]):
            return (
                "🫒 **Black Pepper Phytophthora (Quick Wilt):**\n\n"
                "**Symptoms:** Sudden yellowing, wilting, root rot, black lesions on vines.\n\n"
                "✅ **Treatment:**\n"
                "• Drench soil with **Metalaxyl 2g per litre** water (1–2L per vine)\n"
                "• Spray foliage with **Copper oxychloride 3g/L** water\n\n"
                "🛡️ **Prevention:**\n"
                "• Improve field drainage — grow on mounds or slopes\n"
                "• Apply **Trichoderma 100g per vine** in soil at planting\n"
                "• Avoid waterlogging near standards/supports"
            )
        # ── Generic pest answer ──
        return demo_answer(message)

    # ── FERTILIZER ───────────────────────────────────────────────────────────
    if intent == "fertilizer":
        FERT = {
            "arecanut":  "**Arecanut (bearing palm/year):**\n• Urea 200g + SSP 130g + MOP 130g + FYM 12kg per palm\n• Apply in **2 splits: June and September**\n• Borax 25g per palm (micronutrient)\n• Apply in a ring 1m from base, cover with soil",
            "coconut":   "**Coconut (per palm/year):**\n• Urea 1.3kg + SSP 2kg + MOP 2kg + FYM 50kg\n• Apply in **2 splits: June and December**\n• Apply in circular trench (1.5m radius from trunk)\n• Borax 50g + Ferrous sulfate 25g if showing deficiency",
            "banana":    "**Banana (per plant/crop):**\n• Urea 250g + DAP 100g + MOP 300g + FYM 10kg\n• Give in **4 splits** over 9 months\n• Best method: Drip fertigation saves 30% fertilizer\n• Critical: Never skip fertilizer at bunch shooting stage",
            "paddy":     "**Paddy/Rice (per hectare):**\n• NPK **120:60:60 kg/ha**\n• Full P (DAP) + K (MOP) at transplanting as basal\n• Nitrogen (Urea) in 3 splits: 25% basal + 50% at 21 days + 25% at panicle initiation\n• Do NOT apply Urea during heavy rain",
            "rice":      "**Rice/Paddy (per hectare):**\n• NPK **120:60:60 kg/ha**\n• Full P+K at transplanting. Urea in 3 splits.\n• 25% at transplanting + 50% at 21 days + 25% at panicle initiation",
            "sugarcane": "**Sugarcane (per hectare):**\n• NPK **250:115:115 kg/ha** in 3 splits\n• FYM 25 t/ha as basal before planting\n• Drip fertigation saves 40% water + gives 25% higher yield",
            "turmeric":  "**Turmeric (per hectare):**\n• NPK **150:50:100 kg/ha** + FYM 30 t/ha\n• Full P+K at planting. N in 2 splits: at planting + at 60 days\n• Borax 10kg/ha + ZnSO4 25kg/ha as micronutrients\n• Apply thick mulch after planting",
            "ginger":    "**Ginger (per hectare):**\n• NPK **75:50:75 kg/ha** + FYM 30 t/ha\n• ZnSO4 25kg/ha\n• Apply in 3 splits. Mulch with dry leaves after planting.",
            "chilli":    "**Chilli (per hectare):**\n• NPK **100:50:50 kg/ha** + FYM 20 t/ha\n• Boron spray **0.2%** at flowering improves fruit set by 20–30%\n• Drip fertigation gives best results",
            "maize":     "**Maize (per hectare):**\n• NPK **150:75:37.5 kg/ha**\n• Urea in 3 splits: at sowing + 30 days + 60 days\n• Apply Zinc sulfate 25kg/ha if zinc deficiency (white stripe on leaves)",
            "wheat":     "**Wheat (per hectare):**\n• NPK **120:60:40 kg/ha**\n• Half Urea at sowing + remaining at first irrigation (21 days)\n• Full P (DAP) + K (MOP) at sowing as basal",
            "onion":     "**Onion (per hectare):**\n• NPK **100:50:75 kg/ha** + Sulphur 25kg/ha\n• Apply N in 3 splits. **Stop all N after bulb formation** — excess N causes splitting\n• Sulphur improves pungency and shelf life",
            "tomato":    "**Tomato (per hectare):**\n• NPK **200:120:120 kg/ha** + FYM 25 t/ha\n• Boron 0.2% spray at flowering improves fruit set\n• Apply Calcium (CaNO3) to prevent blossom end rot",
            "coffee":    "**Coffee (per plant/year):**\n• Urea 250g + SSP 150g + MOP 200g + FYM 5kg\n• Apply in **2 splits: June and September**\n• Apply after blossom shower irrigation in March",
            "pepper":    "**Black Pepper (per vine/year):**\n• NPK 50:50:150g + FYM 5kg + Neem cake 1kg\n• Apply before monsoon (May) and after (October)\n• Neem cake prevents root rot and adds nutrients",
            "cotton":    "**Cotton (per hectare):**\n• NPK **150:75:75 kg/ha**\n• Stop excess Nitrogen after boll formation — causes late vegetative growth\n• Apply Boron 0.2% at squaring stage",
            "soybean":   "**Soybean (per hectare):**\n• NPK **20:60:40 kg/ha** (low N — soybean fixes its own N)\n• Rhizobium seed treatment before sowing\n• Apply Sulphur 20kg/ha for higher protein content",
            "groundnut": "**Groundnut (per hectare):**\n• NPK **25:50:75 kg/ha** + Gypsum 500kg/ha at pegging\n• Gypsum is critical for shell filling and preventing empty pods\n• Apply Boron 1kg/ha as micronutrient",
        }
        for crop, advice in FERT.items():
            if crop in m:
                return (
                    f"🧪 **Fertilizer Schedule — {crop.capitalize()}:**\n\n"
                    f"{advice}\n\n"
                    "💡 **Key fertilizers:**\n"
                    "• Urea = Nitrogen (N) — growth & green colour\n"
                    "• DAP/SSP = Phosphorus (P) — roots & flowers\n"
                    "• MOP = Potassium (K) — fruit size & disease resistance\n"
                    "🌱 *Get free soil test (Soil Health Card) from KVK for exact doses.*"
                )
        # General fertilizer question
        return (
            "🧪 **Fertilizer Guide for Indian Farmers:**\n\n"
            "📦 **What each fertilizer does:**\n"
            "• **Urea (46% N)** → Makes plants grow GREEN and tall. Top-dress application.\n"
            "• **DAP (18-46-0)** → Phosphorus for ROOT growth and early establishment.\n"
            "• **MOP (0-0-60)** → Potassium for BIG FRUITS, disease resistance.\n"
            "• **SSP (0-16-0+S)** → Cheaper source of Phosphorus + Sulphur.\n"
            "• **NPK 17:17:17** → Balanced, all growth stages.\n"
            "• **FYM/Compost** → Improves soil health, water holding.\n\n"
            "⚠️ **Golden rules:**\n"
            "• Do soil test first — avoid over-fertilizing\n"
            "• Split doses (2–3 times) — better uptake, less wastage\n"
            "• Never apply before heavy rain — gets washed away\n\n"
            "📞 **Ask crop-specific dose:** Tell me your crop name!\n"
            "🌱 *Free Soil Health Card from KVK gives exact fertilizer recommendations.*"
        )

    # ── IRRIGATION ────────────────────────────────────────────────────────────
    if intent == "irrigation":
        return demo_answer(message)   # demo_answer has excellent irrigation answers

    # ── SOIL ANALYSIS ─────────────────────────────────────────────────────────
    if intent == "soil":
        return demo_answer(message)   # demo_answer has good soil answers

    # ── CROP RECOMMENDATION ───────────────────────────────────────────────────
    if intent == "crop":
        # check specific crop questions first
        CROP_INFO = {
            "arecanut": (
                "🌿 **Arecanut (Supari) Farming:**\n\n"
                "📍 **Best regions:** Coastal Karnataka (Shivamogga, Udupi, DK), Kerala, Assam\n"
                "🌱 **Soil:** Well-drained laterite/red loam · pH 5.5–7.0\n"
                "📅 **Planting:** June–September · Spacing: 2.7m × 2.7m\n"
                "💰 **Price:** ₹36,000–₹52,000/quintal · Best market: Shivamogga APMC\n"
                "⏱️ **Starts bearing:** 5–7 years after planting\n"
                "🌧️ **Key risk:** Koleroga disease in monsoon — spray Bordeaux mixture 1% before June\n"
                "💧 **Irrigation:** 15–20L/palm/day in summer (March–May)\n"
                "🏛️ **Sell through:** CAMPCO cooperative or Shivamogga APMC"
            ),
            "coconut": (
                "🥥 **Coconut Farming:**\n\n"
                "📍 **Best regions:** Coastal Karnataka, Kerala, Tamil Nadu, Andhra Pradesh\n"
                "🌱 **Soil:** Sandy loam, laterite · pH 5.5–7.5\n"
                "📅 **Spacing:** 7.5m × 7.5m (triangular) · Starts bearing at 5–7 years\n"
                "💰 **Copra price:** ₹8,500–₹12,000/quintal · Best: Udupi, Thrissur, Pollachi\n"
                "💧 **Irrigation:** 200L/palm/week in summer\n"
                "🌿 **Intercrop:** Banana, Turmeric, Ginger between young palms for extra income\n"
                "🏛️ **Support:** CPCRI (Central Plantation Crops Research Institute)"
            ),
            "banana": (
                "🍌 **Banana Farming (G9 / Grand Naine):**\n\n"
                "📍 **Suitable:** All India · Especially Andhra Pradesh, Karnataka, Gujarat, Bihar\n"
                "🌱 **Variety:** G9 (Grand Naine) — 11 months, 25–35kg/bunch · Panama wilt resistant\n"
                "💰 **Price:** ₹900–₹1,600/quintal · Markets: Hoskote APMC (Bangalore), local\n"
                "💧 **Water:** Critical at bunch shooting — 15L/plant/day via drip\n"
                "🧪 **Fertilizer:** 250g Urea + 100g DAP + 300g MOP per plant over 9 months\n"
                "⚠️ **Risk:** Panama wilt — use resistant varieties, apply Trichoderma at planting"
            ),
            "paddy": (
                "🌾 **Paddy/Rice Farming:**\n\n"
                "📅 **Kharif paddy:** June–November · Rabi paddy (South India): Nov–April\n"
                "🌱 **Top varieties:** Samba Masuri (BPT-5204), Swarna, IR-64, MTU-7029\n"
                "💰 **MSP:** ₹2,183/quintal (2023-24) · Government procurement by FCI\n"
                "🧪 **Fertilizer:** NPK 120:60:60 kg/ha · Urea in 3 splits\n"
                "💧 **Water:** Maintain 3–5cm standing water during tillering\n"
                "🌿 **SRI method:** 30% higher yield · Less water · Use young seedlings (14 days)\n"
                "⚠️ **Key disease:** Blast — spray Tricyclazole 0.6g/L at 25 + 45 days"
            ),
            "coffee": (
                "☕ **Coffee Farming:**\n\n"
                "📍 **Best regions:** Kodagu (Coorg), Chikkamagaluru, Sakleshpur (Karnataka); Wayanad (Kerala)\n"
                "🌱 **Varieties:** Arabica (high quality, hills), Robusta (lowlands, higher yield)\n"
                "💰 **Price:** ₹5,000–₹8,000/quintal cherry · Organic certified fetches 2× premium\n"
                "💧 **Key irrigation:** Blossom shower 250L/plant in Feb–March triggers flowering\n"
                "⚠️ **Key disease:** Leaf rust — spray Copper oxychloride 3g/L at onset of monsoon\n"
                "🏛️ **Support:** Coffee Board India, Coorg & Chikkamagaluru markets"
            ),
            "turmeric": (
                "🍂 **Turmeric Farming:**\n\n"
                "📍 **Best regions:** Erode (TN), Nizamabad (TS), Coastal Karnataka, Odisha\n"
                "📅 **Planting:** April–June · Harvest: 8–9 months later\n"
                "💰 **Price:** ₹7,000–₹20,000/quintal · Best market: Erode APMC (Tamil Nadu)\n"
                "💡 **Tip:** Sell 3–6 months AFTER harvest for 30–40% better price\n"
                "🧪 **Fertilizer:** NPK 150:50:100 kg/ha + FYM 30t/ha\n"
                "⚠️ **Key risk:** Rhizome rot — grow on raised beds, treat seed with Metalaxyl\n"
                "🌱 **Intercrop:** Excellent intercrop under coconut/arecanut"
            ),
            "pepper": (
                "🫒 **Black Pepper Farming:**\n\n"
                "📍 **Best regions:** Kerala (Idukki, Wayanad), Coorg (Karnataka)\n"
                "💰 **Price:** ₹40,000–₹65,000/quintal · Best: Kochi, Kozhikode markets\n"
                "🌱 **Support:** Needs live standard (Erythrina/Silver oak) or dead standards\n"
                "🧪 **Fertilizer:** NPK 50:50:150g + FYM 5kg + Neem cake 1kg per vine/year\n"
                "⚠️ **Key risk:** Phytophthora quick wilt — improve drainage, drench with Metalaxyl\n"
                "🏛️ **Export help:** Spices Board India connects to exporters for premium price"
            ),
        }
        for crop, info in CROP_INFO.items():
            if crop in m:
                return info
        # Return season/region based crop advice
        return demo_answer(message)

    # ── GENERAL / UNKNOWN ─────────────────────────────────────────────────────
    # Try to find any crop keyword and give relevant KB answer
    all_crops = {
        "arecanut": "pest", "areca": "pest", "koleroga": "pest",
        "coconut": "pest", "paddy": "crop", "rice": "crop",
        "banana": "crop", "sugarcane": "irrigation", "coffee": "crop",
        "pepper": "crop", "turmeric": "crop", "ginger": "fertilizer",
        "chilli": "pest", "maize": "pest", "onion": "market",
        "wheat": "crop", "cotton": "crop", "tomato": "market",
        "soybean": "crop", "groundnut": "crop",
    }
    for crop, fallback_intent in all_crops.items():
        if crop in m:
            # Re-run with the found crop and its typical intent
            return smart_answer(f"{fallback_intent} question about {crop}: {message}")

    return (
        "🌿 **Namaste! I am your Kisan AI Farming Advisor.**\n\n"
        "I can answer questions about:\n\n"
        "🌿 **Crops** — Arecanut, Coconut, Paddy, Banana, Coffee, Turmeric, Ginger, Chilli, Pepper, Maize, Wheat, Onion\n"
        "🐛 **Pest & Disease** — Koleroga, Blast, Wilt, Armyworm, Aphids, Weevil\n"
        "🧪 **Fertilizer** — NPK doses, Urea, DAP, MOP schedules per crop\n"
        "💧 **Irrigation** — Drip, sprinkler, stage-wise water schedules\n"
        "📊 **Market Prices** — APMC mandi rates, best time to sell\n"
        "📋 **Govt Schemes** — PM-KISAN, PMFBY, Drip subsidy, Kisan Credit Card\n"
        "🪱 **Soil Health** — pH, NPK, soil type advice\n\n"
        "**Just ask your question in simple words!**\n"
        "Example: *'What is the fertilizer dose for arecanut?'*\n"
        "📞 Kisan Call Centre: **1800-180-1551** (Free, 24×7)"
    )


# ── IBM WatsonX ────────────────────────────────────────────────────────────────
_tok = {"token": "", "exp": 0}

async def get_iam_token() -> str:
    if _tok["token"] and time.time() < _tok["exp"]:
        return _tok["token"]
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.post(
            "https://iam.cloud.ibm.com/identity/token",
            data={"apikey": WATSONX_API_KEY, "grant_type": "urn:ibm:params:oauth:grant-type:apikey"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        r.raise_for_status()
        d = r.json()
        _tok["token"] = d["access_token"]
        _tok["exp"]   = time.time() + d.get("expires_in", 3600) - 60
    return _tok["token"]


def _extract_lang(message: str):
    """Pull out the language instruction appended by the frontend, return (clean_msg, lang_code)."""
    import re
    lang_map = {
        "hindi": "hi", "हिंदी": "hi",
        "kannada": "kn", "ಕನ್ನಡ": "kn",
        "tamil": "ta", "தமிழ்": "ta",
        "telugu": "te", "తెలుగు": "te",
        "marathi": "mr", "मराठी": "mr",
    }
    lang = "en"
    clean = message
    # Look for [Please reply in X ...] tag appended by frontend
    match = re.search(r'\[Please reply in (\w+)', message, re.IGNORECASE)
    if match:
        word = match.group(1).lower()
        for key, code in lang_map.items():
            if key in word or word in key:
                lang = code
                break
        # Remove the tag from the message
        clean = re.sub(r'\[Please reply in[^\]]+\]', '', message).strip()
    return clean, lang


# Pre-built translations for common responses (so even without IBM the farmer gets their language)
_LANG_GREET = {
    "hi": "नमस्ते किसान भाई! मैं आपका कृषि सलाहकार हूँ।",
    "kn": "ನಮಸ್ಕಾರ ರೈತ ಅಣ್ಣ! ನಾನು ನಿಮ್ಮ ಕೃಷಿ ಸಲಹೆಗಾರ.",
    "ta": "வணக்கம் விவசாயி! நான் உங்கள் வேளாண் ஆலோசகர்.",
    "te": "నమస్కారం రైతు అన్నా! నేను మీ వ్యవసాయ సలహాదారుడిని.",
    "mr": "नमस्कार शेतकरी बंधू! मी तुमचा कृषी सल्लागार आहे.",
}
_LANG_SUFFIX = {
    "hi": "\n\n_(हिंदी में उत्तर — IBM Granite AI द्वारा अनुवादित)_",
    "kn": "\n\n_(ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರ — IBM Granite AI ಅನುವಾದ)_",
    "ta": "\n\n_(தமிழில் பதில் — IBM Granite AI மொழிபெயர்ப்பு)_",
    "te": "\n\n_(తెలుగులో సమాధానం — IBM Granite AI అనువాదం)_",
    "mr": "\n\n_(मराठीत उत्तर — IBM Granite AI भाषांतर)_",
}


async def ask_granite(message: str) -> str:
    # Extract language preference and clean message
    clean_msg, lang = _extract_lang(message)

    # Always try IBM first if key looks real
    if WATSONX_API_KEY and "your-" not in WATSONX_API_KEY and "PASTE" not in WATSONX_API_KEY:
        context = "\n".join(KB.values())
        lang_instruction = ""
        if lang != "en":
            lang_names = {"hi":"Hindi","kn":"Kannada","ta":"Tamil","te":"Telugu","mr":"Marathi"}
            lang_instruction = f"\nIMPORTANT: Respond entirely in {lang_names.get(lang,'English')}."
        if "dataplatform" in WATSONX_URL:
            gen_url = f"{WATSONX_URL}/ml/v1/text/generation?version=2023-05-29"
        else:
            gen_url = f"{WATSONX_URL}/ml/v1/text/generation?version=2023-05-29"
        prompt = f"""You are Kisan AI, an expert Smart Farming Advisor for Indian farmers.
You know everything about: arecanut, coconut, paddy, banana, sugarcane, coffee, pepper, turmeric, ginger, onion, chilli, maize, wheat, cotton, soybean, vegetables.
Give a PRACTICAL, SPECIFIC answer the farmer can act on immediately.
Use bullet points. Use simple language. Use Indian units (quintal, per acre, per palm, kg/ha).
Mention exact product names, doses, timings where relevant.
Reference: APMC, KVK, ICAR, MSP prices, government schemes where helpful.{lang_instruction}

FARMING KNOWLEDGE BASE:
{context}

FARMER QUESTION: {clean_msg}

ANSWER:"""
        try:
            token = await get_iam_token()
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.post(
                    gen_url,
                    json={
                        "model_id": "ibm/granite-13b-instruct-v2",
                        "input": prompt,
                        "parameters": {
                            "decoding_method": "greedy",
                            "max_new_tokens": 500,
                            "temperature": 0.3,
                            "repetition_penalty": 1.1,
                            "stop_sequences": ["FARMER QUESTION:", "---"],
                        },
                        "project_id": WATSONX_PROJECT_ID,
                    },
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                )
                r.raise_for_status()
                text = r.json()["results"][0]["generated_text"].strip()
                if text and len(text) > 20:
                    return text
        except Exception as e:
            pass  # fall through to smart_answer below

    # Use smart_answer with the clean message (no lang tag)
    answer = smart_answer(clean_msg)
    # If non-English, append a note (answer is in English since no IBM, but note the language selection)
    if lang != "en":
        lang_names = {"hi":"Hindi (हिन्दी)","kn":"Kannada (ಕನ್ನಡ)","ta":"Tamil (தமிழ்)","te":"Telugu (తెలుగు)","mr":"Marathi (मराठी)"}
        note = (
            f"\n\n---\n"
            f"🌐 *You selected {lang_names.get(lang, lang)}. IBM Granite AI is needed for full {lang_names.get(lang, lang)} responses. "
            f"The answer above is in English. Connect IBM WatsonX to get answers in your language.*"
        )
        return answer + note
    return answer


# ── API ────────────────────────────────────────────────────────────────────────
class ChatReq(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(req: ChatReq):
    if not req.message.strip():
        return {"reply": "Please type a question."}
    return {"reply": await ask_granite(req.message)}


@app.get("/api/schemes")
async def get_schemes():
    return {"schemes": SCHEMES}


@app.get("/api/status")
async def status():
    ibm_ok = bool(WATSONX_API_KEY) and "your-" not in WATSONX_API_KEY and "PASTE" not in WATSONX_API_KEY
    return {
        "ibm_key": "✅ IBM Granite AI connected" if ibm_ok else "⚠️ Demo mode (no IBM key)",
    }


# ── Serve frontend ─────────────────────────────────────────────────────────────
FRONTEND = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(FRONTEND):
    app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("\nKisan AI - Smart Farming Advisor")
    print("Open in browser: http://localhost:8000")
    print("For mobile: use your computer IP, e.g. http://192.168.1.x:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
