"""
data_collection.py
-------------------
Owned by: Teammate B (Vision & Data Layer)

Records webcam hand-landmark samples for each sign you want to recognize.
Press a letter key to label the CURRENT sign, then hold the pose steady
while it records several frames. Press 'q' to quit and save.

Output: data/landmarks.csv
Each row = 21 hand landmarks (x, y, z) flattened + the word label.
"""

import cv2
import mediapipe as mp
import csv
import os
import time

# ---- CONFIGURE YOUR SIGN LIST HERE ----
# Map a keyboard key to the word it represents.
# Starting with 12 core words for the first working prototype.
# The rest of your researched list (welcome, wait, stop, understand)
# can be added later once this set works reliably.
SIGN_KEYS = {
    "h": "hello",
    "d": "deaf",
    "l": "help",
    "w": "water",
    "o": "home",
    "s": "sick",
    "c": "doctor",
    "p": "please",
    "t": "thank_you",
    "y": "yes",
    "n": "no",
    "r": "sorry",
    "e": "welcome",
    "a": "wait",
    "x": "stop",
    "f": "food",
}

OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "landmarks.csv")
SAMPLES_PER_KEYPRESS = 15  # frames captured each time you press a key

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils


def flatten_landmarks(hand_landmarks):
    """Turn MediaPipe's 21 (x, y, z) landmarks into one flat list of 63 numbers."""
    row = []
    for lm in hand_landmarks.landmark:
        row.extend([lm.x, lm.y, lm.z])
    return row


def extract_two_hand_features(multi_hand_landmarks):
    """
    Combines up to 2 hands into one consistent 126-number feature row.
    Hands are sorted left-to-right (by wrist x position) so the order is
    always the same, regardless of which hand MediaPipe detects first.
    If only one hand is visible, the other 63 numbers are filled with 0.
    """
    hands_data = []
    for hand_landmarks in multi_hand_landmarks:
        wrist_x = hand_landmarks.landmark[0].x
        hands_data.append((wrist_x, flatten_landmarks(hand_landmarks)))

    hands_data.sort(key=lambda h: h[0])  # left-to-right order

    features = []
    for _, flat in hands_data:
        features.extend(flat)

    while len(features) < 126:  # pad if fewer than 2 hands detected
        features.extend([0.0] * 63)

    return features[:126]


def main():
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    file_exists = os.path.isfile(OUTPUT_CSV)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    time.sleep(2)
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

    print("Sign keys:", SIGN_KEYS)
    print("Hold your hand sign steady and press the matching key.")
    print("Press 'q' to quit.")

    with open(OUTPUT_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            header = [f"{axis}{i}" for i in range(42) for axis in ("x", "y", "z")]
            header.append("label")
            writer.writerow(header)

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            cv2.putText(frame, "Press a sign key to record, 'q' to quit", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.imshow("SignBridge - Data Collection", frame)

            key = cv2.waitKey(1) & 0xFF
            key_char = chr(key) if key != 255 else ""

            if key_char == "q":
                break

            if key_char in SIGN_KEYS and result.multi_hand_landmarks:
                label = SIGN_KEYS[key_char]
                print(f"Recording '{label}'...")
                count = 0
                while count < SAMPLES_PER_KEYPRESS:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame = cv2.flip(frame, 1)
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    result = hands.process(rgb)
                    if result.multi_hand_landmarks:
                        row = extract_two_hand_features(result.multi_hand_landmarks)
                        row.append(label)
                        writer.writerow(row)
                        count += 1
                    cv2.imshow("SignBridge - Data Collection", frame)
                    cv2.waitKey(1)
                    time.sleep(0.05)
                print(f"Saved {count} samples for '{label}'.")

    cap.release()
    cv2.destroyAllWindows()
    print(f"Done. Data saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
