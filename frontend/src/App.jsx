/**
 * App.jsx
 * -------
 * Main layout for SignBridge web UI with two modes:
 * - Forward: Sign → Text/Speech (webcam → sign recognition → LLM sentence → TTS)
 * - Reverse: Text/Speech → Sign (type/speak → LLM breaks into sign words → flashcards)
 */
import { useState } from 'react'
import WebcamView from './components/WebcamView'
import DetectedSigns from './components/DetectedSigns'
import SentenceOutput from './components/SentenceOutput'
import ReverseMode from './components/ReverseMode'
import { useSignSocket } from './hooks/useSignSocket'

export default function App() {
  const [activeTab, setActiveTab] = useState('forward')

  const {
    connected,
    currentWord,
    confidence,
    wordBuffer,
    sentence,
    isComposing,
    error,
    sendLandmarks,
    clearSentence,
  } = useSignSocket()

  const handleLandmarks = (landmarks) => {
    sendLandmarks(landmarks)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">SignBridge</h1>
        <p className="app-subtitle">Real-time sign language interpreter</p>
        <div className={`connection-badge ${connected ? 'connected' : 'disconnected'}`}>
          {connected ? 'Connected' : 'Connecting...'}
        </div>

        {/* Tab toggle */}
        <div className="tab-bar">
          <button
            className={`tab-button ${activeTab === 'forward' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('forward')}
          >
            Sign → Text
          </button>
          <button
            className={`tab-button ${activeTab === 'reverse' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('reverse')}
          >
            Speech/Text → Sign Words
          </button>
        </div>
      </header>

      <main className="app-main">
        {activeTab === 'forward' ? (
          <>
            <section className="left-panel">
              <WebcamView onLandmarks={handleLandmarks} />
            </section>

            <section className="right-panel">
              <DetectedSigns
                wordBuffer={wordBuffer}
                currentWord={currentWord}
                confidence={confidence}
                connected={connected}
              />

              <SentenceOutput
                sentence={sentence}
                isComposing={isComposing}
                error={error}
              />

              {sentence && (
                <button className="clear-button" onClick={clearSentence}>
                  Clear
                </button>
              )}
            </section>
          </>
        ) : (
          <section className="reverse-panel">
            <ReverseMode />
          </section>
        )}
      </main>

      <footer className="app-footer">
        <p>SignBridge &mdash; Alibaba Cloud AI Hackathon Pakistan 2026</p>
      </footer>
    </div>
  )
}
