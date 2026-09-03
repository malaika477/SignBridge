"""
train_classifier.py
--------------------
Owned by: Teammate B (Vision & Data Layer)

Trains a simple classifier that maps hand landmark positions to a word
label, using the data recorded by data_collection.py.

Output: models/sign_classifier.pkl
"""

import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

DATA_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "landmarks.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "sign_classifier.pkl")


def main():
    df = pd.read_csv(DATA_CSV)
    X = df.drop(columns=["label"])
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Random Forest is a good default: no tuning needed, works well on small
    # datasets like the ones you'll collect in a hackathon timeframe.
    clf = RandomForestClassifier(n_estimators=150, random_state=42)
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    print("Validation performance:")
    print(classification_report(y_test, preds))

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
