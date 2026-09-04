# SignBridge — AI Sign Language Interpreter

A real-time, two-way AI sign language interpreter, built for the **Alibaba Cloud AI Hackathon Pakistan 2026** (Theme: *AI for Pakistan's Future*).

SignBridge lets a Deaf user and a hearing person communicate directly, without a human interpreter present — using just a webcam and microphone.

---

## The Problem

Millions of Deaf and hard-of-hearing people in Pakistan face a daily communication barrier. Certified Pakistan Sign Language (PSL) interpreters are scarce and rarely available in the moments they're needed most — hospitals, schools, government offices, or everyday conversation. Without an interpreter present, communication breaks down in both directions.

## The Solution

SignBridge works two ways:

- **Sign → Text (Forward Mode):** A Deaf user signs in front of a webcam. SignBridge recognizes the signs in real time, and an AI language model composes them into a natural, fluent spoken sentence.
- **Text / Speech → Sign Words (Reverse Mode):** A hearing person types or speaks a sentence. An AI language model reasons about its meaning and maps it onto SignBridge's known sign vocabulary, then plays each matching sign as a flashcard in sequence for the Deaf user to read.

**Example — Forward Mode:**
> Signed: `HELLO → DEAF → SICK → HELP → DOCTOR`
> SignBridge speaks: *"Hello, I am Deaf and I am sick. I need help, please call a doctor."*

**Example — Reverse Mode:**
> Typed: *"I am feeling unwell and need medical attention"*
> SignBridge plays the flashcard sequence: `SICK → DOCTOR → HELP → PLEASE`

Note that the sentence above uses none of the exact vocabulary words — the AI is reasoning about meaning, not just matching keywords.

---

## How It Works

```
Forward Mode:
Webcam → MediaPipe Hands → Landmark features → Classifier → Recognized word
       → (buffer of recent words) → LLM prompt → Natural sentence → Text-to-Speech

Reverse Mode:
Typed / spoken sentence → Speech-to-text (if spoken) → LLM prompt
       → Sequence of known sign words → Flashcard playback
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Hand tracking | MediaPipe Hands (21 landmarks per hand, two hands supported) |
| Sign classification | Random Forest classifier (scikit-learn), ~94% validation accuracy |
| Language model | Groq (Llama 3) — composes sentences and reasons about sign-word mapping |
| Text-to-speech | pyttsx3 |
| Speech-to-text | SpeechRecognition, with typed-input fallback |
| Backend | FastAPI + WebSockets (real-time recognition stream) |
| Frontend | React + Vite |
| Core scripting / prototyping | Python, OpenCV |

---

## Project Structure

```
signbridge/
├── data/
│   └── landmarks.csv          # Recorded training samples (hand landmarks + labels)
├── frontend/                  # React web app (browser UI for both modes)
│   ├── src/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── server/                    # FastAPI backend (WebSocket-based recognition service)
│   ├── app.py
│   └── classifier.py
├── src/                       # Core Python pipeline (standalone / prototyping scripts)
│   ├── data_collection.py     # Record signs via webcam to build the dataset
│   ├── train_classifier.py    # Train the classifier on collected landmarks
│   ├── realtime_recognize.py  # Live webcam sign recognition
│   ├── llm_sentence.py        # LLM: words → sentence, and sentence → sign words
│   ├── tts.py                 # Text-to-speech output
│   ├── reverse_mode.py        # Reverse mode: speech/text → sign flashcard sequence
│   └── main.py                # Full forward-mode pipeline, end to end
├── .env.example                # Template for required environment variables
├── requirements.txt
└── README.md
```

---

## Setup

### Python environment (core pipeline)

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your own LLM API key:

```
LLM_API_KEY=your_key_here
```

### Backend (FastAPI server)

```bash
cd server
uvicorn app:app --reload --port 8001
```

### Frontend (React app)

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173` and connects to the backend at `ws://localhost:8001`.

---

## Current Vocabulary

`hello`, `deaf`, `help`, `water`, `home`, `sick`, `doctor`, `please`, `thank_you`, `yes`, `no`, `sorry`, `welcome`, `wait`, `food`

Both one-handed and two-handed signs are supported.

---

## What's Built

- Real-time two-hand sign recognition (~94% validation accuracy)
- LLM-powered sentence composition from recognized signs (Forward Mode)
- LLM-powered sign-word sequencing from typed or spoken sentences (Reverse Mode), displayed as a flashcard sequence
- Text-to-speech output
- Speech-to-text input with automatic fallback to typed input
- Web-based interface for both modes, backed by a FastAPI WebSocket service

## Honest Limitations & Roadmap

- Reverse Mode currently displays each matched sign as a **text flashcard**, not a rendered hand image or animation. Visual hand-sign rendering is the next planned step.
- The current vocabulary is intentionally focused (15 core words) to keep recognition accuracy high; expanding vocabulary is a natural next step.
- Motion-based signs (where meaning depends on movement, not just static hand shape) are not yet distinguished from static signs.
- Community validation with Deaf PSL users and experts is planned to verify sign accuracy going forward.

---

## Demo Script

1. Sign: `HELLO → DEAF → SICK → HELP → DOCTOR`
2. SignBridge recognizes the sequence live and speaks: *"Hello, I am Deaf and I am sick. I need help, please call a doctor."*
3. Switch to Reverse Mode. Type: *"I am feeling unwell and need medical attention."*
4. Click **Convert to Signs**, then **Play sequence** — SignBridge plays `SICK → DOCTOR → HELP → PLEASE` as flashcards.

---

Built by **Malaika Amjad** for the Alibaba Cloud AI Hackathon Pakistan 2026.
