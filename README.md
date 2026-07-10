# 🌿 Smart Farming Advisor
> **AI-Powered RAG Agricultural Advisory Platform for Small-Scale Farmers**
> Built with IBM Granite LLM · FastAPI · React · ChromaDB · PostgreSQL

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Quick Start](#quick-start)
6. [IBM Cloud API Key Setup](#ibm-cloud-api-key-setup)
7. [RAG Pipeline](#rag-pipeline)
8. [API Reference](#api-reference)
9. [Deployment](#deployment)
10. [Testing](#testing)
11. [Future Enhancements](#future-enhancements)

---

## 🌾 Overview

Smart Farming Advisor bridges the knowledge gap for small-scale farmers by providing:
- **Real-time AI answers** powered by IBM Granite via WatsonX AI
- **Retrieval-Augmented Generation (RAG)** over trusted agricultural knowledge bases
- **Weather intelligence** with farming advisories
- **Live mandi market prices** from AgMarkNet / data.gov.in
- **Multilingual support** (English, Hindi, Kannada, Tamil, Telugu)
- **Voice input & text-to-speech** responses

---

## ✨ Features

| Feature               | Description |
|-----------------------|-------------|
| 🤖 AI Chat            | Natural language Q&A with IBM Granite + RAG citations |
| 🌤️ Weather            | 7-day forecast with farming advisory |
| 🌾 Crop Recommendation| Season, soil, and climate-aware crop selection |
| 🪱 Soil Analysis      | NPK, pH analysis with improvement suggestions |
| 🐛 Pest & Disease     | Symptom-based diagnosis + image upload |
| 🧪 Fertilizer Advisor | Stage-wise fertilizer schedule |
| 💧 Irrigation         | Smart irrigation calendar |
| 📊 Market Prices      | Live mandi prices with trend charts |
| 🌐 Multilingual       | 5 Indian language support |
| 🎤 Voice              | Mic input + text-to-speech output |

---

## 🛠️ Tech Stack

| Layer        | Technology |
|--------------|------------|
| **LLM**      | IBM Granite 13B via WatsonX AI |
| **RAG**      | LangChain + ChromaDB + Sentence Transformers |
| **Backend**  | Python 3.11, FastAPI, SQLAlchemy (async) |
| **Database** | PostgreSQL 16 |
| **Frontend** | React 18, Recharts, React Router v6 |
| **Auth**     | JWT (python-jose, passlib bcrypt) |
| **Speech**   | Google STT, gTTS |
| **Deploy**   | Docker, Docker Compose, IBM Cloud |

---

## 📁 Project Structure

```
smart-farming-advisor/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + lifespan
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic settings (reads .env)
│   │   │   ├── database.py      # SQLAlchemy async setup
│   │   │   └── security.py      # JWT + password hashing
│   │   ├── api/routes/
│   │   │   ├── auth.py          # Register / Login
│   │   │   ├── chat.py          # Main RAG chat endpoint
│   │   │   ├── weather.py       # OpenWeatherMap integration
│   │   │   ├── crops.py         # Crop recommendation
│   │   │   ├── soil.py          # Soil analysis
│   │   │   ├── pests.py         # Pest & disease diagnosis
│   │   │   ├── fertilizer.py    # Fertilizer advisory
│   │   │   ├── irrigation.py    # Irrigation scheduling
│   │   │   ├── market.py        # Mandi price data
│   │   │   ├── profile.py       # Farmer profile
│   │   │   └── speech.py        # STT / TTS
│   │   ├── models/
│   │   │   ├── user.py          # SQLAlchemy User model
│   │   │   ├── farmer_profile.py# Farmer profile model
│   │   │   └── chat_history.py  # Chat session + messages
│   │   ├── rag/
│   │   │   ├── vector_store.py  # ChromaDB + embeddings
│   │   │   ├── rag_pipeline.py  # Full RAG orchestration
│   │   │   ├── document_loader.py# PDF/DOCX/TXT ingestion
│   │   │   └── seed_knowledge.py # Knowledge base seeder
│   │   ├── services/
│   │   │   ├── llm_service.py   # IBM Granite wrapper
│   │   │   ├── weather_service.py# OpenWeatherMap
│   │   │   ├── market_service.py # AgMarkNet
│   │   │   └── speech_service.py # gTTS + SpeechRecognition
│   │   ├── prompts/
│   │   │   └── templates.py     # Granite prompt templates
│   │   └── utils/
│   │       ├── intent_detector.py # Query intent classification
│   │       └── language_utils.py  # Language detection + translation
│   ├── data/
│   │   ├── documents/           # Put your PDF/DOCX docs here
│   │   └── chroma_db/           # ChromaDB persisted data
│   ├── tests/test_core.py
│   ├── migrations/              # Alembic migrations
│   ├── .env                     # !! Never commit !!
│   ├── .env.example             # Template
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.py
│
├── frontend/
│   ├── src/
│   │   ├── App.js               # Router + providers
│   │   ├── index.css            # Global CSS variables
│   │   ├── services/api.js      # Axios client + service helpers
│   │   ├── context/
│   │   │   ├── AuthContext.js   # Auth state (JWT)
│   │   │   └── FarmerContext.js # Profile + language + dark mode
│   │   ├── components/
│   │   │   ├── Sidebar.js/css   # Collapsible navigation
│   │   │   ├── TopBar.js/css    # Header with lang/dark toggle
│   │   │   └── AppLayout.js     # Protected shell
│   │   └── pages/
│   │       ├── LoginPage.js     # Auth — sign in
│   │       ├── RegisterPage.js  # Auth — sign up
│   │       ├── Dashboard.js     # Home overview
│   │       ├── ChatPage.js      # Full chat UI
│   │       ├── WeatherPage.js   # Weather + charts
│   │       ├── CropsPage.js     # Crop recommendation
│   │       ├── SoilPage.js      # Soil analysis
│   │       ├── PestPage.js      # Pest diagnosis + image
│   │       ├── FertilizerPage.js# Fertilizer advisor
│   │       ├── IrrigationPage.js# Irrigation scheduler
│   │       ├── MarketPage.js    # Market prices
│   │       ├── ProfilePage.js   # Farmer profile
│   │       └── SettingsPage.js  # Language, dark mode
│   ├── public/index.html
│   ├── .env                     # !! Never commit !!
│   ├── .env.example
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
│
└── deployment/
    └── docker-compose.yml
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 16
- Docker (optional, for full stack)

### 1. Clone & Configure

```bash
git clone <your-repo>
cd smart-farming-advisor

# Backend secrets
cp backend/.env.example backend/.env
# Edit backend/.env and fill in your API keys (see below)

# Frontend env
cp frontend/.env.example frontend/.env
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt

# Initialize database
python -c "import asyncio; from app.core.database import init_db; asyncio.run(init_db())"

# Seed knowledge base (ChromaDB)
python -m app.rag.seed_knowledge

# Add your own documents (optional)
# Copy PDF/DOCX files to backend/data/documents/
# python -c "from app.rag.document_loader import ingest_directory; ingest_directory()"

# Run backend
python run.py
```
Backend will start at **http://localhost:8000**
Swagger docs at **http://localhost:8000/api/docs**

### 3. Frontend Setup

```bash
cd frontend
npm install
npm start
```
Frontend at **http://localhost:3000**

---

## 🔐 IBM Cloud API Key Setup

> **Security Note:** API keys are stored in `backend/.env` only. This file is gitignored and never bundled into the frontend build.

### Step 1: Create IBM Cloud Account
1. Go to [https://cloud.ibm.com](https://cloud.ibm.com)
2. Create a free account

### Step 2: Get WatsonX API Key
1. Log in → top right menu → **Manage → Access (IAM)**
2. Left panel → **API keys → Create an IBM Cloud API key**
3. Copy the key (shown only once!)
4. Paste into `backend/.env`:
   ```env
   WATSONX_API_KEY=your_actual_key_here
   ```

### Step 3: Get WatsonX Project ID
1. Go to [https://dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com)
2. Create a project (or use existing)
3. Go to project **Settings → General**
4. Copy the **Project ID**
5. Paste into `backend/.env`:
   ```env
   WATSONX_PROJECT_ID=your_project_id_here
   ```

### Step 4: Weather API Key (OpenWeatherMap)
1. Go to [https://openweathermap.org/api](https://openweathermap.org/api)
2. Sign up for the **free tier**
3. Copy your API key to `backend/.env`:
   ```env
   WEATHER_API_KEY=your_weather_key_here
   ```

### Step 5: Market Price API (data.gov.in)
1. Go to [https://data.gov.in](https://data.gov.in)
2. Register and get API key
3. Add to `backend/.env`:
   ```env
   AGMARKNET_API_KEY=your_agmarknet_key_here
   ```

### Restart Backend
```bash
# The config.py reads .env via pydantic-settings on startup
python run.py
```

---

## 🔗 RAG Pipeline

```
User Query
    ↓
Language Detection (Unicode range detection)
    ↓
Translation to English (googletrans)
    ↓
Intent Classification (keyword-based)
    ↓
Semantic Search (ChromaDB + MiniLM embeddings)
    ↓
Context Assembly (top-K relevant chunks)
    ↓
Prompt Engineering (intent-aware Granite prompt)
    ↓
IBM Granite LLM Generation (WatsonX AI)
    ↓
Back-translation to user's language
    ↓
Response + Source Citations
```

### Adding Custom Documents to RAG

Drop any PDF, DOCX, or TXT file into `backend/data/documents/` and run:

```bash
cd backend
python -c "from app.rag.document_loader import ingest_directory; ingest_directory()"
```

Name the file with a keyword for auto-categorization:
- `crop_guide.pdf` → category: `crop_recommendation`
- `pest_manual.docx` → category: `pest_management`
- `fertilizer_guide.txt` → category: `fertilizer`

---

## 📡 API Reference

Base URL: `http://localhost:8000/api/v1`
Interactive docs: `http://localhost:8000/api/docs`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Create farmer account |
| `/auth/login` | POST | Login, returns JWT |
| `/chat/` | POST | Send AI chat message (RAG) |
| `/chat/sessions` | GET | List chat sessions |
| `/weather/current` | GET | Current weather |
| `/weather/forecast` | GET | 7-day forecast |
| `/weather/advisory` | GET | Farming advisory |
| `/crops/recommend` | POST | Crop recommendation |
| `/soil/analyze` | POST | Soil analysis |
| `/pests/diagnose` | POST | Pest diagnosis |
| `/pests/diagnose-image` | POST | Image-based diagnosis |
| `/fertilizer/recommend` | POST | Fertilizer plan |
| `/irrigation/schedule` | POST | Irrigation schedule |
| `/market/prices` | GET | Mandi prices |
| `/profile/` | GET/PUT | Farmer profile |
| `/speech/tts` | POST | Text → speech |
| `/speech/stt` | POST | Speech → text |

---

## 🚢 Deployment (Docker)

```bash
cd deployment

# Create a .env file with your secrets
# Copy all keys from backend/.env

docker-compose up --build -d

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

### IBM Cloud Deployment

1. Install IBM Cloud CLI: `ibmcloud login`
2. Push to IBM Code Engine:
   ```bash
   ibmcloud ce project create --name farming-advisor
   ibmcloud ce app create --name farming-backend --image us.icr.io/your-ns/farming-backend
   ibmcloud ce app create --name farming-frontend --image us.icr.io/your-ns/farming-frontend
   ```

---

## 🧪 Testing

```bash
cd backend

# Install test deps
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_core.py::test_intent_detection -v
```

---

## 🔮 Future Enhancements

- [ ] **Plant Disease Vision Model** — integrate CLIP/ResNet for crop image analysis
- [ ] **Offline PWA Mode** — service worker caching for field use without internet
- [ ] **Push Notifications** — weather alerts and pest outbreak warnings
- [ ] **PDF Report Generation** — downloadable farm advisory reports
- [ ] **SMS/WhatsApp Bot** — Twilio integration for feature-phone farmers
- [ ] **IoT Sensor Integration** — soil moisture, temperature sensors via MQTT
- [ ] **Geo-clustering** — hyper-local advice using satellite imagery APIs
- [ ] **Federated Learning** — privacy-preserving model fine-tuning from farmer data

---

## 👨‍🌾 License

MIT License — Free for educational and farming community use.

---

*Made with ❤️ for Indian farmers · Powered by IBM Granite AI*
