# 🏛️ Hyderabad Navigator — Intelligent Trip Planning Chatbot

AI-powered multilingual trip planning chatbot for Hyderabad using NLP + Random Forest.
Supports **English**, **Hindi (हिंदी)**, and **Telugu (తెలుగు)** with voice assistant.

---

## 🚀 Quick Start

python -m venv venv
venv/scripts/activate

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Add API Keys (optional but recommended)
Edit `config/config.py`py or set environment variables:
```bash
export OPENWEATHER_API_KEY=your_key_here
export GOOGLE_MAPS_API_KEY=your_key_here
```

### 3. Train Model + Start Server
```bash
python run.py
```
This auto-trains the model on first run, then starts the Flask API.

### 4. Open Frontend
Open `frontend/index.html` in your browser.
Or visit `http://localhost:5000` after starting the server.

---

## 📁 Project Structure

```
hyderabad-navigator/
├── run.py                     ← Main entry point (train + serve)
├── requirements.txt
├── backend/
│   ├── app.py                 ← Flask REST API
│   ├── chatbot.py             ← Core chatbot logic
│   ├── nlp_utils.py           ← Language detection, NLP tools
│   └── voice_handler.py       ← STT + TTS (gTTS + SpeechRecognition)
├── model/
│   ├── train_model.py         ← Train Random Forest classifier
│   ├── test_model.py          ← Evaluate + interactive test
│   ├── dataset.json           ← Multilingual training data (EN/HI/TE)
│   ├── rf_model.pkl           ← Saved model (after training)
│   ├── tfidf_vectorizer.pkl   ← Saved vectorizer
│   └── label_encoder.pkl      ← Saved label encoder
├── frontend/
│   └── index.html             ← Full UI (chat + voice + weather + map)
└── config/
    └── config.py              ← API keys and settings
```

---

## 🤖 AI/ML Stack

| Component | Technology |
|-----------|-----------|
| Intent Classification | Random Forest (sklearn) |
| Feature Extraction | TF-IDF with char n-grams (2-4) |
| Language Detection | Unicode range detection |
| Entity Extraction | Regex + keyword matching |
| Text-to-Speech | gTTS (Google TTS) |
| Speech-to-Text | SpeechRecognition + Google API |

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send text message |
| POST | `/api/voice` | Send voice (base64 WAV) |
| GET | `/api/weather` | Hyderabad weather |
| GET | `/api/places?category=sightseeing` | Places list |
| GET | `/api/itinerary?days=3` | Day-wise trip plan |
| GET | `/api/languages` | Supported languages |

### Chat Request Example
```json
POST /api/chat
{
  "message": "Best places to visit in Hyderabad",
  "language": "en",
  "tts": true
}
```

---

## 🔑 API Keys Required

| Key | Where to Get | Used For |
|-----|-------------|----------|
| OPENWEATHER_API_KEY | openweathermap.org | Live weather |
| GOOGLE_MAPS_API_KEY | console.cloud.google.com | Maps |
| GOOGLE_PLACES_API_KEY | console.cloud.google.com | Places |
| ANTHROPIC_API_KEY | console.anthropic.com | AI fallback |

---

## 🧪 Training & Testing

```bash
# Train model separately
python model/train_model.py

# Test model with sample queries
python model/test_model.py
```

---

## 💬 Supported Intents

- `greeting` / `farewell`
- `sightseeing` — Places, monuments, attractions
- `food_recommendation` — Restaurants, biryani, local food
- `hotel_booking` — Hotels, accommodation
- `transport` — Metro, buses, cabs
- `weather_query` — Climate, temperature
- `budget_query` — Cost, price estimates
- `itinerary` — Day-wise trip plans
- `local_tips` — Travel advice, dos & don'ts
- `emergency_info` — Police, ambulance, hospitals
- `shopping` — Markets, pearls, bangles

---

## 🎙️ Voice Feature

The frontend has a 🎤 microphone button. Click to start recording, click again to stop.
Audio is sent to `/api/voice` which:
1. Converts speech to text (SpeechRecognition)
2. Processes intent (Random Forest)
3. Returns response + TTS audio (gTTS)

---

Built with ❤️ for Hyderabad 🏛️
