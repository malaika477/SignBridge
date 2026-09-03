"""
reverse_mode.py
----------------
Owned by: Teammate A (Prompt & Language Layer)

REVERSE MODE: takes a spoken or typed sentence and converts it into a
sequence of sign words from your known vocabulary, displaying them one
at a time like flashcards — simulating an avatar/interpreter signing
the sentence back.

Two input options are supported:
1. TYPED input (default, most reliable for a live demo — no dependency
   on mic quality, background noise, or internet speech recognition)
2. SPOKEN input (optional, via microphone) — falls back to typed input
   automatically if the microphone/speech recognition isn't available,
   so the demo never breaks on stage.

Run this file directly to test reverse mode on its own:
    py -3.11 reverse_mode.py
"""

import cv2
import numpy as np
import time
from llm_sentence import sentence_to_signs

# The same vocabulary your classifier was trained on. Keep this in sync
# with SIGN_KEYS in data_collection.py.
KNOWN_WORDS = [
    "hello", "deaf", "help", "water", "home", "sick", "doctor", "please",
    "thank_you", "yes", "no", "sorry", "welcome", "wait", "food",
]

SECONDS_PER_WORD = 1.5  # how long each sign word is shown before moving to the next


def get_sentence_input():
    """
    Gets the sentence to convert, from voice if available, otherwise
    from typed input. Never raises — always returns something usable.
    """
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening... speak your sentence now.")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        sentence = recognizer.recognize_google(audio)
        print(f"Heard: {sentence}")
        return sentence
    except Exception as e:
        print(f"Voice input unavailable ({e}), switching to typed input.")
        return input("Type the sentence to convert into signs: ").strip()


def display_sign_sequence(words):
    """
    Shows each recognized sign word one at a time in a simple flashcard
    style window — simulating an avatar/interpreter signing the words
    in sequence. This is the visual output for reverse mode.
    """
    if not words:
        print("No matching sign words found for that sentence.")
        return

    for word in words:
        canvas = np.zeros((400, 700, 3), dtype=np.uint8)
        canvas[:] = (40, 40, 40)  # dark background

        display_word = word.replace("_", " ").upper()
        text_size = cv2.getTextSize(display_word, cv2.FONT_HERSHEY_SIMPLEX, 1.8, 3)[0]
        text_x = (canvas.shape[1] - text_size[0]) // 2
        text_y = (canvas.shape[0] + text_size[1]) // 2

        cv2.putText(canvas, display_word, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 150), 3)
        cv2.putText(canvas, "SignBridge - Reverse Mode", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

        cv2.imshow("SignBridge - Reverse Mode", canvas)
        cv2.waitKey(int(SECONDS_PER_WORD * 1000))

    cv2.destroyAllWindows()


def run_reverse_mode():
    sentence = get_sentence_input()
    if not sentence:
        print("No sentence provided.")
        return

    print("Converting to sign sequence...")
    words = sentence_to_signs(sentence, known_words=KNOWN_WORDS)
    print("Sign sequence:", words)

    display_sign_sequence(words)


if __name__ == "__main__":
    run_reverse_mode()