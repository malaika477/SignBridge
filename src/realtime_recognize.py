"""
realtime_recognize.py
----------------------
Owned by: Teammate B (Vision & Data Layer)

Runs the webcam live, detects hand landmarks with MediaPipe, and uses the
trained classifier to predict which word is being signed. Recognized words
are collected into a rolling buffer that main.py sends to the LLM layer.
"""

import cv2
import mediapipe as mp
import joblib
import os
import time
from collections import deque

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "sign_classifier.pkl")

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils


class SignRecognizer:
    def __init__(self, confidence_threshold=0.5, cooldown_seconds=1.2):
        self.clf = joblib.load(MODEL_PATH)
        self.hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
        self.confidence_threshold = confidence_threshold
        self.cooldown_seconds = cooldown_seconds
        self.last_word = None
        self.last_capture_time = 0

    def _flatten(self, hand_landmarks):
        row = []
        for lm in hand_landmarks.landmark:
            row.extend([lm.x, lm.y, lm.z])
        return row

    def _extract_two_hand_features(self, multi_hand_landmarks):
        """Same logic as data_collection.py — must match exactly so the
        trained model sees the same feature format it was trained on."""
        hands_data = []
        for hand_landmarks in multi_hand_landmarks:
            wrist_x = hand_landmarks.landmark[0].x
            hands_data.append((wrist_x, self._flatten(hand_landmarks)))

        hands_data.sort(key=lambda h: h[0])

        features = []
        for _, flat in hands_data:
            features.extend(flat)

        while len(features) < 126:
            features.extend([0.0] * 63)

        return features[:126]

    def process_frame(self, frame):
        """Returns (annotated_frame, recognized_word_or_None)."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)
        word = None

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            features = [self._extract_two_hand_features(result.multi_hand_landmarks)]
            probs = self.clf.predict_proba(features)[0]
            best_idx = probs.argmax()
            confidence = probs[best_idx]
            predicted = self.clf.classes_[best_idx]

            now = time.time()
            if (confidence >= self.confidence_threshold
                    and now - self.last_capture_time > self.cooldown_seconds):
                word = predicted
                self.last_capture_time = now

            cv2.putText(frame, f"{predicted} ({confidence:.2f})", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        return frame, word


def run_standalone_demo():
    """Quick way to test recognition on its own, without the LLM/TTS layer."""
    recognizer = SignRecognizer()
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    time.sleep(2)
    recent_words = deque(maxlen=10)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame, word = recognizer.process_frame(frame)

        if word:
            recent_words.append(word)
            print("Recognized:", word, "| Buffer:", list(recent_words))

        cv2.putText(frame, " ".join(recent_words), (10, 460),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.imshow("SignBridge - Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_standalone_demo()
