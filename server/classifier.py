"""
server/classifier.py
--------------------
Loads the trained sign_classifier.pkl model and exposes a simple
predict_sign() function that maps a 126-element landmark vector to
a (word, confidence) tuple.

This is the same model used by src/realtime_recognize.py for the
desktop demo — the web server just wraps it in an HTTP-friendly interface.
"""

import os
import joblib
import numpy as np
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "sign_classifier.pkl")
DATA_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "landmarks.csv")

_model = None
_sign_landmarks = None


def _load_model():
    """Lazy-load the classifier model (loaded once, cached globally)."""
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_sign(landmarks: list[float], confidence_threshold: float = 0.5):
    """
    Predict the sign word from a 126-element landmark vector.

    Args:
        landmarks: list of 126 floats (2 hands x 21 landmarks x 3 coords,
                   sorted left-to-right, padded with zeros if only 1 hand)
        confidence_threshold: minimum probability to accept a prediction

    Returns:
        (word, confidence) if above threshold, or (None, confidence) if below.
    """
    clf = _load_model()
    features = np.array([landmarks])
    probs = clf.predict_proba(features)[0]
    best_idx = probs.argmax()
    confidence = float(probs[best_idx])
    predicted = clf.classes_[best_idx]

    if confidence >= confidence_threshold:
        return predicted, confidence
    return None, confidence


def get_vocabulary() -> list[str]:
    """Return the list of words the classifier was trained on."""
    clf = _load_model()
    return sorted(clf.classes_.tolist())


def get_sign_landmarks() -> dict:
    """
    Return the average landmark positions for each trained sign word.
    Used by reverse mode to draw the hand shape for each sign.
    Returns: {"word": [126 floats], ...}
    """
    global _sign_landmarks
    if _sign_landmarks is None:
        df = pd.read_csv(DATA_CSV)
        _sign_landmarks = {}
        for word, group in df.groupby("label"):
            avg = group.drop(columns=["label"]).mean().tolist()
            _sign_landmarks[word] = [round(v, 6) for v in avg]
    return _sign_landmarks
