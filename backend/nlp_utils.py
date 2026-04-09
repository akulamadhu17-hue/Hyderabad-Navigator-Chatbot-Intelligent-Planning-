"""
Hyderabad Navigator - NLP Utilities
Language detection, preprocessing, entity extraction
"""

import re
import unicodedata


# ─── Language Detection ───────────────────────────────────────────────────────

TELUGU_RANGE  = (0x0C00, 0x0C7F)
DEVANAGARI_RANGE = (0x0900, 0x097F)

def detect_language(text: str) -> str:
    """Detect language: 'te' | 'hi' | 'en'"""
    te_count = sum(1 for c in text if TELUGU_RANGE[0] <= ord(c) <= TELUGU_RANGE[1])
    hi_count = sum(1 for c in text if DEVANAGARI_RANGE[0] <= ord(c) <= DEVANAGARI_RANGE[1])

    if te_count > 0:
        return "te"
    if hi_count > 0:
        return "hi"
    return "en"


# ─── Text Preprocessing ───────────────────────────────────────────────────────

def preprocess_text(text: str) -> str:
    """Normalize text for TF-IDF."""
    text = text.strip()
    # Normalize unicode
    text = unicodedata.normalize("NFC", text)
    # Lowercase Latin characters only
    result = []
    for ch in text:
        if ord(ch) < 128:
            result.append(ch.lower())
        else:
            result.append(ch)
    text = "".join(result)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ─── Entity Extraction ────────────────────────────────────────────────────────

HYDERABAD_PLACES = [
    "charminar", "golconda", "golkonda", "hussain sagar", "hussainsagar",
    "ramoji", "birla mandir", "birla temple", "salar jung", "chowmahalla",
    "kbr park", "lumbini park", "nehru zoological", "necklace road",
    "banjara hills", "jubilee hills", "hitech city", "gachibowli",
    "secunderabad", "begum bazaar", "laad bazaar", "abids", "ameerpet",
    "paradise", "bawarchi", "pista house", "shilparamam",
]

DURATION_PATTERNS = [
    # "2 days", "3 nights", "one week"
    (r"\b(\d+)\s*(day|days|night|nights|week|weeks)\b", "numeric"),
    (r"\b(one|two|three|four|five|six|seven)\s*(day|days|night|nights|week|weeks)\b", "word"),
]
WORD_TO_NUM = {"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7}

def extract_duration(text: str):
    """Return (number, unit) or None."""
    t = text.lower()
    for pattern, kind in DURATION_PATTERNS:
        m = re.search(pattern, t)
        if m:
            raw, unit = m.group(1), m.group(2)
            num = WORD_TO_NUM.get(raw, None) if kind == "word" else int(raw)
            return num, unit
    return None


def extract_places(text: str):
    """Return list of recognized Hyderabad place names found in text."""
    t = text.lower()
    found = []
    for place in HYDERABAD_PLACES:
        if place in t:
            found.append(place.title())
    return found


def extract_budget(text: str):
    """Extract budget range hints."""
    t = text.lower()
    if any(w in t for w in ["cheap", "budget", "affordable", "low cost", "सस्ता", "చవకైన"]):
        return "budget"
    if any(w in t for w in ["luxury", "5 star", "five star", "premium", "लग्जरी", "లగ్జరీ"]):
        return "luxury"
    if any(w in t for w in ["mid", "moderate", "medium", "average"]):
        return "mid_range"
    return None


def extract_entities(text: str) -> dict:
    """Extract all entities from user text."""
    return {
        "language": detect_language(text),
        "duration": extract_duration(text),
        "places":   extract_places(text),
        "budget":   extract_budget(text),
    }


# ─── Quick test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    samples = [
        "I want to visit Charminar for two days",
        "నమస్కారం, హైదరాబాద్‌లో చూడవలసిన స్థలాలు",
        "हैदराबाद में 3 दिन की यात्रा की योजना",
        "Budget hotels near Golconda fort",
    ]
    for s in samples:
        print(f"\nText   : {s}")
        print(f"Entities: {extract_entities(s)}")
