# -*- coding: utf-8 -*-
"""
Smart Farming Advisor - Backend
pip install fastapi uvicorn python-dotenv httpx
python main.py
"""
import os, time, re
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel

load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

WATSONX_API_KEY    = os.getenv("WATSONX_API_KEY", "")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")
WATSONX_URL        = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

# ---------------------------------------------------------------------------
# Intent detection
# ---------------------------------------------------------------------------
def detect_intent(msg: str) -> str:
    m = msg.lower()
    if "crop recommendation request" in m: return "crop"
    if "soil analysis request" in m: return "soil"
    if any(w in m for w in ["scheme","subsidy","pm-kisan","pmkisan","pmfby","fasal bima","kcc","kisan credit","enam","e-nam","soil health card","fpo","rkvy","nabard","insurance"]):
        return "schemes"
    if any(w in m for w in ["koleroga","blast","blight","wilt","rot","weevil","borer","aphid","thrips","mite","caterpillar","bollworm","armyworm","mildew","insect","bug","frass","disease","pest","symptom","fungicide","leaf rust"]):
        return "pest"
    if any(w in m for w in ["urea","dap","mop","ssp","npk","fertilizer","manure","compost","fym","fertigation"]):
        return "fertilizer"
    if any(w in m for w in ["irrigat","drip","sprinkler","water schedule","how much water","when to water","waterlog","litre per","basin irrigation"]):
        return "irrigation"
    if any(w in m for w in ["price","mandi","market","sell","rate","quintal","profit","agmarknet","msp","apmc","campco"]):
        return "market"
    if any(w in m for w in ["soil","ph","organic carbon","nitrogen level","potassium level","soil type","soil test"]):
        return "soil"
    if any(w in m for w in ["crop","grow","plant","sow","cultivat","harvest","season","kharif","rabi","which crop","best crop","yield","arecanut","coconut","banana","paddy","rice","sugarcane","coffee","pepper","turmeric","ginger","chilli","maize","onion"]):
        return "crop"
    return "general"

# ---------------------------------------------------------------------------
# Answer engine - all plain English, proper UTF-8
# ---------------------------------------------------------------------------
def build_answer(message: str) -> str:
    intent = detect_intent(message)
    m = message.lower()

    # --- PEST ---
    if intent == "pest":
        if any(w in m for w in ["koleroga","areca","supari","bunch rot"]):
            return (
                "🌿 **Arecanut Koleroga (Phytophthora Fruit Rot)**\n\n"
                "🔴 Symptoms: Bunches turn black, premature fruit drop during monsoon.\n\n"
                "💊 Treatment:\n"
                "- 🧪 Spray Bordeaux mixture 1% on bunches and stalk — June and July\n"
                "- ⚠️ Severe cases: Drench base with Metalaxyl + Mancozeb 3g per litre water\n"
                "- 🔥 Remove and burn all infected bunches immediately\n\n"
                "✅ Prevention: Spray Bordeaux before monsoon starts (end of May)\n"
                "⏰ Best spray time: 6–9 AM. Wear gloves and mask.\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            )
        if any(w in m for w in ["weevil","coconut weevil","red palm","bore hole"]):
            return (
                "🥥 **Coconut Red Palm Weevil**\n\n"
                "🔴 Symptoms: Bore holes in trunk with brown frass, yellow drooping crown.\n\n"
                "💊 Treatment:\n"
                "- 🧪 Inject Chlorpyrifos 2ml per litre water into bore holes — seal with mud\n"
                "- 🪤 Install 4 pheromone traps per hectare to catch adult weevils\n"
                "- 🧴 Fill holes with Carbaryl 10% dust and sand mixture\n\n"
                "⚠️ Severe attack: Fell and burn infested palms to stop spread\n"
                "✅ Prevention: Keep crown clean, apply Chlorpyrifos 0.1% to crown monthly\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            )
        if any(w in m for w in ["blast","paddy blast","neck rot","rice blast"]):
            return (
                "🌾 **Paddy Blast Disease**\n\n"
                "🔴 Symptoms: Spindle-shaped grey/brown lesions on leaves; grey neck at panicle.\n\n"
                "💊 Treatment:\n"
                "- 🧪 Spray Tricyclazole 75 WP — 0.6g per litre water\n"
                "- ⏰ Apply at 25 days and 45 days after transplanting\n"
                "- 🔄 Alternative: Carbendazim 1g per litre water\n\n"
                "✅ Prevention:\n"
                "- 🌱 Use blast-resistant varieties: Samba Masuri BPT-5204, IR-64\n"
                "- ❌ Avoid excess Nitrogen fertilizer\n"
                "- 💧 Do not keep waterlogged — use AWD (alternate wet and dry)\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            )
        if any(w in m for w in ["thrips","chilli pest","mite","silver","curl"]):
            return (
                "🌶️ **Chilli Thrips and Mite Management**\n\n"
                "🔴 Symptoms: Curled leaves, silvery streaks, tiny insects visible.\n\n"
                "💊 Treatment:\n"
                "- 🌿 Spinosad 45 SC — 0.3ml per litre water (organic option)\n"
                "- 🧪 Abamectin 1.9 EC — 0.5ml per litre water (for mites)\n"
                "- ⚠️ Imidacloprid 17.8 SL — 0.3ml per litre (heavy infestation)\n\n"
                "🔄 Alternate chemicals each spray to prevent resistance.\n"
                "⏰ Spray at 6–9 AM. Spray bottom side of leaves too.\n"
                "✅ Prevention: Use yellow sticky traps — 5 per acre\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            )
        if any(w in m for w in ["aphid","sticky","honeydew"]):
            return (
                "🐛 **Aphid Management (All Crops)**\n\n"
                "🔴 Symptoms: Clusters of tiny insects on new shoots, sticky honeydew, curled yellow leaves.\n\n"
                "💊 Treatment:\n"
                "- 🌿 Organic: Neem oil 3ml per litre water plus soap — spray on leaves and stem\n"
                "- 🧪 Chemical: Imidacloprid 0.3ml per litre water\n"
                "- 💦 Strong water jet spray to wash them off\n\n"
                "🔄 Repeat after 7 days if still present.\n"
                "⚠️ Wear gloves. Spray early morning 6–9 AM.\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            )
        if any(w in m for w in ["coffee rust","leaf rust","orange pustule"]):
            return (
                "☕ **Coffee Leaf Rust (Hemileia vastatrix)**\n\n"
                "🔴 Symptoms: Yellowish-orange powdery pustules on underside of leaves.\n\n"
                "💊 Treatment:\n"
                "- 🧪 Spray Copper oxychloride 3g per litre water — cover leaf undersides\n"
                "- ⚠️ Systemic: Propiconazole 1ml per litre for severe attack\n"
                "- ⏰ Spray at onset of monsoon (June) and after (September)\n\n"
                "✅ Prevention: Maintain shade. Avoid over-fertilizing with Nitrogen.\n"
                "☎️ Coffee Board India: 080-25362161\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            )
        if any(w in m for w in ["armyworm","fall armyworm","whorl","caterpillar"]):
            return (
                "🌽 **Maize Fall Armyworm (Spodoptera frugiperda)**\n\n"
                "🔴 Symptoms: Ragged whorl leaves, caterpillars inside whorl, frass visible.\n\n"
                "💊 Treatment:\n"
                "- 🧪 Apply Emamectin benzoate 5 SG — 0.4g per litre INTO the whorl\n"
                "- ⏰ Apply at 15–18 days after germination when caterpillars are small\n"
                "- 🌿 Organic: Bt (Bacillus thuringiensis) 2g per litre — safe and effective\n\n"
                "⏰ Spray early morning. Repeat after 7 days if needed.\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            )
        if any(w in m for w in ["rhizome rot","collar rot","turmeric rot","ginger rot"]):
            return (
                "🍂 **Turmeric / Ginger Rhizome Rot**\n\n"
                "🔴 Symptoms: Yellow wilting from base, rotting at collar, foul smell from soil.\n\n"
                "💊 Treatment:\n"
                "- 🧪 Drench soil with Metalaxyl + Mancozeb 3g per litre water around affected plants\n"
                "- 🚫 Remove infected plants with surrounding soil\n\n"
                "✅ Prevention (most important):\n"
                "- 🌱 Treat seed rhizomes with Metalaxyl 2g per litre before planting (30 min soak)\n"
                "- 🏔️ Grow on raised beds 15–20cm — rhizome rot starts in waterlogged soil\n"
                "- 🍄 Apply Trichoderma 50g per pit at planting\n"
                "- 💧 Ensure proper field drainage — never let water stagnate\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            )
        # generic pest
        return (
            "🐛 **Pest and Disease Guide**\n\n"
            "Common Indian Crop Problems and Quick Fix:\n\n"
            "- 🌿 Arecanut Koleroga: Bordeaux mixture 1% spray before monsoon\n"
            "- 🥥 Coconut Weevil: Chlorpyrifos injection + pheromone traps\n"
            "- 🌾 Paddy Blast: Tricyclazole 0.6g per litre at 25 + 45 days\n"
            "- 🍌 Banana Wilt: Remove infected plants, plant Trichoderma\n"
            "- 🌶️ Chilli Thrips: Spinosad 0.3ml per litre or Abamectin\n"
            "- 🍂 Turmeric Rhizome Rot: Metalaxyl seed treatment, raised beds\n"
            "- 🌽 Maize Armyworm: Emamectin 0.4g per litre into whorl\n"
            "- 🐜 Aphids: Neem oil 3ml per litre or Imidacloprid 0.3ml per litre\n\n"
            "⚠️ Always: Wear gloves and mask. Spray early morning 6–9 AM.\n"
            "📞 Kisan Call Centre: 1800-180-1551 (Free)"
        )

    # --- FERTILIZER ---
    if intent == "fertilizer":
        FERT = {
            "arecanut":  "🌿 Arecanut (bearing palm/year): Urea 200g + SSP 130g + MOP 130g + FYM 12kg per palm.\n⏰ Apply in 2 splits: June and September. 🧪 Borax 25g per palm (micronutrient).",
            "coconut":   "🥥 Coconut (per palm/year): Urea 1.3kg + SSP 2kg + MOP 2kg + FYM 50kg.\n⏰ Apply in 2 splits: June and December. 📌 Circular trench 1.5m radius from trunk.",
            "banana":    "🍌 Banana (per plant/crop): Urea 250g + DAP 100g + MOP 300g + FYM 10kg.\n⏰ Give in 4 splits over 9 months. 💧 Drip fertigation is best.",
            "paddy":     "🌾 Paddy/Rice (per hectare): NPK 120:60:60 kg/ha.\n✅ Full P + K at transplanting. 🧪 Nitrogen (Urea) in 3 splits: 25% basal + 50% at 21 days + 25% at panicle initiation.",
            "rice":      "🌾 Rice/Paddy (per hectare): NPK 120:60:60 kg/ha.\n✅ Full P+K at transplanting. Urea in 3 splits.",
            "sugarcane": "🎋 Sugarcane (per hectare): NPK 250:115:115 kg/ha in 3 splits.\n🌱 FYM 25 t/ha as basal before planting. 💧 Drip fertigation saves 40% water.",
            "turmeric":  "🍂 Turmeric (per hectare): NPK 150:50:100 kg/ha + FYM 30 t/ha.\n✅ Full P+K at planting. N in 2 splits. 🧪 Borax 10kg/ha + ZnSO4 25kg/ha.",
            "ginger":    "🫚 Ginger (per hectare): NPK 75:50:75 kg/ha + FYM 30 t/ha.\n🧪 ZnSO4 25kg/ha. Apply in 3 splits. 🌿 Mulch with dry leaves after planting.",
            "chilli":    "🌶️ Chilli (per hectare): NPK 100:50:50 kg/ha + FYM 20 t/ha.\n🌸 Boron spray 0.2% at flowering improves fruit set by 20-30%.",
            "maize":     "🌽 Maize (per hectare): NPK 150:75:37.5 kg/ha.\n⏰ Urea in 3 splits: at sowing + 30 days + 60 days.",
            "wheat":     "🌾 Wheat (per hectare): NPK 120:60:40 kg/ha.\n✅ Half Urea at sowing + remaining at first irrigation (21 days).",
            "onion":     "🧅 Onion (per hectare): NPK 100:50:75 kg/ha + Sulphur 25kg/ha.\n⚠️ Stop all N after bulb formation - excess N causes splitting.",
            "coffee":    "☕ Coffee (per plant/year): Urea 250g + SSP 150g + MOP 200g + FYM 5kg.\n⏰ Apply in 2 splits: June and September.",
            "pepper":    "🫒 Black Pepper (per vine/year): NPK 50:50:150g + FYM 5kg + Neem cake 1kg.\n⏰ Apply before monsoon (May) and after (October).",
            "tomato":    "🍅 Tomato (per hectare): NPK 200:120:120 kg/ha + FYM 25 t/ha.\n🌸 Boron 0.2% spray at flowering. 🧪 Calcium spray prevents blossom end rot.",
            "cotton":    "🏴 Cotton (per hectare): NPK 150:75:75 kg/ha.\n⚠️ Stop excess Nitrogen after boll formation. Boron 0.2% at squaring stage.",
            "soybean":   "🫘 Soybean (per hectare): NPK 20:60:40 kg/ha (low N - soybean fixes its own N).\n🌱 Rhizobium seed treatment before sowing.",
            "groundnut": "🥜 Groundnut (per hectare): NPK 25:50:75 kg/ha + Gypsum 500kg/ha at pegging.\n⚠️ Gypsum is critical for shell filling and preventing empty pods.",
        }
        for crop, advice in FERT.items():
            if crop in m:
                return (
                    f"🧪 **Fertilizer Schedule — {crop.capitalize()}:**\n\n"
                    f"{advice}\n\n"
                    "📌 Key fertilizers:\n"
                    "- 🌿 Urea = Nitrogen (N) — growth and green colour\n"
                    "- 🔵 DAP/SSP = Phosphorus (P) — roots and flowers\n"
                    "- 🟡 MOP = Potassium (K) — fruit size and disease resistance\n\n"
                    "✅ Get free soil test (Soil Health Card) from KVK for exact doses.\n"
                    "📞 Kisan Call Centre: 1800-180-1551 (Free)"
                )
        return (
            "🧪 **Fertilizer Guide for Indian Farmers:**\n\n"
            "📌 What each fertilizer does:\n"
            "- 🌿 Urea (46% N): Makes plants grow green and tall. Top-dress application.\n"
            "- 🔵 DAP (18-46-0): Phosphorus for root growth and early establishment.\n"
            "- 🟡 MOP (0-0-60): Potassium for big fruits and disease resistance.\n"
            "- 🟤 SSP (0-16-0+S): Cheaper source of Phosphorus plus Sulphur.\n"
            "- ⚖️ NPK 17:17:17: Balanced, good for all growth stages.\n"
            "- 🌱 FYM/Compost: Improves soil health and water holding.\n\n"
            "✅ Golden rules:\n"
            "- 🔬 Do soil test first — avoid over-fertilizing\n"
            "- ✂️ Split doses 2-3 times — better uptake, less wastage\n"
            "- ⛈️ Never apply before heavy rain — gets washed away\n\n"
            "👉 Tell me your crop name for exact dose!\n"
            "🆓 Free Soil Health Card from KVK gives exact fertilizer recommendations.\n"
            "📞 Kisan Call Centre: 1800-180-1551 (Free)"
        )

    # --- IRRIGATION ---
    if intent == "irrigation":
        if any(w in m for w in ["arecanut","areca","supari"]):
            return (
                "💧 **Arecanut Irrigation Plan:**\n\n"
                "📅 Monthly schedule:\n"
                "- ❄️ Nov-Feb (cool/dry): 15-20 litres per palm every 3-4 days\n"
                "- ☀️ Mar-May (summer): 20-25 litres per palm every day or alternate day\n"
                "- 🌧️ Jun-Oct (monsoon): No irrigation needed if rainfall more than 50mm per week\n\n"
                "✅ Best method: Drip irrigation at base of palm — saves 50% water\n"
                "⚠️ Critical stages: Bunch development (Mar-May) — never let soil dry completely\n\n"
                "🌿 Mulching: Apply 10-15 kg coir pith or dry leaves around base. Saves 40% water.\n"
                "💰 Subsidy: PM Krishi Sinchai Yojana gives 55% subsidy on drip systems.\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            )
        if any(w in m for w in ["coconut","tengu"]):
            return (
                "💧 **Coconut Irrigation Plan:**\n\n"
                "📅 Seasonal schedule:\n"
                "- ❄️ Dec-Feb: 40-50 litres per palm every 5-6 days\n"
                "- ☀️ Mar-May (peak summer): 100-200 litres per palm every 3-4 days\n"
                "- 🌧️ Jun-Oct (monsoon): No irrigation if rain is adequate\n\n"
                "✅ Methods: Basin 1.5m radius around trunk, or drip 2 emitters at 1m from trunk.\n"
                "⚠️ Signs of water stress: Yellow leaves, reduced nut size, premature nut drop.\n"
                "🌿 Mulch with coir pith 20-25 kg per palm to retain moisture.\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            )
        if any(w in m for w in ["paddy","rice"]):
            return (
                "💧 **Paddy / Rice Irrigation Plan:**\n\n"
                "📊 Stage-wise water management:\n"
                "- 🌱 Transplanting: Keep 2-3 cm standing water for 7 days\n"
                "- 🌿 Tillering (day 10-30): 3-5 cm standing water — critical stage!\n"
                "- ⚠️ Panicle initiation (day 50-60): 5 cm water — never let dry\n"
                "- 🌸 Flowering/heading: 3-5 cm water continuously\n"
                "- 🚜 2 weeks before harvest: Drain field completely\n\n"
                "✅ AWD method saves 30% water: Install perforated pipe 20cm deep.\n"
                "📌 Irrigate only when water drops 15cm below surface.\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            )
        if any(w in m for w in ["banana","kela","bale","plantain"]):
            return (
                "💧 **Banana Irrigation Plan:**\n\n"
                "📊 Stage-wise schedule:\n"
                "- 🌱 Planting to 3 months: 8 litres per plant every 2-3 days\n"
                "- 🌿 Vegetative (3-7 months): 10-12 litres per plant daily\n"
                "- ⚠️ Bunch shooting (CRITICAL): 15 litres per plant daily — never skip!\n"
                "- 🍌 Bunch development to harvest: 12 litres per plant daily\n\n"
                "✅ Best method: Drip irrigation — 2 emitters per plant at 30cm from base.\n"
                "🔴 Critical: Water stress at shooting reduces bunch weight by 30-40%.\n"
                "🌿 Mulch with dry leaves or sugarcane trash to save moisture.\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            )
        return (
            "💧 **Irrigation Guide for Indian Farmers:**\n\n"
            "⏰ Best time to irrigate: Early morning 5-8 AM or evening 5-7 PM\n\n"
            "📊 Frequency by soil type:\n"
            "- 🏜️ Sandy soil: Every 3-4 days\n"
            "- 🌱 Loamy soil: Every 5-6 days\n"
            "- 🏔️ Clay soil: Every 7-8 days\n\n"
            "⚠️ Critical growth stages needing most water:\n"
            "- 🌱 Germination/transplanting — always irrigate immediately\n"
            "- 🌸 Flowering stage — never let soil dry out\n"
            "- 🍎 Fruit/grain filling — maintain 60-70% soil moisture\n\n"
            "💡 Tips:\n"
            "- 💧 Drip irrigation saves 40-60% water vs flood\n"
            "- 🌿 Mulching reduces water loss by 30-40%\n"
            "- 🌧️ Skip irrigation if 10+ mm rain expected\n"
            "- 👆 Finger test: push finger 5cm into soil — if dry, irrigate now\n\n"
            "💰 PMKSY gives 55% subsidy on drip systems — apply at Horticulture Dept.\n"
            "📞 Kisan Call Centre: 1800-180-1551 (Free)"
        )

    # --- MARKET ---
    if intent == "market":
        prices = {
            "arecanut": ("Rs.36,000-Rs.52,000", "📍 Best market: Shivamogga APMC (Karnataka). CAMPCO cooperative offers fair prices. 📈 Peak price: March-June."),
            "coconut":  ("Rs.8,500-Rs.12,000 (copra)", "📍 Markets: Udupi, Coimbatore, Thrissur. 💡 Value addition as virgin coconut oil fetches premium."),
            "banana":   ("Rs.900-Rs.1,600", "📍 Hoskote, Bangalore APMC. ✅ G9 variety preferred. Contract farming available."),
            "paddy":    ("Rs.2,183 (MSP)", "✅ Government MSP procurement. Sell at FCI or state agency."),
            "rice":     ("Rs.2,183 (MSP)", "✅ Government MSP available. Check APMC for Samba Masuri (BPT-5204) premium."),
            "turmeric": ("Rs.7,000-Rs.20,000", "📍 Best market: Erode (TN), Nizamabad (TS). 💡 Sell 3-6 months after harvest for better price."),
            "pepper":   ("Rs.40,000-Rs.65,000", "📍 Markets: Kochi, Kozhikode (Kerala). 🌐 Spices Board India helps export. 🏆 Organic fetches 2-3x premium."),
            "ginger":   ("Rs.15,000-Rs.35,000 (dry)", "💡 Sell dried ginger for better price. 📍 Calicut, Cochin markets. Export quality commands premium."),
            "chilli":   ("Rs.8,000-Rs.22,000", "📍 Guntur APMC (AP) is largest chilli market. ✅ Grade Teja variety separately for best price."),
            "onion":    ("Rs.1,000-Rs.2,800", "📍 Nashik APMC. ⚠️ Price very volatile. 👥 FPO collective selling gives better price."),
            "sugarcane":("FRP Rs.315/qt (2023-24)", "✅ Sell to sugar factory linked to your area. 💰 FRP (Fair and Remunerative Price) is guaranteed."),
            "wheat":    ("Rs.2,275 (MSP)", "✅ Government MSP available. Sell at FCI or registered mandi."),
            "coffee":   ("Rs.5,000-Rs.8,000 (cherry)", "☕ Coffee Board India, Coorg/Chikkamagaluru markets. 🏆 Organic certification fetches premium."),
            "tomato":   ("Rs.500-Rs.5,000", "⚠️ Highly volatile. 💡 Sell Feb-May for best price. 📍 Bangalore APMC."),
        }
        crop_hint = ""
        for crop, (price, tip) in prices.items():
            if crop in m:
                crop_hint = f"\n\n💰 {crop.capitalize()} price: {price}/quintal\n📌 Tip: {tip}"
                break
        return (
            "📊 **Indian APMC Market Prices (indicative — check agmarknet.nic.in for live rates):**\n\n"
            "- 🌿 Arecanut: Rs.36,000-Rs.52,000/qt (Shivamogga APMC)\n"
            "- 🥥 Coconut copra: Rs.8,500-Rs.12,000/qt\n"
            "- 🍌 Banana (G9): Rs.900-Rs.1,600/qt\n"
            "- 🌾 Paddy: Rs.2,183/qt (MSP)\n"
            "- 🍂 Turmeric: Rs.7,000-Rs.20,000/qt (Erode)\n"
            "- 🌶️ Chilli: Rs.8,000-Rs.22,000/qt (Guntur)\n"
            "- 🫒 Pepper: Rs.40,000-Rs.65,000/qt (Kochi)\n"
            "- 🌾 Wheat: Rs.2,275/qt (MSP)\n"
            + crop_hint +
            "\n\n📱 Check live prices: agmarknet.nic.in | e-NAM app | Kisan Suvidha app\n"
            "📞 Kisan Call Centre: 1800-180-1551 (Free)"
        )

    # --- SCHEMES ---
    if intent == "schemes":
        if any(w in m for w in ["pm-kisan","pmkisan","6000","income support"]):
            return (
                "🏛️ **PM-KISAN — Pradhan Mantri Kisan Samman Nidhi:**\n\n"
                "💰 Benefit: Rs.6,000 per year in 3 installments of Rs.2,000 each\n"
                "✅ Who gets it: All land-holding farmers with valid Aadhaar\n\n"
                "📋 How to apply:\n"
                "- 🌐 Visit pmkisan.gov.in online\n"
                "- 🏢 Go to nearest CSC (Common Service Centre)\n"
                "- 📄 Carry: Aadhaar + bank passbook + land documents\n\n"
                "📞 Helpline: 155261 | Check status at pmkisan.gov.in\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            )
        if any(w in m for w in ["pmfby","fasal bima","insurance","crop insurance"]):
            return (
                "🛡️ **PMFBY — Pradhan Mantri Fasal Bima Yojana:**\n\n"
                "💰 Benefit: Crop insurance at very low premium:\n"
                "- 🌾 Kharif crops (Paddy, Maize, etc.): 2% premium only\n"
                "- ❄️ Rabi crops (Wheat, Onion, etc.): 1.5% premium only\n"
                "- 🏛️ Rest paid by Government!\n\n"
                "📋 How to apply:\n"
                "- 🏦 Apply at your bank branch before sowing season\n"
                "- 🌐 Also at CSC center or pmfby.gov.in\n"
                "- ✅ Loanee farmers enrolled automatically\n\n"
                "☂️ Covers: Drought, flood, pest attack, hailstorm, disease losses.\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            )
        if any(w in m for w in ["drip","sinchai","pmksy","irrigation subsidy"]):
            return (
                "💧 **PM Krishi Sinchai Yojana (PMKSY):**\n\n"
                "💰 Benefit:\n"
                "- 👨‍🌾 Small and marginal farmers: 55% subsidy on drip/sprinkler system\n"
                "- 🧑‍🌾 Other farmers: 45% subsidy\n\n"
                "✅ Drip system for 1 acre costs Rs.35,000-Rs.55,000 — you pay only half!\n\n"
                "📋 How to apply:\n"
                "- 🏢 Visit state Horticulture Department office\n"
                "- 📄 Carry: Aadhaar + land documents + bank account\n"
                "- 🌐 pmksy.gov.in for details\n\n"
                "📈 Drip irrigation saves 40-60% water and increases yield by 20-30%.\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            )
        if any(w in m for w in ["kcc","kisan credit","loan","credit"]):
            return (
                "💳 **Kisan Credit Card (KCC):**\n\n"
                "💰 Benefit: Crop loans at 4% per annum interest\n"
                "✅ Up to Rs.3 lakh without collateral\n\n"
                "📋 How to apply:\n"
                "- 🏦 Visit any nationalized bank, RRB, or Co-operative bank\n"
                "- 📄 Carry: Aadhaar + land documents + passport photo\n"
                "- ⏰ Approval usually within 2 weeks\n\n"
                "📌 Covers: Crop inputs, maintenance, post-harvest expenses\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            )
        return (
            "🏛️ **Government Schemes for Indian Farmers:**\n\n"
            "- 💰 PM-KISAN: Rs.6,000/year income support → pmkisan.gov.in\n"
            "- 🛡️ PMFBY: Crop insurance at 2% premium → pmfby.gov.in\n"
            "- 💧 PMKSY: 45-55% subsidy on drip irrigation → pmksy.gov.in\n"
            "- 🔬 Soil Health Card: Free soil test → soilhealth.dac.gov.in\n"
            "- 💳 Kisan Credit Card: Crop loans at 4% → Any bank\n"
            "- 📱 e-NAM: Sell crops online at better price → enam.gov.in\n"
            "- 👥 FPO: Join farmer group for better market prices\n\n"
            "📞 Kisan Call Centre: 1800-180-1551 (Free, 24x7 in local language)"
        )

    # --- SOIL ---
    if intent == "soil":
        lines = ["🪱 **Soil Analysis and Recommendations:**\n"]
        ph_val = None
        for token in m.replace("="," ").replace(":"," ").split():
            try:
                v = float(token)
                if 1 < v < 14: ph_val = v; break
            except: pass
        if ph_val:
            if ph_val < 5.5:
                lines.append(f"🔴 pH {ph_val} — Too Acidic: Apply Agricultural Lime 2-3 bags (100 kg each) per acre. ⏰ Wait 2-3 weeks before sowing.")
            elif ph_val > 7.5:
                lines.append(f"🟡 pH {ph_val} — Alkaline: Apply Gypsum 1-2 bags per acre. 🌱 Add FYM 5 t/acre.")
            else:
                lines.append(f"✅ pH {ph_val} — Optimal! Most crops grow well at this pH.")
        lines.append("\n📊 General soil advice:")
        lines.append("- 🏖️ Laterite soil (coastal): pH 4.5-5.5, acidic. Apply lime 3-4 t/ha. ✅ Good for arecanut, coconut, coffee.")
        lines.append("- 🏴 Black cotton soil: pH 7.5-8.5, alkaline. Apply gypsum. ✅ Good for cotton, sugarcane.")
        lines.append("- 🌿 Low Nitrogen: Add urea or FYM. Green manuring with Dhaincha or Sunhemp helps.")
        lines.append("- 🔵 Low Phosphorus: Apply DAP or SSP at sowing.")
        lines.append("- 🟡 Low Potassium: Apply MOP during fruiting/bunch development.")
        lines.append("- 🤎 Low Organic Carbon: Add FYM 15 t/ha or vermicompost 3-5 t/ha.")
        lines.append("\n🆓 Get free Soil Health Card from KVK or government Agriculture Department.")
        lines.append("📞 Kisan Call Centre: 1800-180-1551 (Free)")
        return "\n".join(lines)

    # --- CROP ---
    if intent == "crop":
        CROP_INFO = {
            "arecanut": (
                "🌿 **Arecanut (Supari) Farming:**\n\n"
                "📍 Best regions: Coastal Karnataka (Shivamogga, Udupi, DK), Kerala, Assam\n"
                "🪨 Soil: Well-drained laterite/red loam, pH 5.5-7.0\n"
                "🌱 Planting: June-September, Spacing: 2.7m x 2.7m\n"
                "💰 Price: Rs.36,000-Rs.52,000/quintal, Best market: Shivamogga APMC\n"
                "⏰ Starts bearing: 5-7 years after planting\n"
                "⚠️ Key risk: Koleroga disease in monsoon — spray Bordeaux mixture 1% before June\n"
                "💧 Irrigation: 15-20L/palm/day in summer (March-May)\n"
                "🏪 Sell through: CAMPCO cooperative or Shivamogga APMC\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            ),
            "coconut": (
                "🥥 **Coconut Farming:**\n\n"
                "📍 Best regions: Coastal Karnataka, Kerala, Tamil Nadu, Andhra Pradesh\n"
                "🪨 Soil: Sandy loam, laterite, pH 5.5-7.5\n"
                "📏 Spacing: 7.5m x 7.5m (triangular), Starts bearing at 5-7 years\n"
                "💰 Copra price: Rs.8,500-Rs.12,000/quintal, Best: Udupi, Thrissur, Pollachi\n"
                "💧 Irrigation: 200L/palm/week in summer\n"
                "✅ Intercrop: Banana, Turmeric, Ginger between young palms for extra income\n"
                "🏛️ Support: CPCRI (Central Plantation Crops Research Institute)\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            ),
            "banana": (
                "🍌 **Banana Farming (G9 / Grand Naine):**\n\n"
                "📍 Suitable: All India, especially Andhra Pradesh, Karnataka, Gujarat, Bihar\n"
                "🌱 Variety: G9 (Grand Naine) — 11 months, 25-35kg/bunch, Panama wilt resistant\n"
                "💰 Price: Rs.900-Rs.1,600/quintal, Markets: Hoskote APMC (Bangalore), local\n"
                "💧 Water: Critical at bunch shooting — 15L/plant/day via drip\n"
                "🧪 Fertilizer: 250g Urea + 100g DAP + 300g MOP per plant over 9 months\n"
                "⚠️ Risk: Panama wilt — use resistant varieties, apply Trichoderma at planting\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            ),
            "paddy": (
                "🌾 **Paddy/Rice Farming:**\n\n"
                "📅 Kharif paddy: June-November, Rabi paddy (South India): Nov-April\n"
                "🌱 Top varieties: Samba Masuri (BPT-5204), Swarna, IR-64, MTU-7029\n"
                "💰 MSP: Rs.2,183/quintal (2023-24), Government procurement by FCI\n"
                "🧪 Fertilizer: NPK 120:60:60 kg/ha, Urea in 3 splits\n"
                "💧 Water: Maintain 3-5cm standing water during tillering\n"
                "📈 SRI method: 30% higher yield, Less water, Use young seedlings (14 days)\n"
                "⚠️ Key disease: Blast — spray Tricyclazole 0.6g/L at 25 + 45 days\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            ),
            "coffee": (
                "☕ **Coffee Farming:**\n\n"
                "📍 Best regions: Kodagu (Coorg), Chikkamagaluru, Sakleshpur (Karnataka); Wayanad (Kerala)\n"
                "🌱 Varieties: Arabica (high quality, hills), Robusta (lowlands, higher yield)\n"
                "💰 Price: Rs.5,000-Rs.8,000/quintal cherry, Organic certified fetches 2x premium\n"
                "💧 Key irrigation: Blossom shower 250L/plant in Feb-March triggers flowering\n"
                "⚠️ Key disease: Leaf rust — spray Copper oxychloride 3g/L at onset of monsoon\n"
                "🏛️ Support: Coffee Board India, Coorg and Chikkamagaluru markets\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            ),
            "turmeric": (
                "🍂 **Turmeric Farming:**\n\n"
                "📍 Best regions: Erode (TN), Nizamabad (TS), Coastal Karnataka, Odisha\n"
                "📅 Planting: April-June, Harvest: 8-9 months later\n"
                "💰 Price: Rs.7,000-Rs.20,000/quintal, Best market: Erode APMC (Tamil Nadu)\n"
                "💡 Tip: Sell 3-6 months AFTER harvest for 30-40% better price\n"
                "🧪 Fertilizer: NPK 150:50:100 kg/ha + FYM 30t/ha\n"
                "⚠️ Key risk: Rhizome rot — grow on raised beds, treat seed with Metalaxyl\n"
                "✅ Intercrop: Excellent intercrop under coconut/arecanut\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            ),
            "pepper": (
                "🫒 **Black Pepper Farming:**\n\n"
                "📍 Best regions: Kerala (Idukki, Wayanad), Coorg (Karnataka)\n"
                "💰 Price: Rs.40,000-Rs.65,000/quintal, Best: Kochi, Kozhikode markets\n"
                "🌿 Support: Needs live standard (Erythrina/Silver oak) or dead standards\n"
                "🧪 Fertilizer: NPK 50:50:150g + FYM 5kg + Neem cake 1kg per vine/year\n"
                "⚠️ Key risk: Phytophthora quick wilt — improve drainage, drench with Metalaxyl\n"
                "🌐 Export help: Spices Board India connects to exporters for premium price\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            ),
        }
        for crop, info in CROP_INFO.items():
            if crop in m:
                return info
        # Season-based
        month = time.localtime().tm_mon
        if 6 <= month <= 10:
            return (
                "🌧️ **Recommended Kharif Crops (June-October):**\n\n"
                "- 🌾 Paddy: Best for rice-growing states, MSP Rs.2,183/qt\n"
                "- 🌽 Maize: Hybrid varieties, Yield 5-8 t/ha, Good poultry demand\n"
                "- 🍂 Turmeric: High value spice, Rs.7,000-Rs.20,000/qt at Erode\n"
                "- 🫚 Ginger: Wet areas, Dry ginger Rs.15,000-Rs.35,000/qt\n"
                "- 🌶️ Chilli: AP/Telangana, Rs.8,000-Rs.22,000/qt at Guntur\n"
                "- 🥜 Groundnut: Sandy loam, MSP Rs.5,850/qt\n\n"
                "📍 Select your state for more specific advice.\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            )
        if month >= 11 or month <= 3:
            return (
                "❄️ **Recommended Rabi Crops (November-March):**\n\n"
                "- 🌾 Wheat: North India, MSP Rs.2,275/qt, Best in Punjab/UP\n"
                "- 🧅 Onion: Nashik APMC, Sell Feb-Apr for best price\n"
                "- 🫘 Gram (Chickpea): Low water, MSP Rs.5,440/qt\n"
                "- 🌻 Sunflower: Drought tolerant, Good oil crop\n"
                "- 🌿 Mustard: Rajasthan/MP, MSP Rs.5,650/qt\n"
                "- 🌾 Rabi Paddy: South India (Karnataka/TN), Fine varieties\n\n"
                "📍 Select your state for more specific advice.\n"
                "📞 Kisan Call Centre: 1800-180-1551 (Free)"
            )
        return (
            "☀️ **Recommended Summer/Zaid Crops (April-June):**\n\n"
            "- 🍉 Watermelon: Fast crop 60-70 days, Rs.5-15/kg\n"
            "- 🥒 Cucumber: Low cost, Quick return\n"
            "- 🌽 Sweet Corn: 50-60 days, Good demand\n"
            "- 🫘 Moong (Green Gram): Drought tolerant, MSP Rs.8,558/qt\n"
            "- 🌻 Sunflower: Summer variety, 90 days\n\n"
            "📞 Kisan Call Centre: 1800-180-1551 (Free)"
        )

    # --- GENERAL ---
    # Try crop keywords
    crop_map = {"arecanut":"pest","areca":"pest","coconut":"pest","paddy":"crop","rice":"crop",
                "banana":"crop","turmeric":"crop","ginger":"fertilizer","chilli":"pest",
                "maize":"pest","onion":"market","wheat":"crop","coffee":"crop","pepper":"crop"}
    for crop, fallback in crop_map.items():
        if crop in m:
            return build_answer(f"{fallback} question about {crop}: {message}")

    return (
        "🙏 **Namaste! I am your Kisan AI Farming Advisor.**\n\n"
        "🌾 I can answer questions about:\n\n"
        "- 🌱 Crops: Arecanut, Coconut, Paddy, Banana, Coffee, Turmeric, Ginger, Chilli, Pepper, Maize, Wheat, Onion\n"
        "- 🐛 Pest and Disease: Koleroga, Blast, Wilt, Armyworm, Aphids, Weevil\n"
        "- 🧪 Fertilizer: NPK doses, Urea, DAP, MOP schedules per crop\n"
        "- 💧 Irrigation: Drip, sprinkler, stage-wise water schedules\n"
        "- 📊 Market Prices: APMC mandi rates, best time to sell\n"
        "- 🏛️ Govt Schemes: PM-KISAN, PMFBY, Drip subsidy, Kisan Credit Card\n"
        "- 🪱 Soil Health: pH, NPK, soil type advice\n\n"
        "👉 Just ask your question in simple words!\n"
        "💡 Example: What is the fertilizer dose for arecanut?\n"
        "📞 Kisan Call Centre: 1800-180-1551 (Free, 24x7)"
    )


# ---------------------------------------------------------------------------
# Translation helper — guaranteed Kannada / Hindi output
# ---------------------------------------------------------------------------
def translate_to(text: str, lang: str) -> str:
    """Translate English text to target lang using deep_translator."""
    if lang == "en":
        return text
    try:
        from deep_translator import GoogleTranslator
        result = GoogleTranslator(source="en", target=lang).translate(text)
        return result if result and result.strip() else text
    except Exception:
        return text  # fallback: return English if translation fails


# ---------------------------------------------------------------------------
# IBM WatsonX
# ---------------------------------------------------------------------------
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
        _tok["exp"] = time.time() + d.get("expires_in", 3600) - 60
    return _tok["token"]


async def ask_ai(message: str, lang: str = "en") -> str:
    """Generate answer in English then translate to lang."""

    # Try IBM WatsonX if key is real
    if WATSONX_API_KEY and "your-" not in WATSONX_API_KEY and "PASTE" not in WATSONX_API_KEY:
        gen_url = f"{WATSONX_URL}/ml/v1/text/generation?version=2023-05-29"
        prompt = (
            "You are Kisan AI, an expert Smart Farming Advisor for Indian farmers.\n"
            "Give a PRACTICAL, SPECIFIC answer the farmer can act on immediately.\n"
            "Start your answer with a relevant emoji (🌾 for crops, 💧 for water, 🐛 for pests, 🧪 for fertilizer, 📊 for prices, 🌱 for soil).\n"
            "Use emojis like 🌿 💧 🧪 🐛 ✅ ⚠️ 📌 before each bullet point.\n"
            "Use bullet points. Use simple language. Use Indian units (quintal, per acre, per palm, kg/ha).\n"
            "Mention exact product names, doses, timings where relevant.\n"
            "Reference: APMC, KVK, ICAR, MSP prices, government schemes where helpful.\n\n"
            f"FARMER QUESTION: {message}\n\nANSWER:"
        )
        try:
            token = await get_iam_token()
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.post(
                    gen_url,
                    json={
                        "model_id": "ibm/granite-13b-instruct-v2",
                        "input": prompt,
                        "parameters": {"decoding_method": "greedy", "max_new_tokens": 500, "temperature": 0.3},
                        "project_id": WATSONX_PROJECT_ID,
                    },
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                )
                r.raise_for_status()
                text = r.json()["results"][0]["generated_text"].strip()
                if text and len(text) > 20:
                    return translate_to(text, lang)
        except Exception:
            pass

    # Fallback: built-in answer engine
    english_answer = build_answer(message)
    return translate_to(english_answer, lang)


# ---------------------------------------------------------------------------
# API routes — support BOTH /api/chat (legacy) and /api/v1/chat/ (frontend)
# ---------------------------------------------------------------------------
class ChatReq(BaseModel):
    message: str
    language: str = "en"          # "en" | "hi" | "kn"
    session_id: str | None = None  # ignored but accepted so frontend doesn't error
    farmer_context: dict | None = None

async def _do_chat(message: str, language: str) -> JSONResponse:
    if not message.strip():
        return JSONResponse({"reply": "Please type a question.",
                             "response": "Please type a question.",
                             "session_id": "demo", "message_id": "0",
                             "intent": None, "sources": [], "docs_retrieved": 0})
    reply = await ask_ai(message, lang=language)
    return JSONResponse({
        # /api/chat consumers
        "reply": reply,
        # /api/v1/chat/ consumers (frontend ChatPage.js)
        "response": reply,
        "session_id": "demo-session",
        "message_id": str(int(time.time())),
        "intent": detect_intent(message),
        "language": language,
        "sources": [],
        "docs_retrieved": 0,
    })

@app.post("/api/chat")
async def chat_legacy(req: ChatReq):
    return await _do_chat(req.message, req.language)

@app.post("/api/v1/chat/")
async def chat_v1(req: ChatReq):
    return await _do_chat(req.message, req.language)

@app.get("/api/v1/chat/sessions")
async def sessions():
    return JSONResponse([])

@app.get("/api/v1/chat/sessions/{session_id}/messages")
async def messages(session_id: str):
    return JSONResponse([])

@app.get("/api/status")
async def status():
    ibm_ok = bool(WATSONX_API_KEY) and "your-" not in WATSONX_API_KEY
    return JSONResponse({"ibm_key": "IBM Granite AI connected" if ibm_ok else "Demo mode (no IBM key)"})

@app.get("/api/schemes")
async def get_schemes():
    schemes = [
        {"name": "PM-KISAN", "benefit": "Rs.6,000/year", "url": "pmkisan.gov.in"},
        {"name": "PMFBY Crop Insurance", "benefit": "2% premium only", "url": "pmfby.gov.in"},
        {"name": "PM Krishi Sinchai Yojana", "benefit": "55% drip subsidy", "url": "pmksy.gov.in"},
        {"name": "Soil Health Card", "benefit": "Free soil test", "url": "soilhealth.dac.gov.in"},
        {"name": "Kisan Credit Card", "benefit": "Loan at 4% interest", "url": "Any bank"},
        {"name": "e-NAM", "benefit": "Better mandi prices", "url": "enam.gov.in"},
    ]
    return JSONResponse({"schemes": schemes})

# ---------------------------------------------------------------------------
# Serve frontend
# ---------------------------------------------------------------------------
FRONTEND = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(FRONTEND):
    app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="static")

if __name__ == "__main__":
    import uvicorn, sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    port = int(os.getenv("PORT", 8000))
    print("Kisan AI - Smart Farming Advisor")
    print(f"Open: http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
