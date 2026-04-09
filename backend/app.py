"""
Hyderabad Navigator - Flask Backend
REST API for chatbot, voice, weather, places
"""

import os
import sys
import json
import base64
import requests

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask_cors import CORS

from config.config import (
    SECRET_KEY, DEBUG, PORT,
    OPENWEATHER_API_KEY, GOOGLE_PLACES_API_KEY,
    GOOGLE_MAPS_API_KEY, HYDERABAD_LAT, HYDERABAD_LON
)
from backend.chatbot import get_chatbot
from backend.voice_handler import text_to_speech_base64, speech_to_text

# ─── App Setup ────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Pre-load chatbot
chatbot = get_chatbot()


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return jsonify({"message": "Hyderabad Navigator API is running!", "version": "1.0.0"})


@app.route("/api/chat", methods=["POST"])
def chat():
    """Process a text message and return chatbot response."""
    data = request.get_json(silent=True) or {}
    text = data.get("message", "").strip()
    lang = data.get("language")          # optional override

    if not text:
        return jsonify({"error": "No message provided"}), 400

    result = chatbot.get_response(text, lang)

    # Optionally generate TTS audio
    if data.get("tts", False):
        audio_b64 = text_to_speech_base64(result["response"], result["language"])
        result["audio_base64"] = audio_b64

    return jsonify(result)


@app.route("/api/voice", methods=["POST"])
def voice():
    """Accept audio (base64 WAV) and return transcription + response."""
    data = request.get_json(silent=True) or {}
    audio_b64 = data.get("audio_base64", "")
    lang      = data.get("language", "en")

    if not audio_b64:
        return jsonify({"error": "No audio provided"}), 400

    try:
        audio_bytes = base64.b64decode(audio_b64)
    except Exception:
        return jsonify({"error": "Invalid base64 audio"}), 400

    transcription = speech_to_text(audio_bytes, lang)
    if not transcription:
        return jsonify({"error": "Could not transcribe audio. Ensure SpeechRecognition is installed."}), 422

    result = chatbot.get_response(transcription, lang)
    result["transcription"] = transcription

    audio_out = text_to_speech_base64(result["response"], result["language"])
    result["audio_base64"] = audio_out

    return jsonify(result)


@app.route("/api/weather", methods=["GET"])
def weather():
    """Return current Hyderabad weather from OpenWeatherMap."""
    if OPENWEATHER_API_KEY == "YOUR_OPENWEATHER_API_KEY":
        # Return mock data if key not set
        return jsonify({
            "city": "Hyderabad",
            "temperature": 32,
            "feels_like": 35,
            "description": "Partly cloudy",
            "humidity": 55,
            "wind_speed": 12,
            "icon": "02d",
            "note": "Mock data - add OPENWEATHER_API_KEY for real data"
        })

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={HYDERABAD_LAT}&lon={HYDERABAD_LON}"
        f"&appid={OPENWEATHER_API_KEY}&units=metric"
    )
    try:
        resp = requests.get(url, timeout=5)
        d = resp.json()
        return jsonify({
            "city":        d["name"],
            "temperature": round(d["main"]["temp"]),
            "feels_like":  round(d["main"]["feels_like"]),
            "description": d["weather"][0]["description"].capitalize(),
            "humidity":    d["main"]["humidity"],
            "wind_speed":  round(d["wind"]["speed"] * 3.6),   # m/s → km/h
            "icon":        d["weather"][0]["icon"],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/places", methods=["GET"])
def places():
    """Return curated Hyderabad places."""
    category = request.args.get("category", "all")

    places_data = {
        "sightseeing": [
            {"name": "Charminar",              "lat": 17.3616, "lng": 78.4747, "rating": 4.4, "type": "Monument"},
            {"name": "Golconda Fort",           "lat": 17.3833, "lng": 78.4011, "rating": 4.4, "type": "Fort"},
            {"name": "Hussain Sagar Lake",      "lat": 17.4239, "lng": 78.4738, "rating": 4.3, "type": "Lake"},
            {"name": "Ramoji Film City",        "lat": 17.2543, "lng": 78.6808, "rating": 4.3, "type": "Theme Park"},
            {"name": "Salar Jung Museum",       "lat": 17.3714, "lng": 78.4804, "rating": 4.4, "type": "Museum"},
            {"name": "Birla Mandir",            "lat": 17.4062, "lng": 78.4691, "rating": 4.6, "type": "Temple"},
            {"name": "Chowmahalla Palace",      "lat": 17.3583, "lng": 78.4699, "rating": 4.5, "type": "Palace"},
            {"name": "KBR National Park",       "lat": 17.4156, "lng": 78.4283, "rating": 4.3, "type": "Park"},
        ],
        "food": [
            {"name": "Paradise Biryani",        "lat": 17.4399, "lng": 78.4983, "rating": 4.3, "type": "Restaurant"},
            {"name": "Bawarchi Restaurant",     "lat": 17.4282, "lng": 78.4943, "rating": 4.2, "type": "Restaurant"},
            {"name": "Pista House",             "lat": 17.3848, "lng": 78.4797, "rating": 4.3, "type": "Restaurant"},
            {"name": "Shah Ghouse Cafe",        "lat": 17.3601, "lng": 78.4757, "rating": 4.3, "type": "Cafe"},
        ],
        "hotels": [
            {"name": "Taj Falaknuma Palace",    "lat": 17.3308, "lng": 78.4629, "rating": 4.7, "type": "5-Star Hotel"},
            {"name": "ITC Kohenur",             "lat": 17.4333, "lng": 78.3833, "rating": 4.6, "type": "5-Star Hotel"},
            {"name": "Lemon Tree Hotel",        "lat": 17.4415, "lng": 78.3847, "rating": 4.2, "type": "3-Star Hotel"},
        ],
    }

    if category == "all":
        result = []
        for cat_places in places_data.values():
            result.extend(cat_places)
        return jsonify({"places": result, "count": len(result)})

    filtered = places_data.get(category, [])
    return jsonify({"places": filtered, "count": len(filtered), "category": category})


@app.route("/api/itinerary", methods=["GET"])
def itinerary():
    """Generate a day-wise itinerary."""
    days = int(request.args.get("days", 2))
    days = max(1, min(days, 7))

    plans = {
        1: {
            "title": "Hyderabad in a Day",
            "days": [{"day": 1, "title": "Old City Highlights",
                       "morning": "Charminar → Laad Bazaar",
                       "afternoon": "Salar Jung Museum → Chowmahalla Palace",
                       "evening": "Hussain Sagar sunset",
                       "dinner": "Paradise Biryani"}]
        },
        2: {
            "title": "2-Day Hyderabad Explorer",
            "days": [
                {"day": 1, "title": "Old City Heritage",
                 "morning": "Charminar → Laad Bazaar shopping",
                 "afternoon": "Mecca Masjid → Chowmahalla Palace",
                 "evening": "Hussain Sagar sunset → Necklace Road",
                 "dinner": "Shadab Hotel"},
                {"day": 2, "title": "Forts & Culture",
                 "morning": "Golconda Fort",
                 "afternoon": "Salar Jung Museum",
                 "evening": "Birla Mandir → Lumbini Park",
                 "dinner": "Bawarchi Biryani"},
            ]
        },
        3: {
            "title": "3-Day Hyderabad Explorer",
            "days": [
                {"day": 1, "title": "Old City Heritage",
                 "morning": "Charminar → Laad Bazaar",
                 "afternoon": "Chowmahalla Palace → Mecca Masjid",
                 "evening": "Hussain Sagar",
                 "dinner": "Shadab Hotel (Biryani)"},
                {"day": 2, "title": "Forts & Museums",
                 "morning": "Golconda Fort (early)",
                 "afternoon": "Salar Jung Museum",
                 "evening": "Birla Mandir → Planetarium",
                 "dinner": "Paradise Biryani"},
                {"day": 3, "title": "Modern Hyderabad",
                 "morning": "Ramoji Film City",
                 "afternoon": "Hi-Tech City",
                 "evening": "Shilparamam Craft Village",
                 "dinner": "Banjara Hills"},
            ]
        },
    }

    plan = plans.get(days, plans[3])
    return jsonify(plan)


@app.route("/api/languages", methods=["GET"])
def languages():
    return jsonify({"supported": ["en", "hi", "te"],
                    "names": {"en": "English", "hi": "Hindi", "te": "Telugu"}})


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀 Starting Hyderabad Navigator API...")
    print(f"   Running on http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
