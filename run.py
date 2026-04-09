"""
Hyderabad Navigator - Main Entry Point
Run this file to start the full application
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

def train_if_needed():
    model_path = os.path.join(BASE_DIR, "model", "rf_model.pkl")
    if not os.path.exists(model_path):
        print("🚀 Training model for first time...")
        sys.path.insert(0, os.path.join(BASE_DIR, "model"))
        from model.train_model import train
        train()
    else:
        print("✅ Model already trained")

if __name__ == "__main__":
    train_if_needed()
    from backend.app import app
    from config.config import PORT, DEBUG
    print(f"\n🌐 Open browser: http://localhost:{PORT}")
    print(f"📁 Frontend:     frontend/index.html")
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
