/**
 * ReverseMode.jsx
 * ---------------
 * Reverse mode: type or speak a sentence → server breaks it into sign words
 * → displayed as simple text flashcards in sequence.
 *
 * Features:
 * - Text input for typing a sentence
 * - Microphone button using browser Web Speech API for voice input
 * - "Convert to Signs" button that calls POST /api/reverse
 * - Flashcard display showing each sign word with auto-advance
 */
import { useState, useCallback, useRef, useEffect } from 'react'

export default function ReverseMode() {
  const [inputText, setInputText] = useState('')
  const [signWords, setSignWords] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [listening, setListening] = useState(false)
  const [currentCard, setCurrentCard] = useState(0)
  const [playing, setPlaying] = useState(false)
  const recognitionRef = useRef(null)
  const playTimerRef = useRef(null)

  // --- Voice input via Web Speech API ---
  const startListening = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      setError('Speech recognition not supported in this browser. Use Chrome or Edge.')
      return
    }

    const recognition = new SpeechRecognition()
    recognition.lang = 'en-US'
    recognition.interimResults = false
    recognition.maxAlternatives = 1

    recognition.onstart = () => setListening(true)
    recognition.onend = () => setListening(false)
    recognition.onerror = (e) => {
      setListening(false)
      if (e.error !== 'aborted') {
        setError(`Speech error: ${e.error}`)
      }
    }
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      setInputText(transcript)
    }

    recognitionRef.current = recognition
    recognition.start()
  }, [])

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
  }, [])

  // --- Convert sentence to signs ---
  const convertToSigns = useCallback(async () => {
    if (!inputText.trim()) return

    setLoading(true)
    setError(null)
    setSignWords([])
    setCurrentCard(0)
    setPlaying(false)

    try {
      const res = await fetch('/api/reverse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sentence: inputText.trim() }),
      })
      const data = await res.json()
      if (data.error) {
        setError(data.error)
      } else {
        setSignWords(data.words || [])
      }
    } catch (err) {
      setError(`Server error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }, [inputText])

  // --- Flashcard auto-advance ---
  useEffect(() => {
    if (playing && signWords.length > 0) {
      playTimerRef.current = setInterval(() => {
        setCurrentCard(prev => {
          if (prev >= signWords.length - 1) {
            setPlaying(false)
            return prev
          }
          return prev + 1
        })
      }, 1500)
    }
    return () => {
      if (playTimerRef.current) clearInterval(playTimerRef.current)
    }
  }, [playing, signWords.length])

  const handlePlay = () => {
    setCurrentCard(0)
    setPlaying(true)
  }

  const handleStop = () => {
    setPlaying(false)
    if (playTimerRef.current) clearInterval(playTimerRef.current)
  }

  const speechSupported = typeof window !== 'undefined' &&
    (window.SpeechRecognition || window.webkitSpeechRecognition)

  return (
    <div className="reverse-mode">
      <h3 className="section-label">Speech/Text → Sign Vocabulary</h3>
      <p className="reverse-hint">
        Type or speak a sentence to see it broken down into the sign vocabulary words
        your classifier recognises — displayed as text labels in sequence.
      </p>
      <p className="reverse-disclaimer">
        Currently displays sign vocabulary as text labels.
        Visual hand-sign rendering is planned for a future version.
      </p>

      {/* Input area */}
      <div className="reverse-input-row">
        <input
          type="text"
          className="reverse-input"
          placeholder="Type a sentence... e.g. I need help from a doctor"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && convertToSigns()}
        />

        {speechSupported && (
          <button
            className={`mic-button ${listening ? 'mic-listening' : ''}`}
            onClick={listening ? stopListening : startListening}
            title={listening ? 'Stop listening' : 'Speak a sentence'}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/>
              <path d="M19 10v2a7 7 0 01-14 0v-2"/>
              <line x1="12" y1="19" x2="12" y2="23"/>
              <line x1="8" y1="23" x2="16" y2="23"/>
            </svg>
          </button>
        )}

        <button
          className="convert-button"
          onClick={convertToSigns}
          disabled={loading || !inputText.trim()}
        >
          {loading ? 'Converting...' : 'Convert to Signs'}
        </button>
      </div>

      {listening && (
        <div className="listening-indicator">
          <span className="listening-dot" />
          Listening... speak your sentence now
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="error-state">
          <span className="error-icon">&#9888;</span>
          <p className="error-text">{error}</p>
        </div>
      )}

      {/* Flashcard display */}
      {signWords.length > 0 && (
        <div className="flashcard-section">
          <div className="flashcard-controls">
            <span className="flashcard-count">
              {currentCard + 1} / {signWords.length}
            </span>
            {!playing ? (
              <button className="play-button" onClick={handlePlay}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="5,3 19,12 5,21"/>
                </svg>
                Play sequence
              </button>
            ) : (
              <button className="play-button stop" onClick={handleStop}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <rect x="6" y="4" width="4" height="16"/>
                  <rect x="14" y="4" width="4" height="16"/>
                </svg>
                Stop
              </button>
            )}
          </div>

          <div className="flashcard">
            <span className="flashcard-word">
              {signWords[currentCard].replace('_', ' ').toUpperCase()}
            </span>
          </div>

          {/* Word strip */}
          <div className="flashcard-strip">
            {signWords.map((word, i) => (
              <button
                key={i}
                className={`strip-word ${i === currentCard ? 'strip-word-active' : ''}`}
                onClick={() => { setCurrentCard(i); setPlaying(false) }}
              >
                {word.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>
      )}

      {signWords.length === 0 && !loading && !error && (
        <div className="empty-state">
          <span className="empty-icon">&#128070;</span>
          <p>Enter a sentence above to see it as sign words</p>
        </div>
      )}
    </div>
  )
}
