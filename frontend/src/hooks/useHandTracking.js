/**
 * useHandTracking.js
 * ------------------
 * Initializes MediaPipe Hands in the browser and extracts hand landmarks
 * from each webcam frame using native getUserMedia.
 *
 * MediaPipe is loaded via CDN scripts in index.html (the npm package has
 * broken ES module exports). We poll for window.Hands to become available.
 *
 * Landmark extraction produces the exact same 126-element vector as
 * data_collection.py:extract_two_hand_features():
 *   - Hands sorted left-to-right by wrist x position
 *   - Each hand: 21 landmarks x 3 coords (x, y, z) = 63 floats
 *   - Padded with zeros if only 1 hand visible
 *   - Total: always 126 floats
 */
import { useRef, useEffect, useCallback, useState } from 'react'

const HAND_CONNECTIONS = [
  [0,1],[1,2],[2,3],[3,4],
  [0,5],[5,6],[6,7],[7,8],
  [5,9],[9,10],[10,11],[11,12],
  [9,13],[13,14],[14,15],[15,16],
  [13,17],[17,18],[18,19],[19,20],
  [0,17],
]

function extractTwoHandFeatures(multiHandLandmarks) {
  const handsData = multiHandLandmarks.map(lm => ({
    wristX: lm[0].x,
    flat: lm.flatMap(p => [p.x, p.y, p.z]),
  }))
  handsData.sort((a, b) => a.wristX - b.wristX)

  const features = []
  for (const hand of handsData) {
    features.push(...hand.flat)
  }
  while (features.length < 126) {
    features.push(0.0)
  }
  return features.slice(0, 126)
}

export function useHandTracking() {
  const canvasRef = useRef(null)
  const videoRef = useRef(null)
  const handsRef = useRef(null)
  const streamRef = useRef(null)
  const animFrameRef = useRef(null)
  const onResultsCb = useRef(null)
  const pollRef = useRef(null)

  const [cameraError, setCameraError] = useState(null)
  const [handsDetected, setHandsDetected] = useState(false)

  const setOnResults = useCallback((cb) => {
    onResultsCb.current = cb
  }, [])

  useEffect(() => {
    let cancelled = false

    // Poll for MediaPipe CDN to finish loading
    function waitForMediaPipe() {
      if (cancelled) return
      if (typeof window.Hands === 'function' &&
          typeof window.drawConnectors === 'function' &&
          typeof window.drawLandmarks === 'function') {
        initCamera()
      } else {
        pollRef.current = setTimeout(waitForMediaPipe, 300)
      }
    }

    async function initCamera() {
      // 1. Get camera permission
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 640, height: 480, facingMode: 'user' },
        })
        if (cancelled) { stream.getTracks().forEach(t => t.stop()); return }
        streamRef.current = stream
      } catch (err) {
        if (!cancelled) {
          if (err.name === 'NotAllowedError') {
            setCameraError('Camera permission denied. Click the camera icon in your address bar and allow access.')
          } else if (err.name === 'NotFoundError') {
            setCameraError('No camera found. Please connect a webcam.')
          } else {
            setCameraError(`Camera error: ${err.message}`)
          }
        }
        return
      }

      // 2. Create hidden video element
      const video = document.createElement('video')
      video.srcObject = stream
      video.setAttribute('playsinline', '')
      video.muted = true
      video.width = 640
      video.height = 480
      videoRef.current = video

      await video.play()
      if (cancelled) return

      // 3. Initialize MediaPipe Hands
      const hands = new window.Hands({
        locateFile: (file) =>
          `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
      })

      hands.setOptions({
        maxNumHands: 2,
        modelComplexity: 1,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.5,
      })

      hands.onResults((results) => {
        const canvas = canvasRef.current
        if (!canvas) return

        const ctx = canvas.getContext('2d')
        canvas.width = video.videoWidth || 640
        canvas.height = video.videoHeight || 480

        // Draw mirrored camera feed
        ctx.save()
        ctx.translate(canvas.width, 0)
        ctx.scale(-1, 1)
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
        ctx.restore()

        if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
          setHandsDetected(true)

          for (const landmarks of results.multiHandLandmarks) {
            window.drawConnectors(ctx, landmarks, HAND_CONNECTIONS, {
              color: '#00FF88',
              lineWidth: 3,
            })
            window.drawLandmarks(ctx, landmarks, {
              color: '#FF4444',
              lineWidth: 1,
              radius: 3,
            })
          }

          const features = extractTwoHandFeatures(results.multiHandLandmarks)
          if (onResultsCb.current) {
            onResultsCb.current(features)
          }
        } else {
          setHandsDetected(false)
        }
      })

      handsRef.current = hands

      // 4. Process frames
      async function processFrame() {
        if (cancelled || !handsRef.current || !videoRef.current) return
        try {
          await handsRef.current.send({ image: videoRef.current })
        } catch {
          // Ignore transient send errors
        }
        if (!cancelled) {
          animFrameRef.current = requestAnimationFrame(processFrame)
        }
      }
      processFrame()
    }

    waitForMediaPipe()

    return () => {
      cancelled = true
      if (pollRef.current) clearTimeout(pollRef.current)
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current)
      if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop())
      if (handsRef.current) handsRef.current.close()
    }
  }, [])

  return { canvasRef, cameraError, handsDetected, setOnResults }
}
