/**
 * SentenceOutput.jsx
 * ------------------
 * Displays the composed sentence from the LLM. Shows a loading spinner
 * while the sentence is being composed, and error state if the LLM fails.
 */
import TTSButton from './TTSButton'

export default function SentenceOutput({ sentence, isComposing, error }) {
  return (
    <div className="sentence-output">
      <h3 className="section-label">Translated Sentence</h3>

      {isComposing && (
        <div className="composing-state">
          <div className="spinner" />
          <span>Composing sentence...</span>
        </div>
      )}

      {error && !isComposing && (
        <div className="error-state">
          <span className="error-icon">&#9888;</span>
          <p className="error-text">
            {error.length > 120 ? error.slice(0, 120) + '...' : error}
          </p>
        </div>
      )}

      {!isComposing && !error && sentence && (
        <div className="sentence-result">
          <p className="sentence-text">{sentence}</p>
          <TTSButton text={sentence} />
        </div>
      )}

      {!isComposing && !error && !sentence && (
        <div className="empty-sentence">
          <p>Sign 2-3 words, then pause to generate a sentence</p>
        </div>
      )}
    </div>
  )
}
