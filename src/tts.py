"""
tts.py
------
Owned by: Teammate A (Prompt & Language Layer)

Converts the final generated sentence into spoken audio.

Uses pyttsx3 by default (fully offline, free, no API key needed — good
for a reliable live demo). If you want higher-quality Urdu voice output,
swap in a cloud TTS API (Alibaba Cloud also offers speech synthesis).
"""

import pyttsx3

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        _engine.setProperty("rate", 165)  # slightly slower = clearer for demo
    return _engine


def speak(text: str):
    """Speaks the given text out loud (blocking call)."""
    if not text:
        return
    engine = _get_engine()
    engine.say(text)
    engine.runAndWait()


def list_available_voices():
    """Useful for picking a voice that sounds better for Urdu/English mix."""
    engine = _get_engine()
    voices = engine.getProperty("voices")
    for v in voices:
        print(v.id, "-", v.name, "-", v.languages)


if __name__ == "__main__":
    list_available_voices()
    speak("I need a doctor, I am in pain.")
