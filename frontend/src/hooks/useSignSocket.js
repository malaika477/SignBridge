/**
 * useSignSocket.js
 * ----------------
 * Manages the WebSocket connection to the FastAPI backend for real-time
 * sign recognition. Sends landmark vectors, receives word/sentence/error events.
 *
 * Server message types:
 *   { type: "word", word, confidence, buffer }
 *   { type: "composing", words }
 *   { type: "sentence", text, words }
 *   { type: "error", message }
 */
import { useRef, useEffect, useState, useCallback } from 'react'

// Auto-detect WebSocket URL based on current page origin
function getWsUrl() {
  const { protocol, host } = window.location
  // In local dev (Vite dev server on 5173), connect to backend on 8001
  if (host.includes('localhost:5173') || host.includes('127.0.0.1:5173')) {
    return 'ws://localhost:8001/ws/recognize'
  }
  // In deployment, use same host with wss:// (secure WebSocket)
  const wsProtocol = protocol === 'https:' ? 'wss:' : 'ws:'
  return `${wsProtocol}//${host}/ws/recognize`
}

const WS_URL = getWsUrl()
const RECONNECT_DELAY_MS = 3000

export function useSignSocket() {
  const wsRef = useRef(null)
  const reconnectTimer = useRef(null)

  const [connected, setConnected] = useState(false)
  const [currentWord, setCurrentWord] = useState(null)
  const [confidence, setConfidence] = useState(0)
  const [wordBuffer, setWordBuffer] = useState([])
  const [sentence, setSentence] = useState(null)
  const [isComposing, setIsComposing] = useState(false)
  const [error, setError] = useState(null)

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(WS_URL)

      ws.onopen = () => {
        setConnected(true)
        setError(null)
      }

      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data)

        switch (msg.type) {
          case 'word':
            setCurrentWord(msg.word)
            setConfidence(msg.confidence)
            setWordBuffer(msg.buffer)
            setError(null)
            break

          case 'composing':
            setIsComposing(true)
            setError(null)
            break

          case 'sentence':
            setSentence(msg.text)
            setIsComposing(false)
            setWordBuffer([])
            setError(null)
            break

          case 'error':
            setError(msg.message)
            setIsComposing(false)
            break

          default:
            break
        }
      }

      ws.onclose = () => {
        setConnected(false)
        // Auto-reconnect after delay
        reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY_MS)
      }

      ws.onerror = () => {
        ws.close()
      }

      wsRef.current = ws
    } catch {
      reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY_MS)
    }
  }, [])

  useEffect(() => {
    connect()
    return () => {
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [connect])

  const sendLandmarks = useCallback((landmarks) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ landmarks }))
    }
  }, [])

  const clearSentence = useCallback(() => {
    setSentence(null)
    setIsComposing(false)
    setCurrentWord(null)
    setWordBuffer([])
  }, [])

  return {
    connected,
    currentWord,
    confidence,
    wordBuffer,
    sentence,
    isComposing,
    error,
    sendLandmarks,
    clearSentence,
  }
}
