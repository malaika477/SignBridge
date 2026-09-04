/**
 * WebcamView.jsx
 * --------------
 * Displays the webcam feed with MediaPipe hand skeleton overlay.
 * Shows error state if camera access is denied.
 */
import { useEffect, useRef } from 'react'
import { useHandTracking } from '../hooks/useHandTracking'

export default function WebcamView({ onLandmarks }) {
  const { canvasRef, cameraError, handsDetected, status, setOnResults } = useHandTracking()
  const onLandmarksRef = useRef(onLandmarks)
  onLandmarksRef.current = onLandmarks

  useEffect(() => {
    setOnResults((landmarks) => {
      if (onLandmarksRef.current) onLandmarksRef.current(landmarks)
    })
  }, [setOnResults])

  if (cameraError) {
    return (
      <div className="webcam-view webcam-error">
        <div className="error-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/>
            <circle cx="12" cy="13" r="4"/>
            <line x1="1" y1="1" x2="23" y2="23"/>
          </svg>
        </div>
        <p className="error-title">Camera Access Required</p>
        <p className="error-detail">{cameraError}</p>
        <p className="error-hint">Please allow camera access in your browser settings.</p>
      </div>
    )
  }

  const statusMessages = {
    'loading-mediapipe': 'Loading hand tracking...',
    'requesting-camera': 'Waiting for camera permission...',
    'starting': 'Starting camera...',
  }

  return (
    <div className={`webcam-view ${handsDetected ? 'hands-detected' : ''}`}>
      <canvas ref={canvasRef} className="webcam-canvas" />
      {!handsDetected && status !== 'running' && statusMessages[status] && (
        <div className="no-hands-overlay">
          <p>{statusMessages[status]}</p>
        </div>
      )}
      {!handsDetected && status === 'running' && (
        <div className="no-hands-overlay">
          <p>Show your hands to the camera</p>
        </div>
      )}
    </div>
  )
}
