"""
Knowledge Base Seeder — Populates ChromaDB with Indian Agricultural Knowledge
Covers: Arecanut, Coconut, Paddy, Sugarcane, Banana, Maize, Coffee, Pepper,
        Turmeric, Ginger, Onion, Chilli + standard crops and soil/pest/fertilizer data.

Usage:
    cd backend
    python -m app.rag.seed_knowledge
"""
from loguru import logger
from app.rag.vector_store import add_documents


FARMING_KNOWLEDGE = [

    # ══════════════════════════════════════════════════════════════
    #  REGIONAL CROPS — SOUTH INDIA (Karnataka, Kerala, Tamil Nadu)
    # ══════════════════════════════════════════════════════════════

    # ── Arecanut (Supari) ────────────────────────────────────────
    {
        "id": "crop_arecanut_001",
        "content": "Arecanut (Areca catechu) is a major plantation crop of Karnataka, Kerala, and Assam. Climate: 14–36°C, 750–4500mm rainfall, humidity 70–80%. Soil: Well-drained laterite, red loam, pH 5.5–7.0. Planting: June–September, pit size 90x90x90cm, spacing 2.7x2.7m. Yield: 1.5–3 kg dry nuts/palm/year (starts bearing at 5–7 years). Key variety: Mangala, Sumangala, Shreemangala (Karnataka), Mohitnagar (Assam). Harvesting: Bunches harvested every 40–45 days. Important districts: Shivamogga, Dakshina Kannada, Udupi, Uttara Kannada.",
        "category": "crop_recommendation",
        "source": "ICAR_Arecanut_Guide",
    },
    {
        "id": "crop_arecanut_002",
        "content": "Arecanut fertilizer requirement: Young palms (1–5 years): Urea 50g + SSP 75g + MOP 50g per palm every 6 months. Bearing palms (>5 years): Urea 200g + SSP 130g + MOP 130g + FYM 12kg per palm per year. Apply in 2 splits (June and September). Micronutrient: Borax 25g/palm in June. Irrigation: Summer irrigation critical — drip irrigation highly recommended. Apply 15–20 liters/palm/day in summer. Green manuring with Dhaincha improves soil health significantly.",
        "category": "fertilizer",
        "source": "ICAR_Arecanut_Guide",
    },
    {
        "id": "pest_arecanut_001",
        "content": "Major Arecanut Pests and Diseases: (1) Koleroga (Mahali/Fruit Rot) caused by Phytophthora palmivora — most destructive. Symptoms: Premature fruit drop, dark brown rotting of bunches. Management: Remove infected bunches, apply Bordeaux mixture 1% spray in June–July, drench trunk with Metalaxyl + Mancozeb 3g/L. (2) Yellow Leaf Disease — suspected mycoplasma. Symptoms: Yellowing and drooping of lower leaves. No cure; remove affected palms. (3) Inflorescence die-back: Apply Hexaconazole 2ml/L. (4) White grub: Apply Phorate 5g/palm in soil.",
        "category": "pest_management",
        "source": "ICAR_Arecanut_Guide",
    },

    # ── Coconut ──────────────────────────────────────────────────
    {
        "id": "crop_coconut_001",
        "content": "Coconut (Cocos nucifera) is grown across coastal Karnataka, Kerala, Tamil Nadu, Goa, and Andhra Pradesh. Climate: 25–32°C, 1500–2500mm rainfall, coastal humid conditions. Soil: Sandy loam, laterite, alluvial — well-drained. Spacing: 7.5x7.5m (triangular). Bearing starts at 5–7 years. Annual yield: 80–120 nuts/palm (tall varieties), 150–200 nuts/palm (hybrid). Key varieties: Tiptur Tall, Lakshadweep Ordinary, D×T Hybrids (VHC1, Kerasree). Intercropping: Banana, pineapple, turmeric, ginger, vegetables in early years. Market: Coconut, copra, neera (toddy), coir.",
        "category": "crop_recommendation",
        "source": "ICAR_Coconut_Guide",
    },
    {
        "id": "crop_coconut_002",
        "content": "Coconut fertilizer requirement per palm per year: Urea 1.3kg + SSP 2.0kg + MOP 2.0kg + FYM 50kg. Apply in 2 doses: June and December. Apply in circular trench (2m radius). Micronutrients: Borax 50g, Ferrous sulfate 25g for palms showing deficiency. Irrigation: Critical during summer — drip irrigation gives best results. Apply 200 liters/palm/week during dry season. Basin irrigation: 40 liters every 4 days. Mulching with coir pith or dry leaves reduces water loss significantly.",
        "category": "fertilizer",
        "source": "ICAR_Coconut_Guide",
    },
    {
        "id": "pest_coconut_001",
        "content": "Major Coconut Pests and Diseases: (1) Rhinoceros Beetle (Oryctes rhinoceros) — attacks growing tip. Management: Remove rotting logs/manure heaps (breeding sites), plug crown with naphthalene balls, biological control with Metarhizium anisopliae. (2) Red Palm Weevil — most serious pest. Adults bore into trunk. Management: Inject Monocrotophos 10ml/L or Chlorpyrifos in holes, pheromone traps (4/hectare), trunk injection. (3) Bud Rot (Phytophthora) — remove rotting portion, apply Bordeaux mixture. (4) Stem Bleeding: Scrape affected area, apply Bordeaux paste. (5) Eriophyid Mite: Spray Wettable Sulfur 3g/L.",
        "category": "pest_management",
        "source": "ICAR_Coconut_Guide",
    },

    # ── Banana ───────────────────────────────────────────────────
    {
        "id": "crop_banana_001",
        "content": "Banana is grown across Karnataka, Maharashtra, Tamil Nadu, Andhra Pradesh, and Gujarat. Major varieties: Robusta (G9 clone — commercial), Nendran (Kerala), Rasthali, Poovan (south India), Grand Naine (export). Climate: 15–35°C, rainfall 1500–2000mm or irrigation needed. Soil: Rich loamy, well-drained, pH 6.0–7.5. Planting density: 1.8x1.8m (3000 plants/acre) for tissue culture. Yield: 25–35kg/bunch. Crop duration: 11–14 months. High value crop — popular for contract farming. Needs staking after flowering to prevent wind lodging.",
        "category": "crop_recommendation",
        "source": "ICAR_Banana_Guide",
    },
    {
        "id": "crop_banana_002",
        "content": "Banana fertilizer requirement per plant (tissue culture G9/Robusta): Total: Urea 250g + DAP 100g + MOP 300g + FYM 10kg. Schedule: At planting: full DAP + 25% N + 25% K. 45 days: 25% N + 25% K. 90 days: 25% N + 25% K. At shooting: 25% N + 50% K. Micronutrients: Zinc sulfate 0.5% + Boron 0.2% foliar spray at 2 and 4 months. Drip fertigation gives best yield — dissolve in irrigation water. Water requirement: 8–10 mm/day. Critical irrigation stages: bunch development and shooting.",
        "category": "fertilizer",
        "source": "ICAR_Banana_Guide",
    },
    {
        "id": "pest_banana_001",
        "content": "Major Banana Pests and Diseases: (1) Panama Wilt (Fusarium oxysporum) — most destructive. Symptoms: Yellowing, splitting of pseudostem. Management: Use wilt-resistant varieties (Rasthali, Nendran), avoid replanting in infected soil, use TC plants, Trichoderma viride soil application. (2) Banana Bunchy Top Virus (BBTV) — curling, streaking of leaves. Remove and burn infected plants. Control aphid vector. (3) Sigatoka Leaf Spot: Remove lower leaves, apply Propiconazole 0.1% or Mancozeb 2.5g/L. (4) Stem Weevil: Trapping with pseudostem pieces + Chlorpyrifos. (5) Nematodes (RKN): Apply Carbofuran 3G in planting pit.",
        "category": "pest_management",
        "source": "ICAR_Banana_Guide",
    },

    # ── Coffee ───────────────────────────────────────────────────
    {
        "id": "crop_coffee_001",
        "content": "Coffee (Arabica and Robusta) is primarily grown in Kodagu, Chikkamagaluru, Hassan districts of Karnataka and Wayanad (Kerala). Arabica: 15–24°C, 1500–2500mm rainfall, altitude 900–1800m. Robusta: 22–28°C, 2000–3000mm rainfall, altitude 300–900m. Soil: Deep rich loamy, laterite, well-drained, pH 5.5–6.5. Shade tree management critical — Silver Oak, Dadap (Erythrina) are common shade trees. Planting distance: 2.7x2.7m (Arabica), 3x3m (Robusta). Yield: 400–700 kg cherry/ha. Certification: USDA Organic and Rainforest Alliance certification for premium market access.",
        "category": "crop_recommendation",
        "source": "Coffee_Board_India",
    },
    {
        "id": "pest_coffee_001",
        "content": "Major Coffee Pests and Diseases: (1) White Stem Borer (Xylotrechus quadripes) — most serious Arabica pest. Management: Swab trunk with Carbaryl 50% WP paste, shade regulation, removal of infested wood. (2) Coffee Berry Borer (CBB): Place bait/trap plants, spray Endosulfan 35 EC (restricted use), use SBB trap. (3) Coffee Leaf Rust (Hemileia vastatrix) — orange powdery spots on underleaf. Spray Hexaconazole 1ml/L or Copper oxychloride 3g/L before monsoon. (4) Black Rot (Koleroga): Copper-based fungicides during monsoon. (5) Mealy Bug: Release Cryptolaemus beetles (biocontrol), spray NEEM oil 3ml/L.",
        "category": "pest_management",
        "source": "Coffee_Board_India",
    },

    # ── Black Pepper ─────────────────────────────────────────────
    {
        "id": "crop_pepper_001",
        "content": "Black Pepper (Piper nigrum) — 'King of Spices' — grown in Kerala, Karnataka (Kodagu, Sirsi), Goa. Climate: 10–40°C, 1250–3000mm rainfall, shade required. Soil: Laterite, loam, well-drained, pH 5.5–6.5. Support: Requires live support (Erythrina, Silver Oak) or concrete/bamboo poles. Spacing: 2.5x2.5m or 3x3m. Varieties: Panniyur-1, Pournami, Sreekara, Subhakara. Yield: 2–3 kg dry pepper/vine/year. Harvesting: Spike harvest when first berry turns red (Nov–Feb). Organic pepper fetches 2–3x premium price.",
        "category": "crop_recommendation",
        "source": "Spices_Board_India",
    },
    {
        "id": "pest_pepper_001",
        "content": "Major Pepper Diseases and Pests: (1) Phytophthora Foot Rot — most devastating disease. Symptoms: Quick wilting, collar region blackening, sudden vine death. Management: Remove infected plants, drench soil with Metalaxyl 1g/L, spray foliage with Bordeaux mixture 1%. Do not over-irrigate. Plant on raised beds. (2) Pollu Beetle (Longitarsus nigripennis): Spray Dimethoate 30 EC 2ml/L. (3) Stunt Disease (virus): Remove infected vines, control thrips vector. (4) Anthracnose: Copper oxychloride 3g/L spray. (5) Nematodes: Apply Carbofuran in root zone.",
        "category": "pest_management",
        "source": "Spices_Board_India",
    },

    # ── Turmeric ─────────────────────────────────────────────────
    {
        "id": "crop_turmeric_001",
        "content": "Turmeric (Curcuma longa) is a major spice/medicinal crop grown in Andhra Pradesh, Telangana, Tamil Nadu, Karnataka, Maharashtra, and Odisha. Climate: 20–30°C, 1500–2000mm rainfall, partial shade beneficial. Soil: Sandy loam, clay loam, well-drained, pH 5.5–7.0. Planting: April–May (Kharif), 45x30cm spacing, rhizome pieces (50–60g). Varieties: Alleppey, Rajapuri, Erode Local, Nizamabad Bulb, Megha Turmeric (high curcumin). Yield: 20–25 tonnes/ha fresh rhizomes. Harvesting: 8–9 months after planting (Dec–Feb). Yield of dried powder: 20–25% of fresh weight. Market: High demand for Erode (TN) and Nizamabad (TS) variety.",
        "category": "crop_recommendation",
        "source": "Spices_Board_India",
    },
    {
        "id": "fert_turmeric_001",
        "content": "Turmeric fertilizer: NPK 150:50:100 kg/ha. FYM 30 t/ha as basal. Split application: At planting: 50% N + full P + 50% K. At 60 days: 25% N + 25% K. At 120 days: 25% N + 25% K. Micronutrient: ZnSO4 25kg/ha + Borax 10kg/ha. Apply earthing up at 60 and 120 days. Mulch with green leaves (3–4 t/ha) after planting to retain moisture. Neem cake 250kg/ha in soil reduces nematode damage. Annual rainfall of 1500mm or 4–5 irrigations in dry areas sufficient.",
        "category": "fertilizer",
        "source": "Spices_Board_India",
    },
    {
        "id": "pest_turmeric_001",
        "content": "Major Turmeric Pests and Diseases: (1) Rhizome Rot (Pythium aphanidermatum) — most serious. Yellow wilting, rotting collar. Management: Use healthy rhizomes, treat seed rhizomes with Metalaxyl 1g/L or Trichoderma viride 4g/L before planting, avoid waterlogging, apply Bordeaux mixture 1% at 30 and 60 days. (2) Leaf Blotch (Taphrina): Mancozeb 2.5g/L spray. (3) Rhizome scale (Aspidiella hartii): Apply Dimethoate 30 EC 2ml/L. (4) Shoot Borer (Conogethes punctiferalis): Apply Malathion 50 EC 1ml/L in leaf whorl. (5) Nematodes: Apply Carbofuran 3G at planting.",
        "category": "pest_management",
        "source": "Spices_Board_India",
    },

    # ── Ginger ───────────────────────────────────────────────────
    {
        "id": "crop_ginger_001",
        "content": "Ginger (Zingiber officinale) is grown in Kerala, Karnataka, Meghalaya, Himachal Pradesh, and Odisha. Climate: 25–35°C, 1250–2500mm rainfall, partial shade. Soil: Sandy loam, clay loam, well-drained, organic rich, pH 5.5–6.5. Planting: April–May, spacing 30x20cm, seed rhizome 20–25g. Varieties: Rio-de-Janeiro, Maran, Nadia, Wynad Local, Himachal. Yield: 15–25 tonnes/ha fresh. Harvesting: 8–10 months. Green ginger: 6 months. Dry ginger: 9–10 months. Seed material requirement: 1500–2000 kg/ha. Ginger is labor-intensive but high-value — commonly grown in garden land intercropped with coconut.",
        "category": "crop_recommendation",
        "source": "Spices_Board_India",
    },
    {
        "id": "pest_ginger_001",
        "content": "Major Ginger Diseases: (1) Rhizome Rot / Soft Rot (Pythium spp.) — most common. Yellowing, rotting at collar region. Management: Use disease-free rhizomes, treat seeds with Metalaxyl 2g/L for 30 min, good drainage, apply Bordeaux mixture 1% to soil at planting and 30/60 days after. (2) Bacterial Wilt (Ralstonia solanacearum): Wilting with ooze from cut stem. Remove infected clumps, pour 0.2% bleaching powder. (3) Leaf Spot (Phyllosticta): Mancozeb 2.5g/L spray. (4) Shoot Borer (Conogethes punctiferalis): Neem oil 3ml/L or Malathion 1ml/L. (5) Root-knot Nematode: Carbofuran 3G at planting + Neem cake 250kg/ha.",
        "category": "pest_management",
        "source": "Spices_Board_India",
    },

    # ── Onion ────────────────────────────────────────────────────
    {
        "id": "crop_onion_001",
        "content": "Onion (Allium cepa) is a major commercial crop in Maharashtra (Nashik, Pune), Karnataka (Dharwad, Belgaum), Madhya Pradesh, and Gujarat. Varieties: Nasik Red, N53, Agrifound Dark Red (Kharif), Agrifound Light Red (Rabi), Phule Suvarna. Kharif sowing: June–July transplant. Rabi: Oct–Nov sowing, Jan–Feb transplant. Late Kharif: Nov–Dec. Soil: Sandy loam, well-drained, pH 6.0–7.5. Yield: 25–35 t/ha. Onion needs careful post-harvest handling — curing for 7–10 days reduces storage losses. Price is highly volatile — growers' cooperatives help stabilize income.",
        "category": "crop_recommendation",
        "source": "NHRDF_Onion_Guide",
    },
    {
        "id": "fert_onion_001",
        "content": "Onion fertilizer recommendation: NPK 100:50:75 kg/ha. FYM 25 t/ha at land preparation. Split N: 50% at transplanting, 25% at 30 days, 25% at 60 days. Full P and K at transplanting. Sulphur 25kg/ha improves pungency and shelf life. Micronutrients: ZnSO4 10kg/ha, Borax 2kg/ha. Foliar spray: 0.5% ZnSO4 + 0.25% Borax at 30 and 50 days. Tip: Excess nitrogen causes poor keeping quality — avoid urea after bulb formation. Drip fertigation improves yield by 30–40%.",
        "category": "fertilizer",
        "source": "NHRDF_Onion_Guide",
    },
    {
        "id": "pest_onion_001",
        "content": "Major Onion Pests and Diseases: (1) Thrips (Thrips tabaci) — most serious pest. Silver streaks on leaves, stunting. Management: Spray Fipronil 5SC 1ml/L or Spinosad 0.3ml/L. Yellow sticky traps (10/acre). Avoid excess N. (2) Purple Blotch (Alternaria porri): Purple spots on leaves. Spray Mancozeb 2.5g/L or Iprodione 2g/L. (3) Downy Mildew (Peronospora destructor): Humid conditions. Spray Metalaxyl + Mancozeb 2.5g/L. (4) Stemphylium Blight: Tebuconazole 1ml/L. (5) Bulb Rot (Fusarium): Use healthy transplants, soil drench with Carbendazim 1g/L.",
        "category": "pest_management",
        "source": "NHRDF_Onion_Guide",
    },

    # ── Chilli ───────────────────────────────────────────────────
    {
        "id": "crop_chilli_001",
        "content": "Chilli (Capsicum annuum) is a major crop in Andhra Pradesh (Guntur), Telangana, Karnataka, Maharashtra, and Madhya Pradesh. Varieties: LCA 334 (high yield), Byadagi (dry chilli, Karnataka), Teja (AP/TS), G4 (Guntur), Hybrid varieties (Mahico, Seminis). Climate: 20–30°C, well distributed rainfall or irrigation. Soil: Sandy loam to clay loam, pH 5.5–7.0. Transplant at 6–7 weeks. Spacing: 60x45cm or 60x60cm. Yield: 20–30 t/ha green, 3–5 t/ha dry. Harvesting: Green (90–100 days), Red ripe (120–135 days), Dry (150–180 days). Byadagi and Teja varieties command premium in spice market.",
        "category": "crop_recommendation",
        "source": "ICAR_Chilli_Guide",
    },
    {
        "id": "fert_chilli_001",
        "content": "Chilli fertilizer: NPK 100:50:50 kg/ha. FYM 25 t/ha. Basal: Full P + K + 25% N. Top dressing at 30 days: 25% N. At first flowering: 25% N. After first harvest: 25% N. Micronutrients: ZnSO4 25kg/ha in soil. Foliar spray: Boron 0.2% at flowering improves fruit set. Calcium + Boron spray reduces blossom end rot. Drip fertigation with water-soluble fertilizers (19:19:19 NPK, Potassium Nitrate) during flowering and fruiting improves yield significantly.",
        "category": "fertilizer",
        "source": "ICAR_Chilli_Guide",
    },
    {
        "id": "pest_chilli_001",
        "content": "Major Chilli Pests and Diseases: (1) Thrips and Mites — curl leaves, silvery appearance. Spray Abamectin 0.5ml/L or Spinosad 0.3ml/L for thrips; Dicofol 2.5ml/L or Fenpyroximate 1ml/L for mites. (2) Fruit Borer (Helicoverpa): Spray Emamectin benzoate 0.4g/L or Neem oil 3ml/L. Pheromone traps. (3) Anthracnose / Fruit Rot (Colletotrichum): Reddish-brown sunken spots on fruits. Spray Propiconazole 1ml/L or Azoxystrobin 1g/L. (4) Bacterial Wilt: Use resistant varieties, remove infected plants. (5) Leaf Curl Virus (Begomovirus): Destroy infected plants, control whitefly vector with Imidacloprid 0.3ml/L.",
        "category": "pest_management",
        "source": "ICAR_Chilli_Guide",
    },

    # ══════════════════════════════════════════════════════════════
    #  MAJOR FOOD CROPS
    # ══════════════════════════════════════════════════════════════

    # ── Paddy (Rice) ─────────────────────────────────────────────
    {
        "id": "crop_paddy_001",
        "content": "Paddy (Rice) is the staple crop of India — grown in all states. Kharif paddy: June–July sowing, September–November harvest. Rabi paddy (South India): November–December sowing, February–April harvest. Types: Transplanted paddy (wet method), direct seeded, SRI method. Major varieties: BPT-5204 (Samba Masuri), MTU-7029, Jaya, IR-36, Pusa Basmati 1 (North), ADT 36 (TN), Jyothi (Karnataka). SRI method: Saves 30–50% water, uses less seed, higher yield (8–10 t/ha vs 5–6 t/ha normal). Soil: Clay loam, alluvial — water retention important.",
        "category": "crop_recommendation",
        "source": "DRR_Rice_Production_Guide",
    },
    {
        "id": "fert_paddy_001",
        "content": "Paddy (Rice) fertilizer requirement: NPK 120:60:60 kg/ha for Kharif. Rabi: NPK 150:75:75 kg/ha. (1) Basal at transplanting: Full P (SSP 375kg/ha), full K (MOP 100kg/ha), 25% N (Urea 65kg/ha). (2) First top dressing at 21–25 days: 50% N (Urea 131kg/ha). (3) Panicle initiation stage: 25% N (Urea 65kg/ha). For 1 acre: Urea 87kg, SSP 150kg, MOP 40kg approx. Apply ZnSO4 25kg/ha if zinc deficiency (yellowing of leaves with green veins). SRI method: Reduce 25% chemical fertilizer when using FYM 5t/ha.",
        "category": "fertilizer",
        "source": "DRR_Rice_Production_Guide",
    },
    {
        "id": "irrig_paddy_001",
        "content": "Paddy irrigation guide: Transplanted paddy: Maintain 3–5 cm standing water from transplanting to panicle initiation. Allow field to dry (hair-line cracks) once every 10 days for soil aeration (AWD — Alternate Wet and Dry). Drain 2 weeks before harvest. Critical water stages: Tillering (21–40 DAS), Panicle initiation (50–60 DAS), Flowering (75–85 DAS) — no water stress during these. Total water: 1200–2000 mm/crop. AWD method saves 15–30% water without yield loss. SRI: 2–3 cm intermittent irrigation, higher yield with less water.",
        "category": "irrigation",
        "source": "DRR_Rice_Production_Guide",
    },
    {
        "id": "pest_paddy_001",
        "content": "Major Paddy Pests and Diseases: (1) Rice Blast (Pyricularia oryzae) — spindle leaf lesions with grey center. Apply Tricyclazole 0.6g/L or Isoprothiolane 1.5ml/L at 25 and 45 DAT. (2) Brown Plant Hopper (BPH) — hopperburn, plant collapse. Spray Buprofezin 1ml/L or Imidacloprid 0.3ml/L. Avoid hopper-susceptible varieties in endemic areas. (3) Stem Borer — dead heart (vegetative), white ear (reproductive). Spray Fipronil 0.5ml/L or Cartap Hydrochloride 1g/L. Use pheromone traps. (4) Bacterial Leaf Blight: Drain field, spray Copper oxychloride 3g/L or Propiconazole. (5) Sheath Blight: Hexaconazole 2ml/L at 40 DAT.",
        "category": "pest_management",
        "source": "DRR_Rice_Production_Guide",
    },

    # ── Sugarcane ────────────────────────────────────────────────
    {
        "id": "crop_sugarcane_001",
        "content": "Sugarcane is a major commercial crop in Maharashtra (Pune, Solapur, Kolhapur), Karnataka (Belgaum, Mandya), Tamil Nadu (Coimbatore), Uttar Pradesh, and Andhra Pradesh. Climate: 20–35°C, 1500–2500mm rainfall or irrigation. Soil: Loamy, well-drained, pH 6.0–8.0. Major varieties: CO-86032, CO 0238 (UP), M-335 (Maharashtra), COC 671, SNK 566 (TN). Planting: February–March (spring), July–August (adsali/ratoon). Spacing: 90cm rows, 2 bud sett pieces. Duration: 10–12 months. Yield: 80–120 t/ha. Factory-linked farming with FRP (Fair and Remunerative Price) guaranteed by government.",
        "category": "crop_recommendation",
        "source": "ICAR_Sugarcane_Guide",
    },
    {
        "id": "fert_sugarcane_001",
        "content": "Sugarcane fertilizer: NPK 250:115:115 kg/ha (Maharashtra recommendation). FYM 25 t/ha as basal. Application split: At planting: Full P + K + 33% N (Urea 180kg). At 45 days (earthing up): 33% N. At 90 days: 34% N. Trash mulching after first cut conserves moisture and adds organic matter. Micronutrients: ZnSO4 25kg/ha, apply if deficiency. Foliar spray: Potassium Chloride 1% at 3 and 5 months improves juice quality. Trashco (decomposed trash) or press mud compost from sugar factory is excellent organic amendment. Drip fertigation saves 40% water and improves yield by 25–30%.",
        "category": "fertilizer",
        "source": "ICAR_Sugarcane_Guide",
    },
    {
        "id": "pest_sugarcane_001",
        "content": "Major Sugarcane Pests and Diseases: (1) Early Shoot Borer (Chilo infuscatellus) — dead heart in young crop. Spray Chlorpyrifos 20EC 2ml/L; release Trichogramma cards (50,000 eggs/ha). (2) Top Shoot Borer (Scirpophaga excerptalis): Spray Chlorantraniliprole 0.3ml/L. (3) Pyrilla (Leafhopper): Spray Malathion 50EC 1ml/L; biological control with Epiricania melanoleuca. (4) Red Rot (Colletotrichum falcatum): Use disease-free seed, treat setts with Carbendazim 1g/L, remove red-spotted stalks. (5) Wilt (Fusarium sacchari): Rogue out infected clumps, treat with Bavistinol. (6) Grassy Shoot Disease: Use virus-free planting material.",
        "category": "pest_management",
        "source": "ICAR_Sugarcane_Guide",
    },

    # ── Maize ────────────────────────────────────────────────────
    {
        "id": "crop_maize_001",
        "content": "Maize (Zea mays) is grown in Karnataka (Davangere, Haveri), Andhra Pradesh, Telangana, Bihar, and Rajasthan. Kharif: June–July sowing, September–October harvest. Rabi: October–November sowing, February–March harvest. Varieties: Pioneer 30V92, DK C919, Dekalb 9108 (hybrid). Open pollinated: Ganga-11, Ganga Safed-2. Climate: 18–27°C, 600–1000mm rainfall. Soil: Sandy loam to clay loam, pH 6.0–7.5. Spacing: 60x20cm (single row) or 75x20cm. Yield: 6–8 t/ha (hybrid) vs 3–4 t/ha (OPV). Uses: Grain, silage, fodder, sweet corn, baby corn. High demand from poultry and starch industries.",
        "category": "crop_recommendation",
        "source": "ICAR_Maize_Guide",
    },
    {
        "id": "fert_maize_001",
        "content": "Maize fertilizer: NPK 150:75:37.5 kg/ha. FYM 10 t/ha as basal. Application: At sowing: Full P (SSP 469 kg/ha), full K (MOP 62 kg/ha), 33% N (Urea 109kg/ha). At knee-high (V5–V6 stage, 30 days): 50% N (Urea 163kg/ha). At tasselling (VT, 60 days): 17% N (Urea 54kg/ha). Apply Urea in bands close to plants, not broadcast. ZnSO4 25kg/ha if zinc deficiency. For baby corn: Reduce N to 100:50:50, harvest cobs before silking. Fertigation with NPK soluble fertilizers improves yield significantly.",
        "category": "fertilizer",
        "source": "ICAR_Maize_Guide",
    },
    {
        "id": "pest_maize_001",
        "content": "Major Maize Pests: (1) Fall Armyworm (Spodoptera frugiperda) — new invasive pest (since 2018). Ragged leaf feeding in whorl. Management: Monitor regularly from 8 DAS; hand picking egg masses; spray Emamectin benzoate 0.4g/L or Spinetoram 0.5ml/L or Chlorantraniliprole 0.3ml/L into whorl at 15–18 DAS. (2) Stem Borer (Chilo partellus) — dead heart, shot holes. Apply Chlorpyrifos in whorl. (3) Common Rust (Puccinia sorghi): Spray Mancozeb 2.5g/L. (4) Turcicum Blight: Use resistant varieties, spray Propiconazole 1ml/L. (5) Downy Mildew: Apply Metalaxyl + Mancozeb at early stage.",
        "category": "pest_management",
        "source": "ICAR_Maize_Guide",
    },

    # ══════════════════════════════════════════════════════════════
    #  GENERAL CROP MANAGEMENT
    # ══════════════════════════════════════════════════════════════

    {
        "id": "crop_kharif_001",
        "content": "Kharif crops are sown June–July with the onset of monsoon and harvested September–November. Major Kharif crops: Rice/Paddy, Maize, Soybean, Cotton, Groundnut, Jowar, Bajra, Arhar (Pigeon Pea), Tur, Moong. Regional Kharif crops: Banana (replanting), Sugarcane (adsali), Ginger, Turmeric, Chilli (transplanting). These crops require 600–1200mm rainfall and temperatures 25–35°C. Kharif MSP crops: Paddy ₹2183/qt, Maize ₹1962/qt, Soybean ₹4600/qt (2023-24 indicative).",
        "category": "crop_recommendation",
        "source": "ICAR_Crop_Guide",
    },
    {
        "id": "crop_rabi_001",
        "content": "Rabi crops are sown October–December after the monsoon and harvested March–May. Major Rabi crops: Wheat, Barley, Mustard, Gram (Chickpea), Peas, Linseed, Safflower, Onion (Rabi). South India Rabi: Rabi paddy (Tamil Nadu, Andhra Pradesh, Karnataka), Sorghum (jowar), Sunflower. These crops require cool weather 15–20°C during growth and warm dry weather during ripening. MSP: Wheat ₹2275/qt, Gram ₹5440/qt, Mustard ₹5650/qt (2023-24).",
        "category": "crop_recommendation",
        "source": "ICAR_Crop_Guide",
    },
    {
        "id": "crop_soil_laterite_001",
        "content": "Laterite soil (Red soils) are common in coastal Karnataka, Kerala, Goa, and parts of Maharashtra. Suitable crops: Arecanut, Coconut, Cashew, Coffee, Pepper, Turmeric, Ginger, Rubber, Paddy (with irrigation). Soil characteristics: Acidic (pH 4.5–5.5), low N and P, good potassium. Management: Apply agricultural lime 2–3 t/ha to raise pH; regular FYM/green manure application essential; mulching reduces erosion; drip irrigation for plantation crops. Micronutrient deficiency (Zn, B, Mo) common — get soil tested.",
        "category": "crop_recommendation",
        "source": "NBSS_Soil_Database",
    },
    {
        "id": "crop_soil_black_001",
        "content": "Black cotton soil (Vertisols) common in Maharashtra, Karnataka (North), Andhra Pradesh, Telangana. Suitable crops: Cotton, Sorghum, Wheat, Linseed, Chickpea, Sugarcane, Onion. Characteristics: High water retention, prone to waterlogging, sticky when wet, cracking when dry. pH 7.5–8.5. Management: Raised bed planting for drainage; apply gypsum 2–3 t/ha for sodicity; avoid excess irrigation; use broad-based ridges for sugarcane.",
        "category": "crop_recommendation",
        "source": "NBSS_Soil_Database",
    },

    # ══════════════════════════════════════════════════════════════
    #  FERTILIZER REFERENCE
    # ══════════════════════════════════════════════════════════════

    {
        "id": "fert_rice_001",
        "content": "Rice fertilizer reference: NPK 120:60:60 kg/ha standard for Kharif irrigated paddy. For 1 acre: Urea 43kg (as top dress), DAP 33kg (basal), MOP 20kg (basal) — approximation. Use split nitrogen to reduce losses. ICAR tip: Apply ZnSO4 25kg/ha if zinc deficiency observed (khaira disease — white stripes on young leaves).",
        "category": "fertilizer",
        "source": "ICAR_Fertilizer_Manual",
    },
    {
        "id": "fert_wheat_001",
        "content": "Wheat fertilizer: NPK 120:60:40 kg/ha. At sowing: Full P + K + 50% N. At first irrigation (CRI, 21 days): 25% N. At second irrigation: 25% N. ZnSO4 25kg/ha on zinc-deficient soils. Micronutrient spray: 0.5% ZnSO4 + 0.1% Borax for better grain quality.",
        "category": "fertilizer",
        "source": "ICAR_Fertilizer_Manual",
    },
    {
        "id": "fert_general_001",
        "content": "Common fertilizer types: Urea (46% N) — cheapest N source. DAP (18-46-0) — N and P, use at sowing. SSP (0-16-0 + 11% S) — P source with sulfur benefit. MOP/KCl (0-0-60) — K source. NPK 17:17:17 — balanced. NPK 20:20:0 — N and P at sowing. Ammonium Sulphate (21% N + 24% S) — good for S-deficient soils. FYM (farm yard manure) — 0.5% N + organic matter. Micronutrient: ZnSO4 (21% Zn), Borax (11% B), Ferrous Sulfate (19% Fe). PM Kisan Samman Nidhi provides ₹6000/year financial support. Soil Health Cards give free NPK recommendations.",
        "category": "fertilizer",
        "source": "ICAR_Fertilizer_Manual",
    },

    # ══════════════════════════════════════════════════════════════
    #  PEST MANAGEMENT — GENERAL
    # ══════════════════════════════════════════════════════════════

    {
        "id": "pest_aphid_001",
        "content": "Aphids affect almost all crops. Symptoms: Curled yellow leaves, sticky honeydew, sooty mold. Management: (1) Organic: Neem oil 3ml/L + soap 1ml/L. Strong water jet. (2) Chemical: Imidacloprid 0.3ml/L, Thiamethoxam 0.2g/L, Dimethoate 2ml/L. (3) Preventive: Avoid excess N, encourage ladybugs. Yellow sticky traps for monitoring. Safety: Wear PPE kit.",
        "category": "pest_management",
        "source": "NCIPM_Pest_Guide",
    },
    {
        "id": "pest_nematode_001",
        "content": "Root Knot Nematode (Meloidogyne spp.) affects tomato, brinjal, chilli, banana, ginger, turmeric. Symptoms: Galls on roots, stunted growth, yellowing. Management: (1) Soil solarization (May–June): Cover moist soil with transparent polythene for 30–40 days — kills nematodes. (2) Neem cake application 500kg/ha. (3) Carbofuran 3G @ 20kg/ha in planting pits. (4) Biological: Paecilomyces lilacinus 2g/kg soil. (5) Resistant varieties where available. Crop rotation with non-host crops (maize, wheat) helps break nematode cycle.",
        "category": "pest_management",
        "source": "NCIPM_Pest_Guide",
    },

    # ══════════════════════════════════════════════════════════════
    #  IRRIGATION
    # ══════════════════════════════════════════════════════════════

    {
        "id": "irrig_drip_001",
        "content": "Drip irrigation guidelines for plantation and vegetable crops: Install laterals 45–60cm apart. Dripper discharge 2–4 L/hr. Frequency: Every day in summer (high ET), every 2–3 days in winter. Sugarcane drip: 8–10 L/plant/day. Banana drip: 8–10 L/plant/day in summer. Arecanut: 15–20 L/palm/day in summer (March–May). Coconut: 50–200 L/palm/day depending on size and climate. Fertigation efficiency: 30–40% saving vs traditional. PM Krishi Sinchai Yojana subsidy: 45–55% for small and marginal farmers on drip and sprinkler systems.",
        "category": "irrigation",
        "source": "ICAR_Water_Management",
    },

    # ══════════════════════════════════════════════════════════════
    #  SOIL HEALTH
    # ══════════════════════════════════════════════════════════════

    {
        "id": "soil_ph_001",
        "content": "Soil pH management: Optimal pH 6.0–7.0 for most crops. Acidic soil (pH <5.5): Apply agricultural lime (CaCO3) 2–4 t/ha. Laterite soils of coastal Karnataka/Kerala often pH 4.5–5.5 — need 3–4 t/ha lime. Re-test after 3 months. Alkaline soil (pH >7.5): Apply gypsum 2–3 t/ha or elemental sulfur 500kg/ha. Drip irrigation with acidic fertilizers (ammonium sulfate) helps. Green manuring with Dhaincha or Sunhemp improves soil pH. Free Soil Health Cards from government give pH and NPK status.",
        "category": "soil_analysis",
        "source": "NBSS_Soil_Health_Card",
    },
    {
        "id": "soil_organic_001",
        "content": "Soil organic carbon improvement: OC below 0.5% = poor soil. Improvement: (1) FYM 15 t/ha annually. (2) Vermicompost 3–5 t/ha. (3) Green manuring — Dhaincha, Sunhemp, Sesbania. (4) Crop residue incorporation. (5) Neem cake 500kg/ha. (6) Cover crops during fallow. Target: 0.75% OC. Benefits: Improved water holding capacity, better nutrient cycling, more earthworms. Composting paddy straw instead of burning is environmentally beneficial and improves soil health.",
        "category": "soil_analysis",
        "source": "NBSS_Soil_Health_Card",
    },

    # ══════════════════════════════════════════════════════════════
    #  MARKET INTELLIGENCE
    # ══════════════════════════════════════════════════════════════

    {
        "id": "market_arecanut_001",
        "content": "Arecanut market: Major markets: Shimoga, Sirsi, Mangalore (Karnataka); Shivamogga APMC is India's largest arecanut market. Price range: ₹30,000–60,000/quintal depending on variety and grade. Varieties: Rashi (chali), White arecanut fetch premium. Season peak price: March–June. Processing: Ripe arecanut → boiled and dried (koka) or fresh-split chali. Cooperative societies like CAMPCO (Mangalore) offer fair prices. Export to Southeast Asia, China is significant.",
        "category": "market_prices",
        "source": "AGMARKNET_Data",
    },
    {
        "id": "market_coconut_001",
        "content": "Coconut market: Tender coconut: ₹15–40/piece retail. Copra: ₹8,000–12,000/quintal. Coconut oil: ₹150–200/L. Major markets: Pollachi, Coimbatore (TN); Kundapur, Udupi (Karnataka); Thrissur (Kerala). CPCRI minimum support price scheme. Value addition: Virgin coconut oil, desiccated coconut, coconut chips, neera-based products command premium. Coir from husk has good market (₹15,000–20,000/t).",
        "category": "market_prices",
        "source": "AGMARKNET_Data",
    },
    {
        "id": "market_spices_001",
        "content": "Spice market prices (indicative): Turmeric: ₹7,000–20,000/quintal (Erode/Nizamabad market). Black pepper: ₹35,000–60,000/quintal (Kochi, Kozhikode). Ginger (dry): ₹15,000–35,000/quintal. Chilli (Teja dry): ₹8,000–20,000/quintal (Guntur market). Best selling time for spices: 3–6 months after harvest when prices improve. Grade spices properly to fetch premium. Spices Board India (1800-425-2935) helps connect farmers to exporters. E-NAM platform provides online mandi access.",
        "category": "market_prices",
        "source": "Spices_Board_Market",
    },
    {
        "id": "market_paddy_001",
        "content": "Paddy and rice market: MSP for Paddy (Common): ₹2183/qt (2023-24). MSP for Paddy (Grade A): ₹2203/qt. Procurement: FCI and state procurement agencies buy at MSP during Kharif and Rabi marketing season. Paddy milling yield: 67–68% rice from paddy. Basmati rice fetches ₹4,000–8,000/qt premium. Parboiled rice market is strong in South India. Best to sell after processing (home mill) for better income. Avoid distress selling — store properly for 2–3 months if price is low.",
        "category": "market_prices",
        "source": "AGMARKNET_Data",
    },
    {
        "id": "market_vegetables_001",
        "content": "Vegetable market guide: Onion: ₹1,000–4,000/qt (Nashik/Bangalore APMC). Price highly seasonal — buy forward contracts or cooperative selling. Tomato: ₹500–5,000/qt (high volatility). Consider cold storage (₹2–3/kg/month). Chilli (green): ₹2,000–8,000/qt. Potato: ₹800–2,000/qt (Agra/Jalandhar). Sell through APMC mandis to ensure fair price. FPO (Farmer Producer Organizations) help small farmers get better prices through collective selling. E-NAM online platform: enables farmers to sell in any mandi across India.",
        "category": "market_prices",
        "source": "AGMARKNET_Data",
    },
]


def seed_knowledge_base():
    """Populate ChromaDB with curated Indian farming knowledge."""
    docs = [k["content"] for k in FARMING_KNOWLEDGE]
    metadatas = [{"source": k["source"], "category": k["category"], "id": k["id"]} for k in FARMING_KNOWLEDGE]
    ids = [k["id"] for k in FARMING_KNOWLEDGE]

    add_documents(docs, metadatas, ids)
    logger.info(f"✅ Seeded {len(FARMING_KNOWLEDGE)} knowledge base entries into ChromaDB.")


if __name__ == "__main__":
    import asyncio
    from app.rag.vector_store import init_vector_store

    async def main():
        await init_vector_store()
        seed_knowledge_base()

    asyncio.run(main())
