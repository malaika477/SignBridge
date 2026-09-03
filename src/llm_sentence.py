"""
llm_sentence.py
----------------
Takes a buffer of recognized sign words (e.g. ["help", "doctor", "pain"])
and turns them into a natural, grammatically correct spoken sentence.

Uses Groq's OpenAI-compatible API (free tier) via the `requests` library.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()  # reads variables from your .env file

API_KEY = os.environ.get("LLM_API_KEY", "YOUR_API_KEY_HERE")
MODEL = os.environ.get("LLM_MODEL", "openai/gpt-oss-20b")
API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are a sign-language sentence composer. You will be given
a short sequence of individual words that a deaf user has signed, in the
order they signed them. Your job is to turn these words into ONE natural,
grammatically correct sentence that best represents what the person is
likely trying to communicate.

Rules:
- Only use the meaning implied by the given words — do not invent new topics.
- Prefer short, clear, everyday sentences (this will be spoken aloud).
- If the words suggest urgency (e.g. "help", "sick", "doctor"), keep that
  urgency in the tone of the sentence.
- Respond with Urdu script if the target_language is "urdu", otherwise
  respond in English. Reply with ONLY the final sentence, nothing else.
"""


def _call_llm(prompt_text: str, system_prompt: str = SYSTEM_PROMPT) -> str:
    """Sends a prompt to Groq LLM and returns the plain text response."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_text},
        ],
    }
    response = requests.post(API_URL, json=payload, headers=headers, timeout=15)
    if not response.ok:
        raise RuntimeError(
            f"Groq API returned {response.status_code}: {response.text}"
        )
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def words_to_sentence(words: list, target_language: str = "english") -> str:
    """
    words: list of recognized sign words in order, e.g. ["help", "doctor", "pain"]
    target_language: "english" or "urdu"
    Returns: a natural sentence string.
    """
    if not words:
        return ""

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Signed words in order: {', '.join(words)}\n"
        f"target_language: {target_language}\n"
        "Compose the sentence now."
    )

    try:
        return _call_llm(prompt)
    except Exception as e:
        print("LLM call failed, using fallback:", e)
        return " ".join(words).capitalize() + "."


def sentence_to_signs(sentence: str, known_words: list) -> list:
    """
    Reverse mode: breaks a typed/spoken sentence down into a sequence of
    sign words the app knows how to display, using only the vocabulary
    the classifier was trained on (known_words).
    """
    prompt = (
        "You convert sentences into sign-language word sequences using only "
        "a given vocabulary.\n\n"
        f"Sentence: {sentence}\n"
        f"Known sign vocabulary: {', '.join(known_words)}\n"
        "Break this sentence into the closest sequence of words from the "
        "known vocabulary, in signing order. Reply as a comma-separated "
        "list only, nothing else."
    )

    try:
        raw = _call_llm(
            prompt,
            system_prompt="You convert sentences into sign-language word sequences.",
        )
        return [w.strip().lower() for w in raw.split(",") if w.strip()]
    except Exception as e:
        print("LLM call failed, using fallback:", e)
        return [w for w in sentence.lower().split() if w in known_words]


if __name__ == "__main__":
    example = ["help", "doctor", "sick"]
    print("Words:", example)
    print("Sentence:", words_to_sentence(example, target_language="english"))