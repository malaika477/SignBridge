/**
 * TTSButton.jsx
 * -------------
 * Speaks the given text using the browser's built-in SpeechSynthesis API.
 * No server call needed — works offline once the page is loaded.
 */
import { useState, useCallback } from 'react'

export default function TTSButton({ text }) {
  const [speaking, setSpeaking] = useState(false)

  const handleSpeak = useCallback(() => {
    if (!text || !('speechSynthesis' in window)) return

    // Cancel any ongoing speech
    window.speechSynthesis.cancel()

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 0.9
    utterance.pitch = 1.0
    utterance.lang = 'en-US'

    utterance.onstart = () => setSpeaking(true)
    utterance.onend = () => setSpeaking(false)
    utterance.onerror = () => setSpeaking(false)

    window.speechSynthesis.speak(utterance)
  }, [text])

  if (!text) return null

  const ttsSupported = typeof window !== 'undefined' && 'speechSynthesis' in window

  return (
    <button
      className={`tts-button ${speaking ? 'tts-speaking' : ''}`}
      onClick={handleSpeak}
      disabled={!ttsSupported || speaking}
      title={ttsSupported ? 'Read aloud' : 'Text-to-speech not supported in this browser'}
      aria-label="Read sentence aloud"
    >
      {speaking ? (
        <>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M6 4h4l6 6V4h2v16h-2v-6l-6 6H6V4zm10 4.5a4 4 0 010 7"/>
          </svg>
          <span>Speaking...</span>
        </>
      ) : (
        <>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M11 5L6 9H2v6h4l5 4V5z"/>
            <path d="M15.54 8.46a5 5 0 010 7.07"/>
            <path d="M19.07 4.93a10 10 0 010 14.14"/>
          </svg>
          <span>Read Aloud</span>
        </>
      )}
    </button>
  )
}
