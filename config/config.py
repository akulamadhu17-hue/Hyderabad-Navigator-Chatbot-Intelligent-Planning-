"""
Hyderabad Navigator - Configuration
Replace placeholder values with your actual API keys
"""

import os

# ─── API Keys (set via environment variables or replace here) ────────────────

GOOGLE_MAPS_API_KEY      = os.getenv("GOOGLE_MAPS_API_KEY",      "AIzaSyALrRly3HU580lIhlMmaj8dMIDgRIEWyVE")
GOOGLE_PLACES_API_KEY    = os.getenv("GOOGLE_PLACES_API_KEY",    "YOUR_GOOGLE_PLACES_API_KEY")
OPENWEATHER_API_KEY      = os.getenv("OPENWEATHER_API_KEY",      "4ba37df544mshc725924f35a042bp131112jsn54839f5b3983")
GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY", "YOUR_GOOGLE_TRANSLATE_API_KEY")
ANTHROPIC_API_KEY        = os.getenv("ANTHROPIC_API_KEY",        "YOUR_ANTHROPIC_API_KEY")

# ─── App Settings ─────────────────────────────────────────────────────────────

SECRET_KEY    = os.getenv("SECRET_KEY", "hyderabad-navigator-secret-2024")
DEBUG         = os.getenv("DEBUG", "True") == "True"
PORT          = int(os.getenv("PORT", 5000))

# ─── Hyderabad Coordinates ───────────────────────────────────────────────────

HYDERABAD_LAT = 17.3850
HYDERABAD_LON = 78.4867

# ─── Model Settings ──────────────────────────────────────────────────────────

CONFIDENCE_THRESHOLD = 0.25
SUPPORTED_LANGUAGES  = ["en", "hi", "te"]
