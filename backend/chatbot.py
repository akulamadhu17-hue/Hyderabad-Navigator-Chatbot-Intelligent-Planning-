"""
Hyderabad Navigator - Core Chatbot Logic
Loads RF model and returns intent-based responses
"""

import json
import pickle
import os
import random
from backend.nlp_utils import detect_language, preprocess_text, extract_entities

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR  = os.path.join(BASE_DIR, "model")
DATASET_PATH = os.path.join(MODEL_DIR, "dataset.json")


class HyderabadChatbot:
    def __init__(self):
        self.model      = None
        self.vectorizer = None
        self.le         = None
        self.intents    = {}
        self._load_model()
        self._load_intents()

    # ── Loading ──────────────────────────────────────────────────────────────

    def _load_model(self):
        paths = {
            "model":      os.path.join(MODEL_DIR, "rf_model.pkl"),
            "vectorizer": os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl"),
            "le":         os.path.join(MODEL_DIR, "label_encoder.pkl"),
        }
        missing = [k for k, p in paths.items() if not os.path.exists(p)]
        if missing:
            print(f"⚠️  Model files missing: {missing}. Run model/train_model.py first.")
            return
        with open(paths["model"],      "rb") as f: self.model      = pickle.load(f)
        with open(paths["vectorizer"], "rb") as f: self.vectorizer = pickle.load(f)
        with open(paths["le"],         "rb") as f: self.le         = pickle.load(f)
        print("✅ Model loaded successfully")

    def _load_intents(self):
        if not os.path.exists(DATASET_PATH):
            print(f"⚠️  Dataset not found: {DATASET_PATH}")
            return
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for intent in data["intents"]:
            self.intents[intent["tag"]] = intent.get("responses", {})
        print(f"✅ Loaded {len(self.intents)} intents")

    # ── Prediction ───────────────────────────────────────────────────────────

    def predict_intent(self, text: str):
        if not self.model:
            return "greeting", 0.5
        processed = preprocess_text(text)
        X = self.vectorizer.transform([processed])
        proba = self.model.predict_proba(X)[0]
        idx = proba.argmax()
        return self.le.inverse_transform([idx])[0], float(proba[idx])

    # ── Response ─────────────────────────────────────────────────────────────

    def get_response(self, text: str, lang: str = None) -> dict:
        entities = extract_entities(text)
        detected_lang = lang or entities["language"]

        intent, confidence = self.predict_intent(text)

        # Fallback for low confidence
        if confidence < 0.25:
            fallback = {
                "en": "I'm not sure I understood that. Could you rephrase? You can ask me about places, food, hotels, transport, or weather in Hyderabad!",
                "hi": "मुझे समझ नहीं आया। कृपया दोबारा पूछें। आप हैदराबाद के स्थानों, खाने, होटल, यातायात के बारे में पूछ सकते हैं!",
                "te": "నాకు అర్థం కాలేదు. దయచేసి మళ్ళీ అడగండి. హైదరాబాద్ స్థలాలు, ఆహారం, హోటళ్లు, రవాణా గురించి అడగవచ్చు!",
            }
            return {
                "intent": "unknown",
                "confidence": confidence,
                "response": fallback.get(detected_lang, fallback["en"]),
                "language": detected_lang,
                "entities": entities,
            }

        responses = self.intents.get(intent, {})
        response_text = (
            responses.get(detected_lang)
            or responses.get("en")
            or "Sorry, I don't have information for that."
        )

        return {
            "intent":     intent,
            "confidence": round(confidence, 3),
            "response":   response_text,
            "language":   detected_lang,
            "entities":   entities,
        }


# Singleton
_chatbot_instance = None

def get_chatbot() -> HyderabadChatbot:
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = HyderabadChatbot()
    return _chatbot_instance
