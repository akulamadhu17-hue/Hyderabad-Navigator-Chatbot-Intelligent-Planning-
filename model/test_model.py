"""
Hyderabad Navigator - Model Testing Script
Tests the trained Random Forest intent classifier
"""

import pickle
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_model():
    model_path = os.path.join(BASE_DIR, "rf_model.pkl")
    vec_path   = os.path.join(BASE_DIR, "tfidf_vectorizer.pkl")
    le_path    = os.path.join(BASE_DIR, "label_encoder.pkl")

    for p in [model_path, vec_path, le_path]:
        if not os.path.exists(p):
            print(f"❌ Missing: {p}\nRun train_model.py first.")
            sys.exit(1)

    with open(model_path, "rb") as f: clf = pickle.load(f)
    with open(vec_path,   "rb") as f: vec = pickle.load(f)
    with open(le_path,    "rb") as f: le  = pickle.load(f)
    return clf, vec, le


def predict(text, clf, vec, le):
    X = vec.transform([text.lower().strip()])
    proba = clf.predict_proba(X)[0]
    idx   = proba.argmax()
    intent = le.inverse_transform([idx])[0]
    confidence = proba[idx]
    top3 = sorted(
        zip(le.classes_, proba), key=lambda x: x[1], reverse=True
    )[:3]
    return intent, confidence, top3


def run_tests():
    clf, vec, le = load_model()

    test_cases = [
        # English
        ("What are the best places to visit in Hyderabad?", "sightseeing"),
        ("Where can I eat good biryani?",                  "food_recommendation"),
        ("Suggest a hotel near Charminar",                 "hotel_booking"),
        ("How do I get around by metro?",                  "transport"),
        ("What is the weather like in Hyderabad?",         "weather_query"),
        ("Plan a 2 day trip for me",                       "itinerary"),
        ("What is my total budget for 3 days?",            "budget_query"),
        ("Give me some travel tips",                       "local_tips"),
        ("Emergency number police",                        "emergency_info"),
        ("Where can I shop for pearls?",                   "shopping"),
        ("Hello",                                          "greeting"),
        ("Goodbye",                                        "farewell"),
        # Hindi
        ("हैदराबाद में घूमने की जगह बताओ",               "sightseeing"),
        ("बिरयानी कहाँ मिलेगी",                          "food_recommendation"),
        ("नमस्ते",                                        "greeting"),
        # Telugu
        ("హైదరాబాద్‌లో చూడవలసిన స్థలాలు",               "sightseeing"),
        ("నమస్కారం",                                     "greeting"),
        ("హలీమ్ ఎక్కడ దొరుకుతుంది",                    "food_recommendation"),
    ]

    print("\n🧪 Hyderabad Navigator - Model Test Report")
    print("=" * 60)

    correct = 0
    for text, expected in test_cases:
        intent, conf, top3 = predict(text, clf, vec, le)
        ok = intent == expected
        if ok:
            correct += 1
        status = "✅" if ok else "❌"
        print(f"\n{status} Query   : {text}")
        print(f"   Expected : {expected}")
        print(f"   Predicted: {intent}  (conf: {conf*100:.1f}%)")
        if not ok:
            print(f"   Top-3   : {[(i, f'{p*100:.1f}%') for i,p in top3]}")

    total = len(test_cases)
    print("\n" + "=" * 60)
    print(f"📊 Result: {correct}/{total} correct  ({correct/total*100:.1f}%)")

    # Interactive mode
    print("\n💬 Interactive Test (type 'quit' to exit)")
    print("-" * 40)
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ("quit", "exit", "q"):
                break
            if not user_input:
                continue
            intent, conf, top3 = predict(user_input, clf, vec, le)
            print(f"Intent: {intent}  |  Confidence: {conf*100:.1f}%")
            print(f"Top-3 : {[(i, f'{p*100:.1f}%') for i,p in top3]}")
        except KeyboardInterrupt:
            break
    print("Bye!")


if __name__ == "__main__":
    run_tests()
