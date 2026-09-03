# SignBridge — Sign Language Interpreter

Real-time sign language → spoken sentence interpreter, built for the
Alibaba Cloud AI Hackathon Pakistan 2026.

## How it works (pipeline)

```
Webcam → MediaPipe Hands → Landmark features → Classifier → Recognized word
       → (buffer of recent words) → LLM prompt → Natural sentence → Text-to-Speech
```

## Folder structure

```
signbridge/
├── data/                   # Recorded training samples (CSV of hand landmarks + labels)
│   └── landmarks.csv
├── models/                 # Saved trained classifier
│   └── sign_classifier.pkl
├── src/
│   ├── data_collection.py  # Record your own signs via webcam to build a dataset
│   ├── train_classifier.py # Train a simple classifier on collected landmarks
│   ├── realtime_recognize.py # Live webcam demo: detects signs in real time
│   ├── llm_sentence.py     # Turns recognized words into a natural sentence (LLM prompt)
│   ├── tts.py               # Converts final sentence to speech
│   └── main.py              # Ties everything together for the live demo
├── requirements.txt
└── README.md
```

## Team roles (suggested)

- **Teammate A (you) — Prompt & Language Layer**
  Owns `llm_sentence.py` and `tts.py`. This is where the "smart" part lives:
  turning raw recognized words into fluent, natural sentences.

- **Teammate B — Vision & Data Layer**
  Owns `data_collection.py`, `train_classifier.py`, and `realtime_recognize.py`.
  Responsible for recording sign samples, training the classifier, and getting
  real-time hand tracking working smoothly.

Both of you should be able to run `main.py` together once your pieces are done.

## Setup

```bash
pip install -r requirements.txt
```

## Step-by-step build order

1. **Collect data** — run `data_collection.py`, pick ~15-20 words
   (hello, thank you, help, water, pain, yes, no, doctor, home, food,
   stop, please, sorry, good, bad, more, again, name, understand, wait).
   Record each sign 15-20 times from slightly different angles/speeds.

2. **Train the classifier** — run `train_classifier.py`. This builds a
   small model that maps hand landmark positions to a word label.

3. **Test real-time recognition** — run `realtime_recognize.py` to confirm
   the webcam correctly identifies signs live.

4. **Wire in the LLM layer** — fill in your API key in `llm_sentence.py`
   (use Alibaba Cloud Model Studio / Qwen API if you got hackathon credits,
   otherwise any LLM API works for prototyping).

5. **Add text-to-speech** — `tts.py` uses a free TTS library by default so
   you can demo without any paid API.

6. **Run the full demo** — `main.py` combines everything into the live
   webcam → sentence → speech pipeline.

## Demo script (suggested)

1. Sign: "help" → "doctor" → "pain"
2. App recognizes words in real time (shown on screen as they're detected)
3. After a short pause, the LLM turns it into: *"I need a doctor, I am in pain."*
4. The sentence is spoken aloud.
5. Optional: show reverse mode — type a sentence, see it broken into sign words.

