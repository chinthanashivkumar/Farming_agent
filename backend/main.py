"""
Smart Farming Advisor â€” Simple Backend
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

# â”€â”€ Knowledge base â€” Indian crops focus â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
KB = {
    "crop": """
Kharif (Jun-Oct): Paddy/Rice, Maize, Soybean, Cotton, Groundnut, Bajra, Arhar, Turmeric, Ginger, Chilli (transplant).
Rabi (Nov-Mar): Wheat, Barley, Mustard, Gram, Onion (Rabi), Sunflower, Rabi Paddy (South India).
Summer (Apr-Jun): Sunflower, Moong, Watermelon, Cucumber, Sweet Corn, Vegetables.
Plantation crops (perennial): Arecanut, Coconut, Coffee, Black Pepper, Banana, Mango.
Spice crops: Turmeric, Ginger, Chilli, Pepper â€” high value, good demand.
Laterite soil (coastal Karnataka/Kerala): Arecanut, Coconut, Coffee, Pepper, Cashew, Rubber.
Black cotton soil: Cotton, Sorghum, Wheat, Sugarcane, Onion.
Alluvial soil (river plains): Wheat, Rice, Sugarcane, Vegetables.
Sandy loam: Groundnut, Maize, Turmeric, Ginger, Vegetables.
""",
    "pest": """
Arecanut Koleroga (Phytophthora): Bunches turn black, premature drop in monsoon. Spray Bordeaux mixture 1% in June-July. Drench with Metalaxyl+Mancozeb 3g/L.
Coconut Red Palm Weevil: Bore holes, frass in trunk, yellow crown. Inject Chlorpyrifos 2ml/L into holes. Use 4 pheromone traps per hectare.
Paddy Blast: Spindle-shaped grey lesions. Apply Tricyclazole 0.6g/L at 25 and 45 days after transplanting.
Banana Panama Wilt: Yellowing from bottom leaves, pseudostem splits. No chemical cure â€” use wilt-resistant varieties, apply Trichoderma.
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
Turmeric/Ginger: Requires good drainage â€” rhizome rot in waterlogged conditions. 4-5 irrigations in dry area.
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
Onion: Rs 1,000-2,800/quintal. Nashik APMC. Price volatile â€” consider FPO or cooperative selling.
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

# â”€â”€ Government Schemes data â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
SCHEMES = [
    {
        "id": "pm-kisan",
        "name": "PM-KISAN",
        "full_name": "Pradhan Mantri Kisan Samman Nidhi",
        "benefit": "â‚¹6,000/year",
        "description": "Annual income support in 3 installments of â‚¹2,000 each directly to farmer bank account.",
        "eligibility": "All land-holding farmers with valid Aadhaar and land records",
        "how_to_apply": "pmkisan.gov.in Â· Nearest CSC center Â· Bank branch",
        "category": "income",
        "icon": "ðŸ’°"
    },
    {
        "id": "pmfby",
        "name": "PMFBY",
        "full_name": "PM Fasal Bima Yojana",
        "benefit": "Crop Insurance",
        "description": "Subsidized crop insurance: 2% premium for Kharif, 1.5% for Rabi crops. Full sum insured on loss.",
        "eligibility": "All farmers growing notified crops. Loanee farmers enrolled automatically.",
        "how_to_apply": "Bank branch Â· CSC Â· pmfby.gov.in",
        "category": "insurance",
        "icon": "ðŸ›¡ï¸"
    },
    {
        "id": "pmksy",
        "name": "PM Krishi Sinchai Yojana",
        "full_name": "Pradhan Mantri Krishi Sinchai Yojana",
        "benefit": "45â€“55% subsidy on drip/sprinkler",
        "description": "Subsidy on micro-irrigation systems. Small farmers get 55% subsidy, others get 45%.",
        "eligibility": "All farmers. Apply before purchase of equipment.",
        "how_to_apply": "State Horticulture/Agriculture Dept Â· pmksy.gov.in",
        "category": "subsidy",
        "icon": "ðŸ’§"
    },
    {
        "id": "soil-health-card",
        "name": "Soil Health Card",
        "full_name": "Soil Health Card Scheme",
        "benefit": "Free soil testing",
        "description": "Free soil test and recommendations every 2 years. Know your soil's NPK, pH, and micronutrients.",
        "eligibility": "All farmers",
        "how_to_apply": "Nearest KVK Â· Agriculture Dept. office Â· soilhealth.dac.gov.in",
        "category": "advisory",
        "icon": "ðŸª±"
    },
    {
        "id": "kcc",
        "name": "Kisan Credit Card",
        "full_name": "Kisan Credit Card (KCC)",
        "benefit": "Crop loan at 4% interest",
        "description": "Short-term crop loans up to â‚¹3 lakh at 4% per annum (with interest subvention). No collateral up to â‚¹1.6 lakh.",
        "eligibility": "All farmers, sharecroppers, oral lessees",
        "how_to_apply": "Any nationalized bank Â· Regional Rural Bank Â· Co-operative bank",
        "category": "finance",
        "icon": "ðŸ¦"
    },
    {
        "id": "enam",
        "name": "e-NAM",
        "full_name": "National Agriculture Market",
        "benefit": "Better mandi prices",
        "description": "Online platform to sell crops across India. Transparent price discovery. No middlemen.",
        "eligibility": "All farmers. Requires Aadhaar + bank account.",
        "how_to_apply": "enam.gov.in Â· Nearest APMC office Â· Kisan Suvidha app",
        "category": "market",
        "icon": "ðŸ“±"
    },
    {
        "id": "rkvy",
        "name": "RKVY",
        "full_name": "Rashtriya Krishi Vikas Yojana",
        "benefit": "Agriculture development grants",
        "description": "Infrastructure, machinery, storage, and processing unit grants through state agriculture departments.",
        "eligibility": "Individual farmers and FPOs. Project-based applications.",
        "how_to_apply": "State Agriculture Department Â· District Collector office",
        "category": "subsidy",
        "icon": "ðŸ—ï¸"
    },
    {
        "id": "fpo",
        "name": "FPO Support",
        "full_name": "Farmer Producer Organization",
        "benefit": "â‚¹18 lakh grant per FPO",
        "description": "Form or join an FPO for collective bargaining, bulk input purchase, and better market prices.",
        "eligibility": "Minimum 300 farmers to form an FPO",
        "how_to_apply": "NABARD Â· SFAC Â· State Agriculture Dept",
        "category": "collective",
        "icon": "ðŸ‘¥"
    }
]

# â”€â”€ Intent detection â€” Indian crops aware â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def detect_intent(msg: str) -> str:
    m = msg.lower()
    # Explicit prefixes from the frontend â€” check these first before keyword matching
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


# â”€â”€ Demo answers â€” each intent gets a UNIQUE, specific answer â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def demo_answer(message: str) -> str:
    intent = detect_intent(message)
    msg    = message.lower()

    if intent == "schemes":
        if any(w in msg for w in ["pm-kisan", "pmkisan", "6000", "income support"]):
            return (
                "ðŸ’° **PM-KISAN â€” Pradhan Mantri Kisan Samman Nidhi:**\n\n"
                "âœ… **Benefit:** â‚¹6,000 per year in 3 installments of â‚¹2,000 each\n"
                "ðŸ‘¨â€ðŸŒ¾ **Who gets it:** All land-holding farmers with valid Aadhaar\n"
                "ðŸ“ **How to apply:**\n"
                "â€¢ Visit **pmkisan.gov.in** online\n"
                "â€¢ Go to nearest **CSC (Common Service Centre)**\n"
                "â€¢ Carry: Aadhaar + bank passbook + land documents\n\n"
                "ðŸ“ž Helpline: **155261** Â· Check status at pmkisan.gov.in"
            )
        if any(w in msg for w in ["pmfby", "fasal bima", "insurance", "crop insurance"]):
            return (
                "ðŸ›¡ï¸ **PMFBY â€” Pradhan Mantri Fasal Bima Yojana:**\n\n"
                "âœ… **Benefit:** Crop insurance at very low premium:\n"
                "â€¢ Kharif crops (Paddy, Maize, etc.) â†’ **2% premium only**\n"
                "â€¢ Rabi crops (Wheat, Onion, etc.) â†’ **1.5% premium only**\n"
                "â€¢ Rest paid by Government!\n\n"
                "ðŸ“ **How to apply:**\n"
                "â€¢ Apply at your **bank branch** before sowing season\n"
                "â€¢ Also at CSC center or pmfby.gov.in\n"
                "â€¢ **Loanee farmers** enrolled automatically\n\n"
                "âš ï¸ Covers: Drought, flood, pest attack, hailstorm, disease losses."
            )
        if any(w in msg for w in ["drip", "sinchai", "irrigation subsidy", "pmksy"]):
            return (
                "ðŸ’§ **PM Krishi Sinchai Yojana (PMKSY):**\n\n"
                "âœ… **Benefit:**\n"
                "â€¢ Small & marginal farmers: **55% subsidy** on drip/sprinkler system\n"
                "â€¢ Other farmers: **45% subsidy**\n\n"
                "ðŸ’° Drip system for 1 acre costs â‚¹35,000â€“â‚¹55,000 â€” you pay only half!\n\n"
                "ðŸ“ **How to apply:**\n"
                "â€¢ Visit state **Horticulture Department** office\n"
                "â€¢ Carry: Aadhaar + land documents + bank account\n"
                "â€¢ pmksy.gov.in for details\n\n"
                "ðŸ’¡ Drip irrigation saves 40â€“60% water and increases yield by 20â€“30%."
            )
        if any(w in msg for w in ["kcc", "kisan credit", "loan", "credit"]):
            return (
                "ðŸ¦ **Kisan Credit Card (KCC):**\n\n"
                "âœ… **Benefit:** Crop loans at **4% per annum** interest\n"
                "ðŸ’³ Up to **â‚¹3 lakh** without collateral\n\n"
                "ðŸ“ **How to apply:**\n"
                "â€¢ Visit any **nationalized bank**, RRB, or Co-operative bank\n"
                "â€¢ Carry: Aadhaar + land documents + passport photo\n"
                "â€¢ Approval usually within 2 weeks\n\n"
                "âœ… Covers: Crop inputs, maintenance, post-harvest expenses\n"
                "ðŸ“ž Bank helpline or **Kisan Call Centre: 1800-180-1551**"
            )
        return (
            "ðŸ“‹ **Government Schemes for Indian Farmers:**\n\n"
            "ðŸ’° **PM-KISAN** â€” â‚¹6,000/year income support â†’ pmkisan.gov.in\n"
            "ðŸ›¡ï¸ **PMFBY** â€” Crop insurance at 2% premium â†’ pmfby.gov.in\n"
            "ðŸ’§ **PMKSY** â€” 45â€“55% subsidy on drip irrigation â†’ pmksy.gov.in\n"
            "ðŸª± **Soil Health Card** â€” Free soil test â†’ soilhealth.dac.gov.in\n"
            "ðŸ¦ **Kisan Credit Card** â€” Crop loans at 4% â†’ Any bank\n"
            "ðŸ“± **e-NAM** â€” Sell crops online at better price â†’ enam.gov.in\n"
            "ðŸ‘¥ **FPO** â€” Join farmer group for better market prices\n\n"
            "ðŸ“ž **Kisan Call Centre: 1800-180-1551** (Free, 24Ã—7 in local language)"
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

        lines = ["ðŸª± **Soil Test Analysis Result:**\n"]

        # pH section
        if ph_val:
            if ph_val < 5.5:
                lines.append(f"ðŸ”´ **pH {ph_val} â€” Too Acidic**\nâ€¢ Apply **Agricultural Lime** 2â€“3 bags (100 kg each) per acre\nâ€¢ Wait 2â€“3 weeks after liming before sowing\nâ€¢ Good for: Paddy can still grow, but apply lime first")
            elif ph_val > 7.5:
                lines.append(f"ðŸŸ¡ **pH {ph_val} â€” Alkaline**\nâ€¢ Apply **Gypsum** 1â€“2 bags per acre to reduce pH\nâ€¢ Add FYM 10 kg/tree or 5 t/acre to improve structure")
            else:
                lines.append(f"ðŸŸ¢ **pH {ph_val} â€” Optimal!** Most crops grow well at this pH âœ…")
        else:
            lines.append("ðŸ“Š **pH:** Not provided â€” get a Soil Health Card for free pH testing")

        # NPK section
        lines.append("\nðŸ“‹ **NPK Status & Correction:**")
        if n_val is not None:
            if n_val < 280:   lines.append(f"â€¢ ðŸ”´ Nitrogen {n_val} kg/ha = LOW â†’ Apply **Urea 50 kg/acre** or FYM 2 trolleys")
            elif n_val < 560: lines.append(f"â€¢ ðŸŸ¡ Nitrogen {n_val} kg/ha = MEDIUM â†’ Apply **Urea 25 kg/acre** at sowing")
            else:             lines.append(f"â€¢ ðŸŸ¢ Nitrogen {n_val} kg/ha = HIGH â€” No Urea needed now")
        else:
            lines.append("â€¢ Nitrogen: Not tested â†’ Typical correction: Urea 40â€“50 kg/acre")
        if p_val is not None:
            if p_val < 10:    lines.append(f"â€¢ ðŸ”´ Phosphorus {p_val} kg/ha = LOW â†’ Apply **DAP 1 bag (50 kg)/acre** at sowing")
            elif p_val < 25:  lines.append(f"â€¢ ðŸŸ¡ Phosphorus {p_val} kg/ha = MEDIUM â†’ Apply **SSP 1 bag/acre**")
            else:             lines.append(f"â€¢ ðŸŸ¢ Phosphorus {p_val} kg/ha = HIGH â€” No DAP needed")
        if k_val is not None:
            if k_val < 110:   lines.append(f"â€¢ ðŸ”´ Potassium {k_val} kg/ha = LOW â†’ Apply **MOP 25 kg/acre** at fruiting stage")
            elif k_val < 280: lines.append(f"â€¢ ðŸŸ¡ Potassium {k_val} kg/ha = MEDIUM â†’ Apply **MOP 15 kg/acre**")
            else:             lines.append(f"â€¢ ðŸŸ¢ Potassium {k_val} kg/ha = HIGH â€” MOP not required")
        if oc_val is not None:
            if oc_val < 0.5:  lines.append(f"â€¢ ðŸ”´ Organic Carbon {oc_val}% = LOW â†’ Add **Vermicompost 500 kg/acre** + FYM 2 t/acre every year")
            elif oc_val < 0.75: lines.append(f"â€¢ ðŸŸ¡ Organic Carbon {oc_val}% = MEDIUM â†’ Add FYM 1 t/acre")
            else:             lines.append(f"â€¢ ðŸŸ¢ Organic Carbon {oc_val}% = GOOD âœ…")

        lines.append("\nðŸ’¡ *Get a **free Soil Health Card** from your nearest KVK (Krishi Vigyan Kendra). Test every 2 years.*")
        return "\n".join(lines)

    if intent == "pest":
        if any(w in msg for w in ["koleroga", "arecanut", "areca", "bunch rot", "phytophthora"]):
            return (
                "ðŸŒ¿ **Arecanut Koleroga (Fruit Rot):**\n\n"
                "**What you see:** Bunches turning black, premature fruit drop during monsoon\n\n"
                "âœ… **Treatment:**\n"
                "â€¢ ðŸŒ¿ **Bordeaux mixture 1%** â€” spray on bunches + stalk (June-July)\n"
                "â€¢ ðŸ’Š **Metalaxyl + Mancozeb 3g/L** â€” drench at base if severe\n"
                "â€¢ âœ‚ï¸ Remove and burn infected bunches immediately\n\n"
                "ðŸ›¡ï¸ **Prevention:** Spray Bordeaux mixture *before monsoon starts* (May)\n"
                "âš ï¸ Best spray time: 6â€“9 AM. Wear mask and gloves.\n"
                "ðŸ“ž Contact: Arecanut Research Station, Vitla (Karnataka)"
            )
        if any(w in msg for w in ["aphid", "sticky", "yellow leaves", "curled"]):
            return (
                "ðŸ› **Looks like APHIDS!**\n\n"
                "**What you see:** Curled yellow leaves, sticky liquid on leaves\n\n"
                "âœ… **Simple Treatment:**\n"
                "â€¢ ðŸŒ¿ **Natural:** Mix **3ml neem oil** in 1 litre water, spray on leaves (bottom side too)\n"
                "â€¢ ðŸ’Š **Chemical:** **Imidacloprid** â€” 0.3 ml in 1 litre water\n"
                "â€¢ ðŸš¿ Spray with strong water jet to wash them off\n\n"
                "âš ï¸ **Safety:** Wear gloves. Spray in early morning (6â€“9 AM).\n"
                "ðŸ” Repeat after 7 days if still present."
            )
        if any(w in msg for w in ["blast", "grey lesion", "spindle", "neck rot"]):
            return (
                "ðŸŒ¾ **Paddy Blast Disease:**\n\n"
                "**What you see:** Spindle-shaped grey or brown lesions on leaves, grey neck at panicle\n\n"
                "âœ… **Treatment:**\n"
                "â€¢ ðŸ’Š **Tricyclazole 75 WP** â€” 0.6g/L water. Spray at 25 and 45 days after transplanting.\n"
                "â€¢ ðŸ’Š **Carbendazim** â€” 1g/L as alternative\n"
                "â€¢ âœ‚ï¸ Remove infected tillers\n\n"
                "ðŸ›¡ï¸ **Prevention:**\n"
                "â€¢ Use blast-resistant varieties (Samba Masuri, BPT-5204)\n"
                "â€¢ Avoid excess Nitrogen fertilizer\n"
                "â€¢ Do NOT waterlog â€” maintain alternate wetting and drying"
            )
        if any(w in msg for w in ["bollworm", "hole", "boll", "cotton", "frass"]):
            return (
                "ðŸ› **Looks like BOLLWORM!**\n\n"
                "âœ… **Simple Treatment:**\n"
                "â€¢ ðŸŸ¢ **Organic:** Spray **Bt (Bacillus thuringiensis)** â€” safe for humans\n"
                "â€¢ ðŸ’Š **Chemical:** **Emamectin benzoate** â€” 0.4g per litre water\n"
                "â€¢ ðŸª¤ Put **pheromone traps** in field to catch adult moths\n\n"
                "âš ï¸ **Safety:** Do not spray during flowering. Wear mask while spraying."
            )
        if any(w in msg for w in ["weevil", "coconut weevil", "red palm"]):
            return (
                "ðŸ¥¥ **Coconut Red Palm Weevil:**\n\n"
                "**What you see:** Bore holes in trunk, frass oozing, yellow drooping crown\n\n"
                "âœ… **Treatment:**\n"
                "â€¢ ðŸ’Š **Inject Chlorpyrifos 2ml/L** into bore holes using syringe. Seal with mud.\n"
                "â€¢ ðŸª¤ Install **4 pheromone traps per hectare** to catch adults\n"
                "â€¢ ðŸŒ¿ Fill holes with **Carbaryl 10% dust + sand**\n\n"
                "âš ï¸ **Severe infestation:** Fell and destroy infested palms. Burning is best.\n"
                "ðŸ›¡ï¸ **Prevention:** Keep crown clean. Apply Chlorpyrifos 0.1% to crown area."
            )
        # Generic pest answer
        return (
            "ðŸ› **Pest & Disease Guide for Farmers:**\n\n"
            "**Common Indian Crop Problems & Quick Fix:**\n\n"
            "ðŸŒ¿ **Arecanut Koleroga** â†’ Bordeaux mixture 1% spray before monsoon\n"
            "ðŸ¥¥ **Coconut Weevil** â†’ Chlorpyrifos injection + pheromone traps\n"
            "ðŸŒ¾ **Paddy Blast** â†’ Tricyclazole 0.6g/L at 25 + 45 days\n"
            "ðŸŒ **Banana Wilt** â†’ Remove infected plants, plant Trichoderma\n"
            "ðŸŒ¶ï¸ **Chilli Thrips** â†’ Spinosad 0.3ml/L or Abamectin\n"
            "ðŸ‚ **Turmeric Rhizome Rot** â†’ Metalaxyl seed treatment\n"
            "ðŸŒ½ **Maize Armyworm** â†’ Emamectin 0.4g/L into whorl\n\n"
            "âš ï¸ **Always:** Wear gloves + mask. Spray early morning 6â€“9 AM."
        )

    if intent == "fertilizer":
        crop_hint = ""
        for crop in ["arecanut","coconut","banana","paddy","rice","sugarcane","turmeric","ginger","chilli","maize","onion","wheat","tomato","cotton","potato","pepper","coffee"]:
            if crop in msg:
                doses = {
                    "arecanut":  "**200g Urea + 130g SSP + 130g MOP + 12kg FYM** per palm per year. Apply in June and September splits.",
                    "coconut":   "**1.3kg Urea + 2kg SSP + 2kg MOP + 50kg FYM** per palm per year. Apply June and December.",
                    "banana":    "**250g Urea + 100g DAP + 300g MOP + 10kg FYM** per plant. Give in 4 splits. Drip fertigation is best.",
                    "paddy":     "NPK **120:60:60** kg/ha â†’ Full P+K at transplanting. N in 3 splits: 25%+50%+25%",
                    "rice":      "NPK **120:60:60** kg/ha â†’ Full P+K at transplanting. N in 3 splits: 25%+50%+25%",
                    "sugarcane": "NPK **250:115:115** kg/ha in 3 splits. FYM 25t/ha basal. Drip fertigation recommended.",
                    "turmeric":  "NPK **150:50:100** kg/ha + FYM 30t/ha. Apply Borax 10kg/ha + ZnSO4 25kg/ha.",
                    "ginger":    "NPK **75:50:75** kg/ha + FYM 30t/ha. Apply ZnSO4 25kg/ha. Mulch after planting.",
                    "chilli":    "NPK **100:50:50** kg/ha. Boron spray 0.2% at flowering. Drip fertigation improves yield.",
                    "maize":     "NPK **150:75:37** kg/ha. Urea in 3 splits at sowing, 30 days, 60 days.",
                    "onion":     "NPK **100:50:75** kg/ha + Sulphur 25kg/ha. Avoid N after bulb formation.",
                    "wheat":     "NPK **120:60:40** kg/ha â†’ Half Urea at sowing + rest at first irrigation (21 days)",
                    "tomato":    "NPK **200:120:120** kg/ha + FYM 25t/ha + Boron 0.2% spray at flowering",
                    "cotton":    "NPK **150:75:75** kg/ha â†’ Stop excess N after boll formation",
                    "potato":    "NPK **150:80:100** kg/ha. Full dose at planting. Earthing up at 30 days.",
                    "pepper":    "**NPK 50:50:150g** per vine (bearing). Apply FYM 5kg + Neem cake 1kg per vine.",
                    "coffee":    "**Urea 250g + SSP 150g + MOP 200g** per plant per year. Apply June and September.",
                }
                crop_hint = f"\n\nðŸŒ¾ **For {crop.capitalize()}:**\n{doses.get(crop,'')}"
                break
        return (
            "ðŸ§ª **Fertilizer Guide:**\n\n"
            "ðŸ“¦ **What each fertilizer does:**\n"
            "â€¢ **Urea** = Gives Nitrogen (N) â†’ Makes plant grow GREEN and tall\n"
            "â€¢ **DAP** = Gives N + Phosphorus (P) â†’ Helps roots grow strong\n"
            "â€¢ **MOP** = Gives Potassium (K) â†’ Makes fruits bigger and tastier\n"
            "â€¢ **FYM/Compost** = Improves soil health naturally\n"
            + crop_hint +
            "\n\nâš ï¸ **Golden Rule:** Do a soil test first. Too much fertilizer = wasted money + harms soil.\n"
            "ðŸ’¡ Apply in 2â€“3 split doses. Never apply before heavy rain."
        )

    if intent == "irrigation":
        # Give a full dedicated plan for each important crop
        if any(w in msg for w in ["arecanut","areca","supari","betel nut"]):
            return (
                "ðŸ’§ **Arecanut Irrigation Plan:**\n\n"
                "ðŸ“… **Monthly schedule:**\n"
                "â€¢ **Novâ€“Feb (cool/dry):** 15â€“20 litres per palm every **3â€“4 days**\n"
                "â€¢ **Marâ€“May (summer):** 20â€“25 litres per palm **every day** or alternate day\n"
                "â€¢ **Junâ€“Oct (monsoon):** No irrigation needed if rainfall > 50mm/week\n\n"
                "ðŸ’§ **Best method:** Drip irrigation at base of palm â€” saves 50% water\n"
                "â€¢ Drip flow rate: 4â€“8 litres/hour per emitter\n"
                "â€¢ Basin irrigation: Make 1m wide, 15cm deep basin around palm\n\n"
                "âš ï¸ **Critical stages needing most water:**\n"
                "â€¢ Bunch development (Marâ€“May) â€” never let soil dry completely\n"
                "â€¢ Nut filling stage â€” maintain soil moisture at 60â€“70%\n\n"
                "ðŸ’¡ **Mulching:** Apply 10â€“15 kg coir pith or dry leaves around base. Saves 40% water.\n"
                "ðŸ›ï¸ **Subsidy:** PM Krishi Sinchai Yojana gives 55% subsidy on drip systems."
            )
        if any(w in msg for w in ["coconut","nariyal","tengu","copra"]):
            return (
                "ðŸ’§ **Coconut Irrigation Plan:**\n\n"
                "ðŸ“… **Seasonal schedule:**\n"
                "â€¢ **Decâ€“Feb:** 40â€“50 litres per palm every **5â€“6 days**\n"
                "â€¢ **Marâ€“May (peak summer):** 100â€“200 litres per palm every **3â€“4 days**\n"
                "â€¢ **Junâ€“Oct (monsoon):** No irrigation if rain is adequate\n\n"
                "ðŸ’§ **Methods:**\n"
                "â€¢ Basin: 1.5m radius, 20cm deep basin around trunk\n"
                "â€¢ Drip: 2 emitters at 1m from trunk, 8 litres/hour each\n"
                "â€¢ Pot irrigation (coastal): bury pot near roots, fill weekly\n\n"
                "âš ï¸ **Signs of water stress:** Yellow leaves, reduced nut size, premature nut drop\n"
                "ðŸ’¡ Mulch with coir pith 20â€“25 kg per palm to retain moisture."
            )
        if any(w in msg for w in ["paddy","rice"]):
            return (
                "ðŸ’§ **Paddy / Rice Irrigation Plan:**\n\n"
                "ðŸ“… **Stage-wise water management:**\n"
                "â€¢ **Transplanting:** Keep 2â€“3 cm standing water for 7 days\n"
                "â€¢ **Tillering (day 10â€“30):** 3â€“5 cm standing water â€” critical stage!\n"
                "â€¢ **Panicle initiation (day 50â€“60):** 5 cm water â€” never let dry\n"
                "â€¢ **Flowering/heading:** 3â€“5 cm water continuously\n"
                "â€¢ **Grain filling:** Reduce to 2 cm, then allow to dry\n"
                "â€¢ **2 weeks before harvest:** Drain field completely\n\n"
                "ðŸ’¡ **AWD method (saves 30% water):**\n"
                "â€¢ Install perforated pipe 20cm deep in field\n"
                "â€¢ Irrigate only when water level drops 15cm below surface\n\n"
                "âš ï¸ Total water needed: 1200â€“1800mm per crop season"
            )
        if any(w in msg for w in ["banana","kela","bale","plantain"]):
            return (
                "ðŸ’§ **Banana Irrigation Plan:**\n\n"
                "ðŸ“… **Stage-wise schedule:**\n"
                "â€¢ **Planting to 3 months:** 8 litres per plant every **2â€“3 days**\n"
                "â€¢ **Vegetative (3â€“7 months):** 10â€“12 litres per plant daily\n"
                "â€¢ **Bunch shooting (critical):** 15 litres per plant daily â€” never skip!\n"
                "â€¢ **Bunch development to harvest:** 12 litres per plant daily\n\n"
                "ðŸ’§ **Best method:** Drip irrigation â€” 2 emitters per plant at 30cm from base\n"
                "â€¢ Saves 40% water vs flood irrigation\n"
                "â€¢ Can do fertigation (fertilizer + water together)\n\n"
                "âš ï¸ **Critical:** Water stress at shooting reduces bunch weight by 30â€“40%\n"
                "ðŸ’¡ Mulch with dry leaves/sugarcane trash to save moisture."
            )
        if any(w in msg for w in ["sugarcane","ganna"]):
            return (
                "ðŸ’§ **Sugarcane Irrigation Plan:**\n\n"
                "ðŸ“… **Stage-wise schedule:**\n"
                "â€¢ **Germination (0â€“30 days):** Light irrigation every 7â€“10 days\n"
                "â€¢ **Tillering (1â€“3 months):** Every 10â€“12 days\n"
                "â€¢ **Grand growth (3â€“7 months):** Every 7â€“10 days â€” maximum water need\n"
                "â€¢ **Maturity (7â€“10 months):** Every 15â€“20 days, reduce gradually\n\n"
                "ðŸ’§ **Drip irrigation:**\n"
                "â€¢ 8â€“10 litres per plant per day via inline drip\n"
                "â€¢ 40% water saving vs furrow irrigation\n"
                "â€¢ 25% higher yield with drip + fertigation\n\n"
                "âš ï¸ Total water: 1500â€“2000mm per season\n"
                "ðŸ›ï¸ **Subsidy:** PMKSY gives 55% subsidy on drip for sugarcane."
            )
        if any(w in msg for w in ["turmeric","haldi"]):
            return (
                "ðŸ’§ **Turmeric Irrigation Plan:**\n\n"
                "ðŸ“… **Schedule:**\n"
                "â€¢ **After planting (Mayâ€“Jun):** Irrigate immediately after planting\n"
                "â€¢ **Vegetative phase:** Every **7â€“10 days** in dry weather\n"
                "â€¢ **Rhizome development (Augâ€“Oct):** Every **5â€“7 days** â€” critical!\n"
                "â€¢ **Monsoon:** No irrigation if adequate rain\n\n"
                "âš ï¸ **Most important:** Turmeric must NOT be waterlogged â€” causes rhizome rot!\n"
                "â€¢ Grow on raised beds (15â€“20cm) for good drainage\n"
                "â€¢ Total irrigations needed: 15â€“20 times in 8-month crop\n\n"
                "ðŸ’¡ Apply thick mulch (sugarcane trash/dry leaves) after planting â€” saves 60% water."
            )
        if any(w in msg for w in ["coffee"]):
            return (
                "ðŸ’§ **Coffee Irrigation Plan:**\n\n"
                "ðŸ“… **Schedule:**\n"
                "â€¢ **Blossom shower (Febâ€“Mar):** 1â€“2 heavy irrigations of 250 litres/plant to trigger flowering\n"
                "â€¢ **Berry development (Aprâ€“Jun):** 1 irrigation every 10â€“15 days\n"
                "â€¢ **Monsoon (Junâ€“Sep):** No irrigation needed\n"
                "â€¢ **Post-monsoon (Octâ€“Nov):** Stop irrigation to harden berries for harvest\n\n"
                "ðŸ’§ **Method:** Overhead sprinkler or basin. Drip not preferred.\n"
                "âš ï¸ Over-irrigation causes root rot and berry drop\n"
                "ðŸ’¡ Coffee shade trees reduce water need by 30â€“40%."
            )
        if any(w in msg for w in ["pepper","black pepper","kali mirch"]):
            return (
                "ðŸ’§ **Black Pepper Irrigation Plan:**\n\n"
                "ðŸ“… **Schedule:**\n"
                "â€¢ **Dry season (Decâ€“May):** 2â€“3 irrigations per month â€” 10 litres per vine\n"
                "â€¢ **Flowering (Febâ€“Apr):** Regular moisture critical for spike setting\n"
                "â€¢ **Monsoon (Junâ€“Oct):** No irrigation â€” ensure drainage around standards\n\n"
                "âš ï¸ **Do NOT over-irrigate** â€” waterlogging causes Phytophthora collar rot\n"
                "â€¢ Grow on well-drained slopes or raised mounds\n"
                "ðŸ’¡ Mulch with dry leaves to retain moisture in dry season."
            )
        if any(w in msg for w in ["chilli","mirchi","capsicum"]):
            return (
                "ðŸ’§ **Chilli Irrigation Plan:**\n\n"
                "ðŸ“… **Stage-wise schedule:**\n"
                "â€¢ **Transplanting:** Irrigate immediately after transplanting\n"
                "â€¢ **Establishment (0â€“30 days):** Every **4â€“5 days**\n"
                "â€¢ **Flowering (45â€“60 days):** Every **3â€“4 days** â€” critical stage!\n"
                "â€¢ **Fruit setting & filling:** Every **4â€“5 days**\n"
                "â€¢ **Before harvest:** Reduce irrigation to improve colour and drying\n\n"
                "ðŸ’§ **Best method:** Drip irrigation â€” 3â€“4 litres per plant per day\n"
                "âš ï¸ Water stress at flowering causes blossom drop and fruit abortion\n"
                "ðŸ’¡ Boron spray 0.2% at flowering improves fruit set."
            )
        if any(w in msg for w in ["onion","pyaz"]):
            return (
                "ðŸ’§ **Onion Irrigation Plan:**\n\n"
                "ðŸ“… **Stage-wise schedule:**\n"
                "â€¢ **After transplanting:** Light irrigation every **4â€“5 days**\n"
                "â€¢ **Bulb development (45â€“90 days):** Every **5â€“7 days** â€” critical!\n"
                "â€¢ **3 weeks before harvest:** Stop all irrigation to allow skin to form\n\n"
                "ðŸ’§ Sprinkler irrigation gives best results for onion\n"
                "âš ï¸ Over-irrigation causes purple blotch disease and neck rot\n"
                "âš ï¸ Do NOT irrigate after bulb maturity â€” causes double bulbs"
            )
        # Generic irrigation guide for any other crop
        crop_name = ""
        for c in ["maize","wheat","cotton","soybean","groundnut","tomato","potato","ginger"]:
            if c in msg: crop_name = c.capitalize(); break
        generic_tip = f" For **{crop_name}**:" if crop_name else ""
        return (
            f"ðŸ’§ **Irrigation Guide{generic_tip}**\n\n"
            "â° **Best time to irrigate:** Early morning (5â€“8 AM) or evening (5â€“7 PM)\n\n"
            "ðŸ“Š **Frequency by soil type:**\n"
            "â€¢ Sandy soil â†’ Every **3â€“4 days**\n"
            "â€¢ Loamy soil â†’ Every **5â€“6 days**\n"
            "â€¢ Clay soil  â†’ Every **7â€“8 days**\n\n"
            "ðŸ“‹ **Critical growth stages needing most water:**\n"
            "â€¢ Germination/transplanting â€” always irrigate immediately\n"
            "â€¢ Flowering stage â€” never let soil dry out\n"
            "â€¢ Fruit/grain filling â€” maintain 60â€“70% soil moisture\n\n"
            "ðŸ’¡ **Tips:**\n"
            "â€¢ Drip irrigation saves **40â€“60%** water vs flood\n"
            "â€¢ Mulching reduces water loss by 30â€“40%\n"
            "â€¢ Skip irrigation if 10+ mm rain expected\n"
            "â€¢ Finger test: push finger 5cm into soil â€” if dry, irrigate now\n\n"
            "ðŸ›ï¸ PMKSY gives 55% subsidy on drip systems â€” apply at Horticulture Dept."
        )

    if intent == "market":
        crop_hint = ""
        prices = {
            "arecanut": ("â‚¹36,000â€“â‚¹52,000", "Best market: Shivamogga APMC (Karnataka). CAMPCO cooperative offers fair prices. Peak price: Marchâ€“June."),
            "coconut":  ("â‚¹8,500â€“â‚¹12,000 (copra)", "Markets: Udupi, Coimbatore, Thrissur. Value addition as virgin coconut oil fetches premium."),
            "banana":   ("â‚¹900â€“â‚¹1,600", "Hoskote, Bangalore APMC. G9 variety preferred. Contract farming available."),
            "paddy":    ("â‚¹2,183 (MSP)", "Government MSP procurement. Sell at FCI or state agency. Check APMC for premium varieties."),
            "rice":     ("â‚¹2,183 (MSP)", "Government MSP available. Check APMC for Samba Masuri (BPT-5204) premium."),
            "turmeric": ("â‚¹7,000â€“â‚¹20,000", "Best market: Erode (TN), Nizamabad (TS). Sell 3â€“6 months after harvest for better price."),
            "pepper":   ("â‚¹40,000â€“â‚¹65,000", "Markets: Kochi, Kozhikode (Kerala). Spices Board India helps export. Organic fetches 2â€“3x premium."),
            "ginger":   ("â‚¹15,000â€“â‚¹35,000 (dry)", "Sell dried ginger for better price. Calicut, Cochin markets. Export quality commands premium."),
            "chilli":   ("â‚¹8,000â€“â‚¹22,000", "Guntur APMC (AP) is largest chilli market. Grade Teja variety separately for best price."),
            "onion":    ("â‚¹1,000â€“â‚¹2,800", "Nashik APMC. Price very volatile. FPO collective selling gives better price."),
            "sugarcane":("FRP â‚¹315/qt (2023-24)", "Sell to sugar factory linked to your area. FRP (Fair and Remunerative Price) is guaranteed."),
            "wheat":    ("â‚¹2,275 (MSP)", "Government MSP available. Sell at FCI or registered mandi."),
            "coffee":   ("â‚¹5,000â€“â‚¹8,000 (cherry)", "Coffee Board India, Coorg/Chikkamagaluru markets. Organic certification fetches premium."),
            "tomato":   ("â‚¹500â€“â‚¹5,000", "Highly volatile. Sell Febâ€“May for best price. Bangalore APMC. Consider contract farming."),
            "cotton":   ("â‚¹6,500/qt MSP", "Cotton Corporation of India or APMC mandi. Grade Bt cotton separately."),
            "soybean":  ("â‚¹4,600/qt MSP", "Best selling Octâ€“Dec. Avoid immediate post-harvest sale."),
        }
        for crop, (price, tip) in prices.items():
            if crop in msg:
                crop_hint = f"\n\nðŸ“ **{crop.capitalize()} price:** {price}/quintal\nðŸ’¡ {tip}"
                break
        return (
            "ðŸ“Š **Indian APMC Market Prices:**\n\n"
            "ðŸª **Key prices** *(indicative â€” check agmarknet.nic.in for live rates)*:\n"
            "â€¢ ðŸŒ¿ Arecanut: **â‚¹36,000â€“â‚¹52,000**/qt (Shivamogga)\n"
            "â€¢ ðŸ¥¥ Coconut copra: **â‚¹8,500â€“â‚¹12,000**/qt\n"
            "â€¢ ðŸŒ Banana (G9): **â‚¹900â€“â‚¹1,600**/qt\n"
            "â€¢ ðŸŒ¾ Paddy: **â‚¹2,183** (MSP)\n"
            "â€¢ ðŸ‚ Turmeric: **â‚¹7,000â€“â‚¹20,000**/qt (Erode)\n"
            "â€¢ ðŸŒ¶ï¸ Chilli: **â‚¹8,000â€“â‚¹22,000**/qt (Guntur)\n"
            "â€¢ ðŸ«’ Pepper: **â‚¹40,000â€“â‚¹65,000**/qt (Kochi)\n"
            + crop_hint +
            "\n\nðŸ“± **Check live prices:**\n"
            "â€¢ agmarknet.nic.in Â· e-NAM app Â· Kisan Suvidha app\n"
            "â€¢ ðŸ“ž Kisan Call Centre: **1800-180-1551** (Free)"
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
                    "ðŸŒ¿ **Best Plantation Crops for Karnataka:**\n\n"
                    "1. **Arecanut (Supari)** ðŸŒ¿ â€” Best crop for coastal & Malnad Karnataka\n"
                    "   â€¢ Yield: 2â€“4 kg dry/palm/year Â· Price: â‚¹36,000â€“â‚¹52,000/qt Â· Market: Shivamogga APMC\n"
                    "   â€¢ âš ï¸ Risk: Koleroga in monsoon â€” spray Bordeaux mixture before June\n\n"
                    "2. **Coconut** ðŸ¥¥ â€” Excellent for coastal Karnataka\n"
                    "   â€¢ Yield: 80â€“150 nuts/palm/year Â· Price: â‚¹10,500/qt copra Â· Market: Udupi APMC\n"
                    "   â€¢ ðŸ’¡ Intercrop with banana & turmeric for extra income\n\n"
                    "3. **Coffee (Robusta)** â˜• â€” Best for Kodagu, Chikkamagaluru, Sakleshpur\n"
                    "   â€¢ Yield: 500â€“800 kg/acre Â· Price: â‚¹5,000â€“â‚¹8,000/qt cherry\n"
                    "   â€¢ ðŸ’¡ Coffee Board India gives export support and premium prices\n\n"
                    "4. **Black Pepper** ðŸ«’ â€” High value spice, grows with coffee/coconut\n"
                    "   â€¢ Yield: 2â€“4 kg dry/vine Â· Price: â‚¹40,000â€“â‚¹65,000/qt Â· Market: Kochi\n\n"
                    "5. **Banana (G9)** ðŸŒ â€” Short-duration 11 months, good returns\n"
                    "   â€¢ Yield: 25â€“35 kg/bunch Â· Price: â‚¹900â€“â‚¹1,600/qt Â· Market: Hoskote APMC"
                )
            return (
                "ðŸŒ¾ **Best Crops for Karnataka (Kharif + Rabi):**\n\n"
                "ðŸŒ§ï¸ **Kharif season (Juneâ€“Oct):**\n"
                "â€¢ **Paddy (BPT-5204, Samba Masuri)** â€” MSP â‚¹2,183/qt. SRI method saves 40% water.\n"
                "â€¢ **Ragi (Finger Millet)** â€” Drought resistant. Price â‚¹3,000â€“â‚¹4,000/qt.\n"
                "â€¢ **Maize (Hybrid)** â€” Yield 4â€“6 t/ha. Good demand from poultry feed industry.\n"
                "â€¢ **Turmeric** â€” High value. Price â‚¹7,000â€“â‚¹20,000/qt at Erode/Nizamabad.\n\n"
                "â„ï¸ **Rabi season (Octâ€“Feb):**\n"
                "â€¢ **Onion** â€” Good profit but volatile price. Sell at Bangalore APMC.\n"
                "â€¢ **Sunflower** â€” Low water requirement. MSP available.\n"
                "â€¢ **Groundnut** â€” Good for sandy loam. MSP â‚¹5,850/qt.\n\n"
                "ðŸŒ¿ **Plantation (perennial):**\n"
                "â€¢ Arecanut, Coconut, Coffee, Pepper, Banana â€” select **Plantation** tab for details."
            )

        if "kerala" in msg:
            return (
                "ðŸŒ¿ **Best Crops for Kerala:**\n\n"
                "1. **Coconut** ðŸ¥¥ â€” State crop. 150â€“200 nuts/palm. Copra â‚¹10,500/qt.\n"
                "2. **Rubber** â€” Long-term investment. Latex â‚¹180â€“220/kg.\n"
                "3. **Black Pepper** ðŸ«’ â€” Spice garden staple. â‚¹40,000â€“â‚¹65,000/qt at Kochi.\n"
                "4. **Arecanut** â€” Wayanad, Palakkad. â‚¹36,000â€“â‚¹52,000/qt.\n"
                "5. **Banana (Nendran)** ðŸŒ â€” Premium variety. â‚¹40â€“50/kg retail.\n"
                "6. **Ginger** ðŸ«š â€” Dry ginger â‚¹15,000â€“â‚¹35,000/qt. Good export demand.\n\n"
                "ðŸ’¡ *Kerala farmers benefit from spice export. Contact Spices Board India for export registration.*"
            )

        if any(s in msg for s in ["andhra pradesh","telangana","guntur"]):
            return (
                "ðŸŒ¾ **Best Crops for Andhra Pradesh / Telangana:**\n\n"
                "1. **Chilli (Teja/Byadagi)** ðŸŒ¶ï¸ â€” Highest value. â‚¹8,000â€“â‚¹22,000/qt at Guntur APMC.\n"
                "2. **Paddy** â€” MSP â‚¹2,183/qt. Kharif and Rabi both seasons.\n"
                "3. **Cotton** â€” Black cotton soil. MSP â‚¹6,500/qt.\n"
                "4. **Turmeric** â€” Nizamabad is major market. â‚¹7,000â€“â‚¹20,000/qt.\n"
                "5. **Groundnut** â€” Sandy loam soils. MSP â‚¹5,850/qt.\n"
                "6. **Banana** â€” Krishna, Guntur districts. G9 variety best.\n\n"
                "ðŸ“ž *Contact ANGRAU (Acharya NG Ranga Agricultural University) for variety advice.*"
            )

        if any(s in msg for s in ["maharashtra","nashik","pune"]):
            return (
                "ðŸŒ¾ **Best Crops for Maharashtra:**\n\n"
                "1. **Onion** ðŸ§… â€” Nashik is India's largest market. â‚¹1,000â€“â‚¹2,800/qt.\n"
                "2. **Sugarcane** ðŸŽ‹ â€” FRP â‚¹315/qt guaranteed at sugar mills.\n"
                "3. **Soybean** â€” Kharif. MSP â‚¹4,600/qt. Low input cost.\n"
                "4. **Cotton (Bt)** â€” Vidarbha region. MSP â‚¹6,500/qt.\n"
                "5. **Pomegranate** â€” Solapur, Nashik. Premium market â‚¹40â€“80/kg.\n"
                "6. **Grapes** â€” Nashik region. Export quality fetches premium.\n\n"
                "ðŸ’¡ *Nashik APMC is India's largest onion market. Sell in Februaryâ€“April for best price.*"
            )

        # Generic season-based response
        month = time.localtime().tm_mon
        if "plantation" in msg or "perennial" in msg:
            return (
                "ðŸŒ¿ **Plantation / Perennial Crops (All India):**\n\n"
                "1. **Arecanut** ðŸŒ¿ â€” Karnataka, Kerala, Assam Â· â‚¹36,000â€“â‚¹52,000/qt\n"
                "2. **Coconut** ðŸ¥¥ â€” Coastal India Â· â‚¹10,500/qt copra\n"
                "3. **Coffee** â˜• â€” Coorg, Chikkamagaluru, Wayanad Â· â‚¹5,000â€“â‚¹8,000/qt\n"
                "4. **Black Pepper** ðŸ«’ â€” Kerala, Karnataka Â· â‚¹40,000â€“â‚¹65,000/qt\n"
                "5. **Banana (G9)** ðŸŒ â€” Pan India Â· â‚¹900â€“â‚¹1,600/qt\n"
                "6. **Mango (Alphonso)** ðŸ¥­ â€” Maharashtra, Goa Â· â‚¹60â€“â‚¹120/kg\n\n"
                "ðŸ’¡ *Select your state above for more specific plantation crop advice.*"
            )
        if 6 <= month <= 10:
            season, crops_list = "Kharif (Monsoon â€” Jun to Oct)", [
                ("ðŸŒ¾ Paddy","Best for rice-growing states Â· MSP â‚¹2,183/qt"),
                ("ðŸŒ½ Maize","Hybrid varieties Â· Yield 5â€“8 t/ha Â· Good poultry demand"),
                ("ðŸ‚ Turmeric","High value spice Â· â‚¹7,000â€“â‚¹20,000/qt at Erode"),
                ("ðŸ«š Ginger","Wet areas Â· Dry ginger â‚¹15,000â€“â‚¹35,000/qt"),
                ("ðŸŒ¶ï¸ Chilli","AP/Telangana Â· â‚¹8,000â€“â‚¹22,000/qt at Guntur"),
                ("ðŸ¥œ Groundnut","Sandy loam Â· MSP â‚¹5,850/qt"),
            ]
        elif month >= 11 or month <= 3:
            season, crops_list = "Rabi (Winter â€” Nov to Mar)", [
                ("ðŸŒ¾ Wheat","North India Â· MSP â‚¹2,275/qt Â· Best in Punjab/UP"),
                ("ðŸ§… Onion","Nashik APMC Â· Sell Febâ€“Apr for best price"),
                ("ðŸŒ± Gram (Chickpea)","Low water Â· MSP â‚¹5,440/qt"),
                ("ðŸŒ» Sunflower","Drought tolerant Â· Good oil crop"),
                ("ðŸ«˜ Mustard","Rajasthan/MP Â· MSP â‚¹5,650/qt"),
                ("ðŸŒ¾ Rabi Paddy","South India (Karnataka/TN) Â· Fine varieties"),
            ]
        else:
            season, crops_list = "Summer/Zaid (Apr to Jun)", [
                ("ðŸ‰ Watermelon","Fast crop 60â€“70 days Â· â‚¹5â€“15/kg"),
                ("ðŸ¥’ Cucumber","Low cost Â· Quick return"),
                ("ðŸŒ½ Sweet Corn","50â€“60 days Â· Good demand"),
                ("ðŸ«˜ Moong (Green Gram)","Drought tolerant Â· MSP â‚¹8,558/qt"),
                ("ðŸŒ» Sunflower","Summer variety Â· 90 days"),
            ]
        result = f"ðŸŒ¾ **Recommended Crops â€” {season}:**\n\n"
        for name, tip in crops_list:
            result += f"â€¢ **{name}** â€” {tip}\n"
        result += "\nðŸ“‹ *Select your state and soil type for more specific advice.*"
        return result

    return (
        "ðŸŒ¿ **Namaste! I am your Kisan AI Farming Advisor.**\n\n"
        "Ask me anything about Indian crops:\n\n"
        "ðŸŒ¿ **Arecanut/Supari** â€” Koleroga treatment, fertilizer, price\n"
        "ðŸ¥¥ **Coconut** â€” Pest control, irrigation, copra market\n"
        "ðŸŒ¾ **Paddy/Rice** â€” SRI method, fertilizer schedule, blast disease\n"
        "ðŸŒ **Banana** â€” Panama wilt, bunch care, G9 variety\n"
        "ðŸ‚ **Turmeric/Ginger** â€” Rhizome rot, drying, market price\n"
        "ðŸŒ¶ï¸ **Chilli** â€” Thrips, Byadagi variety, Guntur market\n"
        "â˜• **Coffee/Pepper** â€” Leaf rust, Koleroga, Kodagu farming\n"
        "ðŸ“‹ **Schemes** â€” PM-KISAN, PMFBY, Drip subsidy, Kisan Credit Card\n"
        "ðŸ“Š **Market** â€” APMC prices, best time to sell\n"
        "Type your question in simple words â€” I will help! ðŸ˜Š"
    )


# â”€â”€ Smart Answer Engine â€” works without IBM key â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def smart_answer(message: str) -> str:
    """
    Comprehensive keyword-based answer engine.
    Covers every common farmer question with specific, actionable answers.
    """
    intent = detect_intent(message)
    m = message.lower()

    # â”€â”€ SCHEMES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if intent == "schemes":
        return demo_answer(message)   # demo_answer has good scheme answers

    # â”€â”€ MARKET â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if intent == "market":
        return demo_answer(message)   # demo_answer has good market answers

    # â”€â”€ PEST & DISEASE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if intent == "pest":
        # â”€â”€ Arecanut â”€â”€
        if any(w in m for w in ["koleroga","areca","supari","bunch rot","mahali"]):
            return (
                "ðŸŒ¿ **Arecanut Koleroga (Phytophthora Fruit Rot):**\n\n"
                "**Symptoms:** Bunches turn black, premature fruit drop, brown rot on stalk â€” mostly during monsoon.\n\n"
                "âœ… **Treatment:**\n"
                "â€¢ Spray **Bordeaux mixture 1%** on bunches + stalk â€” June & July\n"
                "â€¢ Severe cases: Drench base with **Metalaxyl + Mancozeb 3g/L** water\n"
                "â€¢ Remove & burn all infected bunches immediately\n\n"
                "ðŸ›¡ï¸ **Prevention:** Spray Bordeaux before monsoon starts (May end)\n"
                "â° **Best spray time:** 6â€“9 AM Â· Wear gloves + mask\n"
                "ðŸ“ž Help: Arecanut Research Station, Vitla, Karnataka"
            )
        # â”€â”€ Coconut weevil â”€â”€
        if any(w in m for w in ["coconut weevil","red palm","weevil","bore hole"]):
            return (
                "ðŸ¥¥ **Coconut Red Palm Weevil:**\n\n"
                "**Symptoms:** Bore holes in trunk with brown frass, yellow drooping crown, wilting top leaves.\n\n"
                "âœ… **Treatment:**\n"
                "â€¢ Inject **Chlorpyrifos 2ml/L** water into bore holes using syringe â€” seal with mud after\n"
                "â€¢ Install **4 pheromone traps per hectare** to catch adult weevils\n"
                "â€¢ Fill holes with **Carbaryl 10% dust + sand mixture**\n\n"
                "âš ï¸ **Severe attack:** Fell & burn infested palms to stop spread\n"
                "ðŸ›¡ï¸ **Prevention:** Keep crown clean, apply Chlorpyrifos 0.1% to crown monthly"
            )
        # â”€â”€ Paddy blast â”€â”€
        if any(w in m for w in ["blast","paddy blast","grey lesion","neck rot","rice blast"]):
            return (
                "ðŸŒ¾ **Paddy Blast Disease:**\n\n"
                "**Symptoms:** Spindle-shaped grey/brown lesions on leaves; grey neck at panicle (neck rot).\n\n"
                "âœ… **Treatment:**\n"
                "â€¢ Spray **Tricyclazole 75 WP â€” 0.6g per litre** water\n"
                "â€¢ Apply at **25 days** and **45 days** after transplanting\n"
                "â€¢ Alternative: **Carbendazim 1g/L** water\n\n"
                "ðŸ›¡ï¸ **Prevention:**\n"
                "â€¢ Use blast-resistant varieties (Samba Masuri BPT-5204, IR-64)\n"
                "â€¢ Avoid excess Nitrogen fertilizer\n"
                "â€¢ Do NOT keep waterlogged â€” use AWD (alternate wet & dry)"
            )
        # â”€â”€ Banana wilt / Panama â”€â”€
        if any(w in m for w in ["banana wilt","panama","fusarium","pseudostem split"]):
            return (
                "ðŸŒ **Banana Panama Wilt (Fusarium Wilt):**\n\n"
                "**Symptoms:** Yellowing starts from bottom leaves, pseudostem turns brown inside, splits.\n\n"
                "âš ï¸ **No chemical cure exists for Panama wilt.**\n\n"
                "âœ… **Management:**\n"
                "â€¢ Remove and destroy infected plants immediately â€” do NOT compost\n"
                "â€¢ Apply **Trichoderma viride 50g per plant** in soil at planting\n"
                "â€¢ Use **wilt-resistant varieties** â€” Grand Naine (G9), Nendran, Robusta\n"
                "â€¢ Do NOT plant banana in same field for 2â€“3 seasons\n\n"
                "ðŸ’¡ G9 (Grand Naine) is Panama-resistant and gives best yield."
            )
        # â”€â”€ Chilli thrips / mites â”€â”€
        if any(w in m for w in ["thrips","chilli pest","mite","curl","silver"]):
            return (
                "ðŸŒ¶ï¸ **Chilli Thrips & Mite Management:**\n\n"
                "**Symptoms:** Curled/cupped leaves, silvery streaks on leaves, tiny insects visible.\n\n"
                "âœ… **Treatment:**\n"
                "â€¢ **Spinosad 45 SC â€” 0.3ml per litre** water (organic option)\n"
                "â€¢ **Abamectin 1.9 EC â€” 0.5ml per litre** water (for mites)\n"
                "â€¢ **Imidacloprid 17.8 SL â€” 0.3ml per litre** (for heavy infestation)\n\n"
                "ðŸ” Alternate chemicals each spray to prevent resistance\n"
                "â° Spray at **6â€“9 AM** Â· Spray **bottom side of leaves** too\n"
                "ðŸ›¡ï¸ **Prevention:** Use yellow sticky traps (5 per acre)"
            )
        # â”€â”€ Turmeric rhizome rot â”€â”€
        if any(w in m for w in ["turmeric rot","rhizome rot","collar rot","ginger rot"]):
            return (
                "ðŸ‚ **Turmeric / Ginger Rhizome Rot:**\n\n"
                "**Symptoms:** Yellow wilting from base, rotting at collar, foul smell from soil.\n\n"
                "âœ… **Treatment:**\n"
                "â€¢ Drench soil with **Metalaxyl + Mancozeb 3g/L** water around affected plants\n"
                "â€¢ Remove infected plants with surrounding soil\n\n"
                "ðŸ›¡ï¸ **Prevention (most important):**\n"
                "â€¢ Treat seed rhizomes with **Metalaxyl 2g/L** before planting (30 min soak)\n"
                "â€¢ Grow on **raised beds (15â€“20cm)** â€” rhizome rot starts in waterlogged soil\n"
                "â€¢ Apply **Trichoderma 50g per pit** at planting\n"
                "â€¢ Ensure proper field drainage â€” never let water stagnate"
            )
        # â”€â”€ Maize armyworm â”€â”€
        if any(w in m for w in ["armyworm","fall armyworm","maize pest","whorl","caterpillar"]):
            return (
                "ðŸŒ½ **Maize Fall Armyworm (Spodoptera frugiperda):**\n\n"
                "**Symptoms:** Ragged/torn whorl leaves, caterpillars inside whorl, frass (powdery droppings) visible.\n\n"
                "âœ… **Treatment:**\n"
                "â€¢ Apply **Emamectin benzoate 5 SG â€” 0.4g per litre** INTO the whorl\n"
                "â€¢ Apply at **15â€“18 days** after germination when caterpillars are small\n"
                "â€¢ Mix sand + insecticide and drop into whorl for better contact\n\n"
                "ðŸŒ¿ **Organic option:** Spray **Bt (Bacillus thuringiensis) 2g/L** â€” safe, effective\n"
                "â° Spray early morning Â· Repeat after 7 days if needed"
            )
        # â”€â”€ Aphids â”€â”€
        if any(w in m for w in ["aphid","sticky","honeydew","yellow curl"]):
            return (
                "ðŸ› **Aphid Management (All Crops):**\n\n"
                "**Symptoms:** Clusters of tiny insects on new shoots/leaves, sticky honeydew, curled yellow leaves.\n\n"
                "âœ… **Treatment:**\n"
                "â€¢ ðŸŒ¿ **Organic:** Neem oil **3ml per litre** water + soap â€” spray on leaves & stem\n"
                "â€¢ ðŸ’Š **Chemical:** **Imidacloprid 0.3ml per litre** water\n"
                "â€¢ Strong water jet spray to wash them off\n\n"
                "ðŸ” **Repeat after 7 days** if still present\n"
                "âš ï¸ Wear gloves Â· spray early morning 6â€“9 AM"
            )
        # â”€â”€ Coffee leaf rust â”€â”€
        if any(w in m for w in ["coffee rust","leaf rust","orange pustule","coffee disease"]):
            return (
                "â˜• **Coffee Leaf Rust (Hemileia vastatrix):**\n\n"
                "**Symptoms:** Yellowish-orange powdery pustules on underside of leaves, premature leaf drop.\n\n"
                "âœ… **Treatment:**\n"
                "â€¢ Spray **Copper oxychloride 3g per litre** water â€” cover leaf undersides\n"
                "â€¢ Systemic: **Propiconazole 1ml per litre** for severe attack\n"
                "â€¢ Spray at **onset of monsoon** (June) and after (September)\n\n"
                "ðŸ›¡ï¸ **Prevention:**\n"
                "â€¢ Maintain shade â€” excess sunlight increases rust severity\n"
                "â€¢ Avoid over-fertilizing with Nitrogen\n"
                "ðŸ“ž Coffee Board India helpline: 080-25362161"
            )
        # â”€â”€ Pepper phytophthora â”€â”€
        if any(w in m for w in ["pepper disease","pepper wilt","pepper rot","phytophthora pepper"]):
            return (
                "ðŸ«’ **Black Pepper Phytophthora (Quick Wilt):**\n\n"
                "**Symptoms:** Sudden yellowing, wilting, root rot, black lesions on vines.\n\n"
                "âœ… **Treatment:**\n"
                "â€¢ Drench soil with **Metalaxyl 2g per litre** water (1â€“2L per vine)\n"
                "â€¢ Spray foliage with **Copper oxychloride 3g/L** water\n\n"
                "ðŸ›¡ï¸ **Prevention:**\n"
                "â€¢ Improve field drainage â€” grow on mounds or slopes\n"
                "â€¢ Apply **Trichoderma 100g per vine** in soil at planting\n"
                "â€¢ Avoid waterlogging near standards/supports"
            )
        # â”€â”€ Generic pest answer â”€â”€
        return demo_answer(message)

    # â”€â”€ FERTILIZER â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if intent == "fertilizer":
        FERT = {
            "arecanut":  "**Arecanut (bearing palm/year):**\nâ€¢ Urea 200g + SSP 130g + MOP 130g + FYM 12kg per palm\nâ€¢ Apply in **2 splits: June and September**\nâ€¢ Borax 25g per palm (micronutrient)\nâ€¢ Apply in a ring 1m from base, cover with soil",
            "coconut":   "**Coconut (per palm/year):**\nâ€¢ Urea 1.3kg + SSP 2kg + MOP 2kg + FYM 50kg\nâ€¢ Apply in **2 splits: June and December**\nâ€¢ Apply in circular trench (1.5m radius from trunk)\nâ€¢ Borax 50g + Ferrous sulfate 25g if showing deficiency",
            "banana":    "**Banana (per plant/crop):**\nâ€¢ Urea 250g + DAP 100g + MOP 300g + FYM 10kg\nâ€¢ Give in **4 splits** over 9 months\nâ€¢ Best method: Drip fertigation saves 30% fertilizer\nâ€¢ Critical: Never skip fertilizer at bunch shooting stage",
            "paddy":     "**Paddy/Rice (per hectare):**\nâ€¢ NPK **120:60:60 kg/ha**\nâ€¢ Full P (DAP) + K (MOP) at transplanting as basal\nâ€¢ Nitrogen (Urea) in 3 splits: 25% basal + 50% at 21 days + 25% at panicle initiation\nâ€¢ Do NOT apply Urea during heavy rain",
            "rice":      "**Rice/Paddy (per hectare):**\nâ€¢ NPK **120:60:60 kg/ha**\nâ€¢ Full P+K at transplanting. Urea in 3 splits.\nâ€¢ 25% at transplanting + 50% at 21 days + 25% at panicle initiation",
            "sugarcane": "**Sugarcane (per hectare):**\nâ€¢ NPK **250:115:115 kg/ha** in 3 splits\nâ€¢ FYM 25 t/ha as basal before planting\nâ€¢ Drip fertigation saves 40% water + gives 25% higher yield",
            "turmeric":  "**Turmeric (per hectare):**\nâ€¢ NPK **150:50:100 kg/ha** + FYM 30 t/ha\nâ€¢ Full P+K at planting. N in 2 splits: at planting + at 60 days\nâ€¢ Borax 10kg/ha + ZnSO4 25kg/ha as micronutrients\nâ€¢ Apply thick mulch after planting",
            "ginger":    "**Ginger (per hectare):**\nâ€¢ NPK **75:50:75 kg/ha** + FYM 30 t/ha\nâ€¢ ZnSO4 25kg/ha\nâ€¢ Apply in 3 splits. Mulch with dry leaves after planting.",
            "chilli":    "**Chilli (per hectare):**\nâ€¢ NPK **100:50:50 kg/ha** + FYM 20 t/ha\nâ€¢ Boron spray **0.2%** at flowering improves fruit set by 20â€“30%\nâ€¢ Drip fertigation gives best results",
            "maize":     "**Maize (per hectare):**\nâ€¢ NPK **150:75:37.5 kg/ha**\nâ€¢ Urea in 3 splits: at sowing + 30 days + 60 days\nâ€¢ Apply Zinc sulfate 25kg/ha if zinc deficiency (white stripe on leaves)",
            "wheat":     "**Wheat (per hectare):**\nâ€¢ NPK **120:60:40 kg/ha**\nâ€¢ Half Urea at sowing + remaining at first irrigation (21 days)\nâ€¢ Full P (DAP) + K (MOP) at sowing as basal",
            "onion":     "**Onion (per hectare):**\nâ€¢ NPK **100:50:75 kg/ha** + Sulphur 25kg/ha\nâ€¢ Apply N in 3 splits. **Stop all N after bulb formation** â€” excess N causes splitting\nâ€¢ Sulphur improves pungency and shelf life",
            "tomato":    "**Tomato (per hectare):**\nâ€¢ NPK **200:120:120 kg/ha** + FYM 25 t/ha\nâ€¢ Boron 0.2% spray at flowering improves fruit set\nâ€¢ Apply Calcium (CaNO3) to prevent blossom end rot",
            "coffee":    "**Coffee (per plant/year):**\nâ€¢ Urea 250g + SSP 150g + MOP 200g + FYM 5kg\nâ€¢ Apply in **2 splits: June and September**\nâ€¢ Apply after blossom shower irrigation in March",
            "pepper":    "**Black Pepper (per vine/year):**\nâ€¢ NPK 50:50:150g + FYM 5kg + Neem cake 1kg\nâ€¢ Apply before monsoon (May) and after (October)\nâ€¢ Neem cake prevents root rot and adds nutrients",
            "cotton":    "**Cotton (per hectare):**\nâ€¢ NPK **150:75:75 kg/ha**\nâ€¢ Stop excess Nitrogen after boll formation â€” causes late vegetative growth\nâ€¢ Apply Boron 0.2% at squaring stage",
            "soybean":   "**Soybean (per hectare):**\nâ€¢ NPK **20:60:40 kg/ha** (low N â€” soybean fixes its own N)\nâ€¢ Rhizobium seed treatment before sowing\nâ€¢ Apply Sulphur 20kg/ha for higher protein content",
            "groundnut": "**Groundnut (per hectare):**\nâ€¢ NPK **25:50:75 kg/ha** + Gypsum 500kg/ha at pegging\nâ€¢ Gypsum is critical for shell filling and preventing empty pods\nâ€¢ Apply Boron 1kg/ha as micronutrient",
        }
        for crop, advice in FERT.items():
            if crop in m:
                return (
                    f"ðŸ§ª **Fertilizer Schedule â€” {crop.capitalize()}:**\n\n"
                    f"{advice}\n\n"
                    "ðŸ’¡ **Key fertilizers:**\n"
                    "â€¢ Urea = Nitrogen (N) â€” growth & green colour\n"
                    "â€¢ DAP/SSP = Phosphorus (P) â€” roots & flowers\n"
                    "â€¢ MOP = Potassium (K) â€” fruit size & disease resistance\n"
                    "ðŸŒ± *Get free soil test (Soil Health Card) from KVK for exact doses.*"
                )
        # General fertilizer question
        return (
            "ðŸ§ª **Fertilizer Guide for Indian Farmers:**\n\n"
            "ðŸ“¦ **What each fertilizer does:**\n"
            "â€¢ **Urea (46% N)** â†’ Makes plants grow GREEN and tall. Top-dress application.\n"
            "â€¢ **DAP (18-46-0)** â†’ Phosphorus for ROOT growth and early establishment.\n"
            "â€¢ **MOP (0-0-60)** â†’ Potassium for BIG FRUITS, disease resistance.\n"
            "â€¢ **SSP (0-16-0+S)** â†’ Cheaper source of Phosphorus + Sulphur.\n"
            "â€¢ **NPK 17:17:17** â†’ Balanced, all growth stages.\n"
            "â€¢ **FYM/Compost** â†’ Improves soil health, water holding.\n\n"
            "âš ï¸ **Golden rules:**\n"
            "â€¢ Do soil test first â€” avoid over-fertilizing\n"
            "â€¢ Split doses (2â€“3 times) â€” better uptake, less wastage\n"
            "â€¢ Never apply before heavy rain â€” gets washed away\n\n"
            "ðŸ“ž **Ask crop-specific dose:** Tell me your crop name!\n"
            "ðŸŒ± *Free Soil Health Card from KVK gives exact fertilizer recommendations.*"
        )

    # â”€â”€ IRRIGATION â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if intent == "irrigation":
        return demo_answer(message)   # demo_answer has excellent irrigation answers

    # â”€â”€ SOIL ANALYSIS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if intent == "soil":
        return demo_answer(message)   # demo_answer has good soil answers

    # â”€â”€ CROP RECOMMENDATION â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if intent == "crop":
        # check specific crop questions first
        CROP_INFO = {
            "arecanut": (
                "ðŸŒ¿ **Arecanut (Supari) Farming:**\n\n"
                "ðŸ“ **Best regions:** Coastal Karnataka (Shivamogga, Udupi, DK), Kerala, Assam\n"
                "ðŸŒ± **Soil:** Well-drained laterite/red loam Â· pH 5.5â€“7.0\n"
                "ðŸ“… **Planting:** Juneâ€“September Â· Spacing: 2.7m Ã— 2.7m\n"
                "ðŸ’° **Price:** â‚¹36,000â€“â‚¹52,000/quintal Â· Best market: Shivamogga APMC\n"
                "â±ï¸ **Starts bearing:** 5â€“7 years after planting\n"
                "ðŸŒ§ï¸ **Key risk:** Koleroga disease in monsoon â€” spray Bordeaux mixture 1% before June\n"
                "ðŸ’§ **Irrigation:** 15â€“20L/palm/day in summer (Marchâ€“May)\n"
                "ðŸ›ï¸ **Sell through:** CAMPCO cooperative or Shivamogga APMC"
            ),
            "coconut": (
                "ðŸ¥¥ **Coconut Farming:**\n\n"
                "ðŸ“ **Best regions:** Coastal Karnataka, Kerala, Tamil Nadu, Andhra Pradesh\n"
                "ðŸŒ± **Soil:** Sandy loam, laterite Â· pH 5.5â€“7.5\n"
                "ðŸ“… **Spacing:** 7.5m Ã— 7.5m (triangular) Â· Starts bearing at 5â€“7 years\n"
                "ðŸ’° **Copra price:** â‚¹8,500â€“â‚¹12,000/quintal Â· Best: Udupi, Thrissur, Pollachi\n"
                "ðŸ’§ **Irrigation:** 200L/palm/week in summer\n"
                "ðŸŒ¿ **Intercrop:** Banana, Turmeric, Ginger between young palms for extra income\n"
                "ðŸ›ï¸ **Support:** CPCRI (Central Plantation Crops Research Institute)"
            ),
            "banana": (
                "ðŸŒ **Banana Farming (G9 / Grand Naine):**\n\n"
                "ðŸ“ **Suitable:** All India Â· Especially Andhra Pradesh, Karnataka, Gujarat, Bihar\n"
                "ðŸŒ± **Variety:** G9 (Grand Naine) â€” 11 months, 25â€“35kg/bunch Â· Panama wilt resistant\n"
                "ðŸ’° **Price:** â‚¹900â€“â‚¹1,600/quintal Â· Markets: Hoskote APMC (Bangalore), local\n"
                "ðŸ’§ **Water:** Critical at bunch shooting â€” 15L/plant/day via drip\n"
                "ðŸ§ª **Fertilizer:** 250g Urea + 100g DAP + 300g MOP per plant over 9 months\n"
                "âš ï¸ **Risk:** Panama wilt â€” use resistant varieties, apply Trichoderma at planting"
            ),
            "paddy": (
                "ðŸŒ¾ **Paddy/Rice Farming:**\n\n"
                "ðŸ“… **Kharif paddy:** Juneâ€“November Â· Rabi paddy (South India): Novâ€“April\n"
                "ðŸŒ± **Top varieties:** Samba Masuri (BPT-5204), Swarna, IR-64, MTU-7029\n"
                "ðŸ’° **MSP:** â‚¹2,183/quintal (2023-24) Â· Government procurement by FCI\n"
                "ðŸ§ª **Fertilizer:** NPK 120:60:60 kg/ha Â· Urea in 3 splits\n"
                "ðŸ’§ **Water:** Maintain 3â€“5cm standing water during tillering\n"
                "ðŸŒ¿ **SRI method:** 30% higher yield Â· Less water Â· Use young seedlings (14 days)\n"
                "âš ï¸ **Key disease:** Blast â€” spray Tricyclazole 0.6g/L at 25 + 45 days"
            ),
            "coffee": (
                "â˜• **Coffee Farming:**\n\n"
                "ðŸ“ **Best regions:** Kodagu (Coorg), Chikkamagaluru, Sakleshpur (Karnataka); Wayanad (Kerala)\n"
                "ðŸŒ± **Varieties:** Arabica (high quality, hills), Robusta (lowlands, higher yield)\n"
                "ðŸ’° **Price:** â‚¹5,000â€“â‚¹8,000/quintal cherry Â· Organic certified fetches 2Ã— premium\n"
                "ðŸ’§ **Key irrigation:** Blossom shower 250L/plant in Febâ€“March triggers flowering\n"
                "âš ï¸ **Key disease:** Leaf rust â€” spray Copper oxychloride 3g/L at onset of monsoon\n"
                "ðŸ›ï¸ **Support:** Coffee Board India, Coorg & Chikkamagaluru markets"
            ),
            "turmeric": (
                "ðŸ‚ **Turmeric Farming:**\n\n"
                "ðŸ“ **Best regions:** Erode (TN), Nizamabad (TS), Coastal Karnataka, Odisha\n"
                "ðŸ“… **Planting:** Aprilâ€“June Â· Harvest: 8â€“9 months later\n"
                "ðŸ’° **Price:** â‚¹7,000â€“â‚¹20,000/quintal Â· Best market: Erode APMC (Tamil Nadu)\n"
                "ðŸ’¡ **Tip:** Sell 3â€“6 months AFTER harvest for 30â€“40% better price\n"
                "ðŸ§ª **Fertilizer:** NPK 150:50:100 kg/ha + FYM 30t/ha\n"
                "âš ï¸ **Key risk:** Rhizome rot â€” grow on raised beds, treat seed with Metalaxyl\n"
                "ðŸŒ± **Intercrop:** Excellent intercrop under coconut/arecanut"
            ),
            "pepper": (
                "ðŸ«’ **Black Pepper Farming:**\n\n"
                "ðŸ“ **Best regions:** Kerala (Idukki, Wayanad), Coorg (Karnataka)\n"
                "ðŸ’° **Price:** â‚¹40,000â€“â‚¹65,000/quintal Â· Best: Kochi, Kozhikode markets\n"
                "ðŸŒ± **Support:** Needs live standard (Erythrina/Silver oak) or dead standards\n"
                "ðŸ§ª **Fertilizer:** NPK 50:50:150g + FYM 5kg + Neem cake 1kg per vine/year\n"
                "âš ï¸ **Key risk:** Phytophthora quick wilt â€” improve drainage, drench with Metalaxyl\n"
                "ðŸ›ï¸ **Export help:** Spices Board India connects to exporters for premium price"
            ),
        }
        for crop, info in CROP_INFO.items():
            if crop in m:
                return info
        # Return season/region based crop advice
        return demo_answer(message)

    # â”€â”€ GENERAL / UNKNOWN â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
        "ðŸŒ¿ **Namaste! I am your Kisan AI Farming Advisor.**\n\n"
        "I can answer questions about:\n\n"
        "ðŸŒ¿ **Crops** â€” Arecanut, Coconut, Paddy, Banana, Coffee, Turmeric, Ginger, Chilli, Pepper, Maize, Wheat, Onion\n"
        "ðŸ› **Pest & Disease** â€” Koleroga, Blast, Wilt, Armyworm, Aphids, Weevil\n"
        "ðŸ§ª **Fertilizer** â€” NPK doses, Urea, DAP, MOP schedules per crop\n"
        "ðŸ’§ **Irrigation** â€” Drip, sprinkler, stage-wise water schedules\n"
        "ðŸ“Š **Market Prices** â€” APMC mandi rates, best time to sell\n"
        "ðŸ“‹ **Govt Schemes** â€” PM-KISAN, PMFBY, Drip subsidy, Kisan Credit Card\n"
        "ðŸª± **Soil Health** â€” pH, NPK, soil type advice\n\n"
        "**Just ask your question in simple words!**\n"
        "Example: *'What is the fertilizer dose for arecanut?'*\n"
        "ðŸ“ž Kisan Call Centre: **1800-180-1551** (Free, 24Ã—7)"
    )


# â”€â”€ IBM WatsonX â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
    """Pull out the language instruction appended by the frontend, return (clean_msg, lang_code).
    Supported languages: English (en), Hindi (hi), Kannada (kn).
    """
    import re
    lang_map = {
        "hindi": "hi", "à¤¹à¤¿à¤‚à¤¦à¥€": "hi",
        "kannada": "kn", "à²•à²¨à³à²¨à²¡": "kn",
    }
    lang = "en"
    clean = message
    match = re.search(r'\[Please reply in (\w+)', message, re.IGNORECASE)
    if match:
        word = match.group(1).lower()
        for key, code in lang_map.items():
            if key in word or word in key:
                lang = code
                break
        clean = re.sub(r'\[Please reply in[^\]]+\]', '', message).strip()
    return clean, lang


# â”€â”€ Built-in translations â€” EN / Hindi / Kannada only â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_TRANSLATIONS = {
    "note": {
        "hi": "\n\nðŸ“ž **à¤•à¤¿à¤¸à¤¾à¤¨ à¤•à¥‰à¤² à¤¸à¥‡à¤‚à¤Ÿà¤°: 1800-180-1551** (à¤¨à¤¿à¤ƒà¤¶à¥à¤²à¥à¤•)",
        "kn": "\n\nðŸ“ž **à²•à²¿à²¸à²¾à²¨à³ à²•à²¾à²²à³ à²¸à³†à²‚à²Ÿà²°à³: 1800-180-1551** (à²‰à²šà²¿à²¤)",
    },
    "intent_hdr": {
        "crop":       {"hi": "à¤«à¤¸à¤² à¤¸à¤²à¤¾à¤¹:", "kn": "à²¬à³†à²³à³† à²¸à²²à²¹à³†:"},
        "pest":       {"hi": "à¤•à¥€à¤Ÿ/à¤°à¥‹à¤—:",  "kn": "à²•à³€à²Ÿ/à²°à³‹à²—:"},
        "fertilizer": {"hi": "à¤‰à¤°à¥à¤µà¤°à¤•:",   "kn": "à²—à³Šà²¬à³à²¬à²°:"},
        "market":     {"hi": "à¤®à¤‚à¤¡à¥€ à¤­à¤¾à¤µ:", "kn": "à²®à²¾à²°à³à²•à²Ÿà³à²Ÿà³† à²¬à³†à²²à³†:"},
        "irrigation": {"hi": "à¤¸à¤¿à¤‚à¤šà¤¾à¤ˆ:",   "kn": "à²¨à³€à²°à²¾à²µà²°à²¿:"},
        "schemes":    {"hi": "à¤¯à¥‹à¤œà¤¨à¤¾à¤à¤‚:",  "kn": "à²¯à³‹à²œà²¨à³†à²—à²³à³:"},
        "soil":       {"hi": "à¤®à¤¿à¤Ÿà¥à¤Ÿà¥€:",   "kn": "à²®à²£à³à²£à³:"},
        "general":    {"hi": "à¤¸à¤²à¤¾à¤¹:",     "kn": "à²¸à²²à²¹à³†:"},
    },
}


# â”€â”€ Full translations for top common questions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Kannada and Hindi are prioritized; others use greeting + English body + footer
_FULL_ANSWERS_KN = {
    "koleroga": """à²¨à²®à²¸à³à²•à²¾à²° à²°à³ˆà²¤ à²…à²£à³à²£! à²…à²¡à²•à³†à²¯ à²•à³Šà²³à³†à²°à³‹à²—à²¦ (Phytophthora Fruit Rot) à²¬à²—à³à²—à³†:

**à²²à²•à³à²·à²£à²—à²³à³:** à²—à³Šà²‚à²šà²²à³à²—à²³à³ à²•à²ªà³à²ªà²¾à²—à³à²¤à³à²¤à²µà³†, à²®à²¾à²¨à³à²¸à³‚à²¨à³ à²¸à²®à²¯à²¦à²²à³à²²à²¿ à²•à²¾à²¯à²¿à²—à²³à³ à²‰à²¦à³à²°à³à²¤à³à²¤à²µà³†

**à²šà²¿à²•à²¿à²¤à³à²¸à³†:**
â€¢ à²œà³‚à²¨à³-à²œà³à²²à³ˆà²¨à²²à³à²²à²¿ à²—à³Šà²‚à²šà²²à³ + à²•à²¾à²‚à²¡à²¦ à²®à³‡à²²à³† **à²¬à³‹à²°à³à²¡à³‹ à²®à²¿à²¶à³à²°à²£ 1%** à²¸à²¿à²‚à²ªà²¡à²¿à²¸à²¿
â€¢ à²—à²‚à²­à³€à²° à²¸à²®à²¸à³à²¯à³†: **Metalaxyl + Mancozeb 3g/L** à²¨à³€à²°à²¿à²¨à²²à³à²²à²¿ à²¬à³‡à²°à²¿à²—à³† à²¸à³à²°à²¿à²¯à²¿à²°à²¿
â€¢ à²°à³‹à²—à²—à³à²°à²¸à³à²¤ à²—à³Šà²‚à²šà²²à³à²—à²³à²¨à³à²¨à³ à²¤à³†à²—à³†à²¦à³ à²¸à³à²¡à²¿à²°à²¿

**à²¤à²¡à³†à²—à²Ÿà³à²Ÿà³à²µà²¿à²•à³†:** à²®à²¾à²¨à³à²¸à³‚à²¨à³ à²ªà³à²°à²¾à²°à²‚à²­à²µà²¾à²—à³à²µ à²®à³Šà²¦à²²à³ (à²®à³‡ à²•à³Šà²¨à³†à²¯à²²à³à²²à²¿) à²¬à³‹à²°à³à²¡à³‹ à²®à²¿à²¶à³à²°à²£ à²¸à²¿à²‚à²ªà²¡à²¿à²¸à²¿
à²¸à²¿à²‚à²ªà²¡à²£à³† à²¸à²®à²¯: 6â€“9 AM | à²•à³ˆà²—à²µà²¸à³ + à²®à²¾à²¸à³à²•à³ à²§à²°à²¿à²¸à²¿

à²¸à²¹à²¾à²¯: à²…à²¡à²•à³† à²¸à²‚à²¶à³‹à²§à²¨à²¾ à²•à³‡à²‚à²¦à³à²°, à²µà²¿à²Ÿà³à²², à²•à²°à³à²¨à²¾à²Ÿà²•
ðŸ“ž à²•à²¿à²¸à²¾à²¨à³ à²•à²¾à²²à³ à²¸à³†à²‚à²Ÿà²°à³: 1800-180-1551 (à²‰à²šà²¿à²¤)""",

    "arecanut_fertilizer": """à²¨à²®à²¸à³à²•à²¾à²° à²°à³ˆà²¤ à²…à²£à³à²£! à²…à²¡à²•à³†à²¯ à²—à³Šà²¬à³à²¬à²°à²¦ à²¬à²—à³à²—à³†:

**à²…à²¡à²•à³† (à²«à²²à²¿à²¸à³à²µ à²®à²°/à²µà²°à³à²·à²•à³à²•à³†):**
â€¢ à²¯à³‚à²°à²¿à²¯à²¾ 200g + SSP 130g + MOP 130g + à²Žà²«à³â€Œà²µà³ˆà²Žà²‚ 12kg à²ªà³à²°à²¤à²¿ à²®à²°à²•à³à²•à³†
â€¢ **à²Žà²°à²¡à³ à²¸à²² à²¹à²¾à²•à²¿: à²œà³‚à²¨à³ à²®à²¤à³à²¤à³ à²¸à³†à²ªà³à²Ÿà³†à²‚à²¬à²°à³**
â€¢ à²¬à³‹à²°à²¾à²•à³à²¸à³ 25g à²ªà³à²°à²¤à²¿ à²®à²°à²•à³à²•à³† (à²¸à³‚à²•à³à²·à³à²® à²ªà³‹à²·à²•à²¾à²‚à²¶)
â€¢ à²®à²°à²¦à²¿à²‚à²¦ 1 à²®à³€à²Ÿà²°à³ à²¦à³‚à²°à²¦à²²à³à²²à²¿ à²µà³ƒà²¤à³à²¤à²¾à²•à²¾à²°à²µà²¾à²—à²¿ à²¹à²¾à²•à²¿ à²®à²£à³à²£à³ à²¹à²¾à²•à²¿

**à²ªà³à²°à²®à³à²– à²—à³Šà²¬à³à²¬à²°à²—à²³à³:**
â€¢ à²¯à³‚à²°à²¿à²¯à²¾ = à²¸à²¾à²°à²œà²¨à²• (N) â€” à²¬à³†à²³à²µà²£à²¿à²—à³† + à²¹à²¸à²¿à²°à³ à²¬à²£à³à²£
â€¢ SSP/DAP = à²°à²‚à²œà²• (P) â€” à²¬à³‡à²°à³ + à²¹à³‚à²µà³à²—à²³à³
â€¢ MOP = à²ªà³Šà²Ÿà³à²¯à²¾à²¶à³ (K) â€” à²•à²¾à²¯à²¿ à²—à²¾à²¤à³à²° + à²°à³‹à²— à²¨à²¿à²°à³‹à²§à²•à²¤à³†

à²‰à²šà²¿à²¤ à²®à²£à³à²£à³ à²ªà²°à³€à²•à³à²·à³† (Soil Health Card) KVK à²¯à²¿à²‚à²¦ à²ªà²¡à³†à²¯à²¿à²°à²¿
ðŸ“ž à²•à²¿à²¸à²¾à²¨à³ à²•à²¾à²²à³ à²¸à³†à²‚à²Ÿà²°à³: 1800-180-1551 (à²‰à²šà²¿à²¤)""",

    "market_price_arecanut": """à²¨à²®à²¸à³à²•à²¾à²° à²°à³ˆà²¤ à²…à²£à³à²£! à²…à²¡à²•à³† à²¬à³†à²²à³† à²®à²¾à²¹à²¿à²¤à²¿:

**à²…à²¡à²•à³† (à²šà²¾à²³à²¿) â€” à²ªà³à²°à²¸à³à²¤à³à²¤ à²®à²¾à²°à³à²•à²Ÿà³à²Ÿà³† à²¬à³†à²²à³†:**
â€¢ **â‚¹36,000 à²°à²¿à²‚à²¦ â‚¹52,000/à²•à³à²µà²¿à²‚à²Ÿà²¾à²²à³**
â€¢ à²‰à²¤à³à²¤à²® à²®à²¾à²°à³à²•à²Ÿà³à²Ÿà³†: à²¶à²¿à²µà²®à³Šà²—à³à²— APMC (à²­à²¾à²°à²¤à²¦ à²…à²¤à²¿à²¦à³Šà²¡à³à²¡ à²…à²¡à²•à³† à²®à²¾à²°à³à²•à²Ÿà³à²Ÿà³†)
â€¢ CAMPCO à²¸à²¹à²•à²¾à²° à²¸à²‚à²¸à³à²¥à³†à²¯à³ à²¨à³à²¯à²¾à²¯à²¯à³à²¤ à²¬à³†à²²à³† à²¨à³€à²¡à³à²¤à³à²¤à²¦à³†

**à²‰à²¤à³à²¤à²® à²®à²¾à²°à²¾à²Ÿ à²¸à²®à²¯:** à²®à²¾à²°à³à²šà³â€“à²œà³‚à²¨à³ (à²¬à³†à²²à³† à²…à²¤à³à²¯à³à²¨à³à²¨à²¤ à²®à²Ÿà³à²Ÿà²¦à²²à³à²²à²¿à²°à³à²¤à³à²¤à²¦à³†)

**à²¬à³†à²²à³† à²ªà²°à³€à²•à³à²·à²¿à²¸à²¿:**
â€¢ agmarknet.nic.in â€” à²²à³ˆà²µà³ APMC à²¬à³†à²²à³†à²—à²³à³
â€¢ e-NAM à²…à²ªà³à²²à²¿à²•à³‡à²¶à²¨à³
â€¢ à²•à²¿à²¸à²¾à²¨à³ à²¸à³à²µà²¿à²§à²¾ à²…à²ªà³à²²à²¿à²•à³‡à²¶à²¨à³

ðŸ“ž à²•à²¿à²¸à²¾à²¨à³ à²•à²¾à²²à³ à²¸à³†à²‚à²Ÿà²°à³: 1800-180-1551 (à²‰à²šà²¿à²¤)""",
}

_FULL_ANSWERS_HI = {
    "fertilizer_general": """à¤¨à¤®à¤¸à¥à¤¤à¥‡ à¤•à¤¿à¤¸à¤¾à¤¨ à¤­à¤¾à¤ˆ! à¤–à¤¾à¤¦/à¤‰à¤°à¥à¤µà¤°à¤• à¤•à¥€ à¤œà¤¾à¤¨à¤•à¤¾à¤°à¥€:

**à¤ªà¥à¤°à¤®à¥à¤– à¤‰à¤°à¥à¤µà¤°à¤• à¤”à¤° à¤‰à¤¨à¤•à¤¾ à¤‰à¤ªà¤¯à¥‹à¤—:**
â€¢ **à¤¯à¥‚à¤°à¤¿à¤¯à¤¾ (46% N)** â†’ à¤ªà¥Œà¤§à¥‹à¤‚ à¤•à¥‹ à¤¹à¤°à¤¾ à¤”à¤° à¤²à¤‚à¤¬à¤¾ à¤¬à¤¨à¤¾à¤¤à¤¾ à¤¹à¥ˆà¥¤ à¤Ÿà¥‰à¤ª-à¤¡à¥à¤°à¥‡à¤¸à¤¿à¤‚à¤— à¤•à¥‡ à¤°à¥‚à¤ª à¤®à¥‡à¤‚ à¤¡à¤¾à¤²à¥‡à¤‚à¥¤
â€¢ **DAP (18-46-0)** â†’ à¤«à¥‰à¤¸à¥à¤«à¥‹à¤°à¤¸ â€” à¤œà¤¡à¤¼à¥‹à¤‚ à¤•à¥€ à¤®à¤œà¤¬à¥‚à¤¤à¥€ à¤”à¤° à¤¶à¥à¤°à¥à¤†à¤¤à¥€ à¤µà¤¿à¤•à¤¾à¤¸ à¤•à¥‡ à¤²à¤¿à¤à¥¤
â€¢ **MOP (0-0-60)** â†’ à¤ªà¥‹à¤Ÿà¤¾à¤¶ â€” à¤¬à¤¡à¤¼à¥‡ à¤«à¤², à¤°à¥‹à¤— à¤ªà¥à¤°à¤¤à¤¿à¤°à¥‹à¤§à¤• à¤•à¥à¤·à¤®à¤¤à¤¾à¥¤
â€¢ **SSP (0-16-0+S)** â†’ à¤«à¥‰à¤¸à¥à¤«à¥‹à¤°à¤¸ + à¤¸à¤²à¥à¤«à¤° à¤•à¤¾ à¤¸à¤¸à¥à¤¤à¤¾ à¤¸à¥à¤°à¥‹à¤¤à¥¤
â€¢ **NPK 17:17:17** â†’ à¤¸à¤‚à¤¤à¥à¤²à¤¿à¤¤ â€” à¤¸à¤­à¥€ à¤šà¤°à¤£à¥‹à¤‚ à¤®à¥‡à¤‚ à¤‰à¤ªà¤¯à¥‹à¤—à¥€à¥¤
â€¢ **à¤—à¥‹à¤¬à¤° à¤–à¤¾à¤¦/à¤•à¤®à¥à¤ªà¥‹à¤¸à¥à¤Ÿ** â†’ à¤®à¤¿à¤Ÿà¥à¤Ÿà¥€ à¤•à¥€ à¤¸à¥‡à¤¹à¤¤ à¤¸à¥à¤§à¤¾à¤°à¤¤à¤¾ à¤¹à¥ˆà¥¤

**à¤®à¤¹à¤¤à¥à¤µà¤ªà¥‚à¤°à¥à¤£ à¤¨à¤¿à¤¯à¤®:**
â€¢ à¤ªà¤¹à¤²à¥‡ à¤®à¤¿à¤Ÿà¥à¤Ÿà¥€ à¤•à¥€ à¤œà¤¾à¤‚à¤š à¤•à¤°à¥‡à¤‚ â€” à¤œà¥à¤¯à¤¾à¤¦à¤¾ à¤–à¤¾à¤¦ à¤¨à¥à¤•à¤¸à¤¾à¤¨à¤¦à¤¾à¤¯à¤• à¤¹à¥ˆ
â€¢ 2â€“3 à¤¬à¤¾à¤° à¤®à¥‡à¤‚ à¤¡à¤¾à¤²à¥‡à¤‚ â€” à¤…à¤šà¥à¤›à¤¾ à¤…à¤µà¤¶à¥‹à¤·à¤£, à¤•à¤® à¤¬à¤°à¥à¤¬à¤¾à¤¦à¥€
â€¢ à¤¬à¤¾à¤°à¤¿à¤¶ à¤¸à¥‡ à¤ªà¤¹à¤²à¥‡ à¤¨à¤¹à¥€à¤‚ à¤¡à¤¾à¤²à¥‡à¤‚ â€” à¤¬à¤¹ à¤œà¤¾à¤à¤—à¤¾

ðŸ“ž à¤•à¤¿à¤¸à¤¾à¤¨ à¤•à¥‰à¤² à¤¸à¥‡à¤‚à¤Ÿà¤°: 1800-180-1551 (à¤¨à¤¿à¤ƒà¤¶à¥à¤²à¥à¤•)""",

    "pm_kisan": """à¤¨à¤®à¤¸à¥à¤¤à¥‡ à¤•à¤¿à¤¸à¤¾à¤¨ à¤­à¤¾à¤ˆ! PM-KISAN à¤¯à¥‹à¤œà¤¨à¤¾ à¤•à¥€ à¤œà¤¾à¤¨à¤•à¤¾à¤°à¥€:

**PM-KISAN â€” à¤ªà¥à¤°à¤§à¤¾à¤¨à¤®à¤‚à¤¤à¥à¤°à¥€ à¤•à¤¿à¤¸à¤¾à¤¨ à¤¸à¤®à¥à¤®à¤¾à¤¨ à¤¨à¤¿à¤§à¤¿:**

**à¤²à¤¾à¤­:** â‚¹6,000 à¤ªà¥à¤°à¤¤à¤¿ à¤µà¤°à¥à¤· â€” à¤¤à¥€à¤¨ à¤•à¤¿à¤¸à¥à¤¤à¥‹à¤‚ à¤®à¥‡à¤‚ â‚¹2,000 à¤ªà¥à¤°à¤¤à¥à¤¯à¥‡à¤•

**à¤•à¥Œà¤¨ à¤ªà¤¾à¤¤à¥à¤° à¤¹à¥ˆ:**
â€¢ à¤¸à¤­à¥€ à¤­à¥‚à¤®à¤¿ à¤§à¤¾à¤°à¤• à¤•à¤¿à¤¸à¤¾à¤¨ à¤œà¤¿à¤¨à¤•à¥‡ à¤ªà¤¾à¤¸ à¤†à¤§à¤¾à¤° à¤¹à¥ˆ

**à¤†à¤µà¥‡à¤¦à¤¨ à¤•à¥ˆà¤¸à¥‡ à¤•à¤°à¥‡à¤‚:**
â€¢ à¤‘à¤¨à¤²à¤¾à¤‡à¤¨: **pmkisan.gov.in** à¤ªà¤° à¤œà¤¾à¤à¤‚
â€¢ à¤¨à¤œà¤¦à¥€à¤•à¥€ **CSC (à¤•à¥‰à¤®à¤¨ à¤¸à¤°à¥à¤µà¤¿à¤¸ à¤¸à¥‡à¤‚à¤Ÿà¤°)** à¤ªà¤° à¤œà¤¾à¤à¤‚
â€¢ à¤²à¥‡ à¤œà¤¾à¤à¤‚: à¤†à¤§à¤¾à¤° + à¤¬à¥ˆà¤‚à¤• à¤ªà¤¾à¤¸à¤¬à¥à¤• + à¤œà¤®à¥€à¤¨ à¤•à¥‡ à¤¦à¤¸à¥à¤¤à¤¾à¤µà¥‡à¤œ

**à¤¸à¥à¤¥à¤¿à¤¤à¤¿ à¤œà¤¾à¤‚à¤šà¥‡à¤‚:** pmkisan.gov.in à¤ªà¤° à¤…à¤ªà¤¨à¤¾ à¤†à¤§à¤¾à¤° à¤¨à¤‚à¤¬à¤° à¤¡à¤¾à¤²à¤•à¤°

à¤¹à¥‡à¤²à¥à¤ªà¤²à¤¾à¤‡à¤¨: **155261**
ðŸ“ž à¤•à¤¿à¤¸à¤¾à¤¨ à¤•à¥‰à¤² à¤¸à¥‡à¤‚à¤Ÿà¤°: 1800-180-1551 (à¤¨à¤¿à¤ƒà¤¶à¥à¤²à¥à¤•)""",
}


def _localize_answer(answer: str, lang: str, message: str = "") -> str:
    """Supported: en (unchanged), hi (Hindi), kn (Kannada)."""
    if lang == "en":
        return answer
    m = message.lower()
    if lang == "kn":
        if any(w in m for w in ["koleroga", "areca", "arecanut", "bunch rot"]):
            return _FULL_ANSWERS_KN.get("koleroga", answer)
        if any(w in m for w in ["arecanut", "adake"]) and any(w in m for w in ["fertilizer", "urea"]):
            return _FULL_ANSWERS_KN.get("arecanut_fertilizer", answer)
        if any(w in m for w in ["price", "market"]) and any(w in m for w in ["arecanut", "adake", "supari"]):
            return _FULL_ANSWERS_KN.get("market_price_arecanut", answer)
    elif lang == "hi":
        if any(w in m for w in ["fertilizer", "urea", "khad"]) and not any(c in m for c in ["paddy", "wheat", "banana"]):
            return _FULL_ANSWERS_HI.get("fertilizer_general", answer)
        if any(w in m for w in ["pm-kisan", "pmkisan", "6000", "yojana"]):
            return _FULL_ANSWERS_HI.get("pm_kisan", answer)
    intent = detect_intent(answer[:200])
    hdr    = _TRANSLATIONS["intent_hdr"].get(intent, {}).get(lang, "")
    footer = _TRANSLATIONS["note"].get(lang, "")
    greet  = {"hi": "Namaste Kisan Bhai!\n\n", "kn": "Namaskara Raita Anna!\n\n"}.get(lang, "")
    return "".join(p for p in [greet, hdr + "\n\n" if hdr else "", answer, footer] if p)


async def ask_granite(message: str) -> str:
    """Try IBM WatsonX first; fall back to smart_answer with native-language wrapping."""
    clean_msg, lang = _extract_lang(message)

    # â”€â”€ Try IBM WatsonX if key looks real â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if WATSONX_API_KEY and "your-" not in WATSONX_API_KEY and "PASTE" not in WATSONX_API_KEY:
        context = "\n".join(KB.values())
        lang_names = {"hi": "Hindi", "kn": "Kannada", "ta": "Tamil", "te": "Telugu", "mr": "Marathi"}
        lang_instruction = ""
        if lang != "en":
            lang_instruction = f"\nIMPORTANT: Respond ENTIRELY in {lang_names.get(lang, 'English')}. Every word must be in {lang_names.get(lang, 'English')}."
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
        except Exception:
            pass  # fall through to smart_answer below

    # â”€â”€ Fallback: smart_answer + native-language wrapping (no IBM needed) â”€â”€â”€â”€
    answer = smart_answer(clean_msg)
    return _localize_answer(answer, lang, clean_msg)


# â”€â”€ API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
        "ibm_key": "âœ… IBM Granite AI connected" if ibm_ok else "âš ï¸ Demo mode (no IBM key)",
    }


# â”€â”€ Serve frontend â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
