"""
Hyderabad Navigator - Model Training Script
Trains Random Forest classifier for intent classification
Supports English, Hindi, and Telugu
"""

import json
import pickle
import numpy as np
import os
import sys

# Try to import required libraries
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError as e:
    print(f"Missing library: {e}")
    print("Run: pip install scikit-learn matplotlib seaborn")
    sys.exit(1)

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset.json")
MODEL_DIR = BASE_DIR

# ─── Load Dataset ─────────────────────────────────────────────────────────────
def load_dataset(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts, labels = [], []
    for intent in data["intents"]:
        tag = intent["tag"]
        for pattern in intent["patterns"]:
            texts.append(pattern)
            labels.append(tag)

    print(f"✅ Dataset loaded: {len(texts)} samples, {len(set(labels))} intents")
    return texts, labels

# ─── Preprocessing ────────────────────────────────────────────────────────────
def preprocess(texts):
    """Basic normalization for multilingual text."""
    processed = []
    for t in texts:
        t = t.lower().strip()
        processed.append(t)
    return processed

# ─── Train Model ──────────────────────────────────────────────────────────────
def train(dataset_path=DATASET_PATH, model_dir=MODEL_DIR):
    print("\n🚀 Starting Hyderabad Navigator Model Training...")
    print("=" * 55)

    texts, labels = load_dataset(dataset_path)
    texts = preprocess(texts)

    # Encode labels
    le = LabelEncoder()
    y = le.fit_transform(labels)

    # TF-IDF Vectorizer (works for multilingual text)
    vectorizer = TfidfVectorizer(
        analyzer="char_wb",    # character n-grams work well for multilingual
        ngram_range=(2, 4),
        max_features=8000,
        sublinear_tf=True,
        min_df=1
    )
    X = vectorizer.fit_transform(texts)

    print(f"📊 Feature matrix: {X.shape}")

    # Stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Random Forest Classifier
    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        max_features="sqrt",
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    print("\n🌲 Training Random Forest Classifier...")
    clf.fit(X_train, y_train)

    # Evaluation
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"\n✅ Test Accuracy: {acc * 100:.2f}%")
    print("\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # Cross-validation
    skf = StratifiedKFold(n_splits=min(5, min(np.bincount(y))), shuffle=True, random_state=42)
    cv_scores = cross_val_score(clf, X, y, cv=skf, scoring="accuracy")
    print(f"🔁 Cross-Val Accuracy: {cv_scores.mean() * 100:.2f}% ± {cv_scores.std() * 100:.2f}%")

    # Confusion Matrix
    try:
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(12, 9))
        sns.heatmap(
            cm, annot=True, fmt="d",
            xticklabels=le.classes_,
            yticklabels=le.classes_,
            cmap="YlOrRd"
        )
        plt.title("Intent Classification - Confusion Matrix", fontsize=14)
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        cm_path = os.path.join(model_dir, "confusion_matrix.png")
        plt.savefig(cm_path, dpi=150)
        plt.close()
        print(f"📊 Confusion matrix saved: {cm_path}")
    except Exception as e:
        print(f"⚠️ Could not save confusion matrix: {e}")

    # Save artifacts
    model_path = os.path.join(model_dir, "rf_model.pkl")
    vec_path = os.path.join(model_dir, "tfidf_vectorizer.pkl")
    le_path = os.path.join(model_dir, "label_encoder.pkl")

    with open(model_path, "wb") as f:
        pickle.dump(clf, f)
    with open(vec_path, "wb") as f:
        pickle.dump(vectorizer, f)
    with open(le_path, "wb") as f:
        pickle.dump(le, f)

    print(f"\n💾 Model saved → {model_path}")
    print(f"💾 Vectorizer saved → {vec_path}")
    print(f"💾 Label encoder saved → {le_path}")
    print("\n🎉 Training complete!")

    return clf, vectorizer, le, acc

if __name__ == "__main__":
    train()
