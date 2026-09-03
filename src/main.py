"""
main.py
-------
Owned by: Both teammates (this is where your two pieces connect)

The full live demo loop:
1. Watch webcam, recognize signed words one at a time (Teammate B's code)
2. Buffer recent words
3. After a pause in signing, send the buffer to the LLM to form a sentence
   (Teammate A's code)
4. Speak the sentence aloud (Teammate A's code)
5. Clear the buffer and repeat

Run this after:
- data_collection.py has been used to record signs
- train_classifier.py has produced models/sign_classifier.pkl
- llm_sentence.py has a working API_KEY set (env var LLM_API_KEY)
"""

import cv2
import time
from collections import deque

from realtime_recognize import SignRecognizer
from llm_sentence import words_to_sentence
from tts import speak

PAUSE_TO_TRIGGER_SENTENCE = 2.5  # seconds of no new sign before composing a sentence
TARGET_LANGUAGE = "english"  # change to "urdu" for Urdu output


def main():
    recognizer = SignRecognizer()
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    time.sleep(2)

    word_buffer = deque(maxlen=8)
    last_word_time = time.time()
    sentence_spoken_for_buffer = True

    print("SignBridge running. Sign words, pause briefly to hear the sentence. 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame, word = recognizer.process_frame(frame)

        if word:
            word_buffer.append(word)
            last_word_time = time.time()
            sentence_spoken_for_buffer = False
            print("Recognized:", word)

        # If enough time has passed since the last sign, and we have words
        # waiting, compose and speak the sentence.
        if (word_buffer and not sentence_spoken_for_buffer
                and time.time() - last_word_time > PAUSE_TO_TRIGGER_SENTENCE):
            words = list(word_buffer)
            print("Composing sentence from:", words)
            sentence = words_to_sentence(words, target_language=TARGET_LANGUAGE)
            print("Sentence:", sentence)
            speak(sentence)

            word_buffer.clear()
            sentence_spoken_for_buffer = True

        cv2.putText(frame, " ".join(word_buffer), (10, 460),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.imshow("SignBridge", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
