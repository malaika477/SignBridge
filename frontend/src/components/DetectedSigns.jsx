/**
 * DetectedSigns.jsx
 * -----------------
 * Displays the word buffer as styled chips. Highlights the most recently
 * detected word. Shows a placeholder when no signs have been detected.
 */
export default function DetectedSigns({ wordBuffer, currentWord, confidence, connected }) {
  return (
    <div className="detected-signs">
      <h3 className="section-label">Detected Signs</h3>

      {!connected && (
        <div className="status-badge status-disconnected">
          Disconnected from server
        </div>
      )}

      {wordBuffer.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">&#9995;</span>
          <p>No sign detected yet</p>
          <p className="empty-hint">Sign a word from the trained vocabulary</p>
        </div>
      ) : (
        <div className="word-chips">
          {wordBuffer.map((word, i) => (
            <span
              key={`${word}-${i}`}
              className={`word-chip ${word === currentWord && i === wordBuffer.length - 1 ? 'word-chip-latest' : ''}`}
            >
              {word.replace('_', ' ')}
            </span>
          ))}
        </div>
      )}

      {currentWord && confidence > 0 && (
        <div className="confidence-bar">
          <span className="confidence-label">
            Confidence: {Math.round(confidence * 100)}%
          </span>
          <div className="confidence-track">
            <div
              className="confidence-fill"
              style={{ width: `${Math.round(confidence * 100)}%` }}
            />
          </div>
        </div>
      )}
    </div>
  )
}
