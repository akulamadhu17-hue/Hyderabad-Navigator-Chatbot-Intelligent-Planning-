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
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from config.config import (
    SECRET_KEY, DEBUG, PORT,
    OPENWEATHER_API_KEY, GOOGLE_PLACES_API_KEY,
    GOOGLE_MAPS_API_KEY, HYDERABAD_LAT, HYDERABAD_LON
)
from backend.chatbot import get_chatbot
from backend.voice_handler import text_to_speech_base64, speech_to_text

# ─── App Setup ────────────────────────────────────────────────────────────────

FRONTEND_FOLDER = os.path.join(BASE_DIR, "frontend")

app = Flask(__name__, static_folder=FRONTEND_FOLDER)
app.secret_key = SECRET_KEY

CORS(app, resources={r"/api/*": {"origins": "*"}})

# Pre-load chatbot
chatbot = get_chatbot()

# ─── Frontend Routes (IMPORTANT) ──────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(FRONTEND_FOLDER, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(FRONTEND_FOLDER, path)


# ─── API Routes ───────────────────────────────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    text = data.get("message", "").strip()
    lang = data.get("language")

    if not text:
        return jsonify({"error": "No message provided"}), 400

    result = chatbot.get_response(text, lang)

    if data.get("tts", False):
        audio_b64 = text_to_speech_base64(result["response"], result["language"])
        result["audio_base64"] = audio_b64

    return jsonify(result)


@app.route("/api/voice", methods=["POST"])
def voice():
    data = request.get_json(silent=True) or {}
    audio_b64 = data.get("audio_base64", "")
    lang = data.get("language", "en")

    if not audio_b64:
        return jsonify({"error": "No audio provided"}), 400

    try:
        audio_bytes = base64.b64decode(audio_b64)
    except Exception:
        return jsonify({"error": "Invalid base64 audio"}), 400

    transcription = speech_to_text(audio_bytes, lang)
    if not transcription:
        return jsonify({"error": "Could not transcribe audio"}), 422

    result = chatbot.get_response(transcription, lang)
    result["transcription"] = transcription

    audio_out = text_to_speech_base64(result["response"], result["language"])
    result["audio_base64"] = audio_out

    return jsonify(result)


@app.route("/api/weather", methods=["GET"])
def weather():
    if OPENWEATHER_API_KEY == "YOUR_OPENWEATHER_API_KEY":
        return jsonify({
            "city": "Hyderabad",
            "temperature": 32,
            "feels_like": 35,
            "description": "Partly cloudy",
            "humidity": 55,
            "wind_speed": 12,
            "icon": "02d",
            "note": "Mock data"
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
            "city": d["name"],
            "temperature": round(d["main"]["temp"]),
            "feels_like": round(d["main"]["feels_like"]),
            "description": d["weather"][0]["description"].capitalize(),
            "humidity": d["main"]["humidity"],
            "wind_speed": round(d["wind"]["speed"] * 3.6),
            "icon": d["weather"][0]["icon"],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/places", methods=["GET"])
def places():
    category = request.args.get("category", "all")

    places_data = {
        "sightseeing": [
            {"name": "Charminar", "lat": 17.3616, "lng": 78.4747},
            {"name": "Golconda Fort", "lat": 17.3833, "lng": 78.4011},
        ]
    }

    if category == "all":
        result = []
        for cat in places_data.values():
            result.extend(cat)
        return jsonify({"places": result})

    return jsonify({"places": places_data.get(category, [])})


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀 Starting Hyderabad Navigator...")
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
