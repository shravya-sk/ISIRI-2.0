import { useState, useEffect } from 'react'
import { getBackendMessage } from './api'
import './App.css'

function App() {
  const [inputText, setInputText] = useState('')
  const [backendMessage, setBackendMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [transcription, setTranscription] = useState('')
  const [intent, setIntent] = useState('')
  const [entities, setEntities] = useState({})
  const [recordingStatus, setRecordingStatus] = useState('ready')
  const [mediaRecorder, setMediaRecorder] = useState(null)
  const [audioBlob, setAudioBlob] = useState(null)
  const [uploadStatus, setUploadStatus] = useState(null)
  const [reply, setReply] = useState('')
  const [link, setLink] = useState('')

  useEffect(() => {
    const fetchMessage = async () => {
      try {
        const data = await getBackendMessage()
        setBackendMessage(data.message)
      } catch (err) {
        setError('Failed to connect to backend')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchMessage()
  }, [])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true
      })

      const recorder = new MediaRecorder(stream)
      const chunks = []

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data)
        }
      }

      recorder.onstop = () => {
        const blob = new Blob(chunks, {
          type: 'audio/webm'
        })

        setAudioBlob(blob)

        stream.getTracks().forEach((track) => track.stop())

        uploadAudio(blob)
      }

      recorder.start()

      setMediaRecorder(recorder)
      setRecordingStatus('recording')
      setUploadStatus(null)

    } catch (err) {
      console.error(err)
      setError('Microphone permission is required.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop()
      setRecordingStatus('complete')
    }
  }

  const handleMicrophoneClick = () => {
    if (
      recordingStatus === 'ready' ||
      recordingStatus === 'complete'
    ) {
      setAudioBlob(null)
      setUploadStatus(null)
      startRecording()
    } else if (recordingStatus === 'recording') {
      stopRecording()
    }
  }

  const uploadAudio = async (blob) => {
    try {
      const formData = new FormData()

      formData.append(
        'audio',
        blob,
        'recording.webm'
      )

      const response = await fetch(
        'http://127.0.0.1:8000/upload-audio',
        {
          method: 'POST',
          body: formData
        }
      )

      const data = await response.json()

      console.log('Backend Response:', data)

      if (response.ok && data.success) {
        setUploadStatus('success')

        setTranscription(data.transcription || '')
        setIntent(data.intent || '')
        setEntities(data.entities || {})
        setReply(data.reply || '')
        setLink(data.link || '')

      } else {
        setUploadStatus('failed')
      }

    } catch (err) {
      console.error(err)
      setUploadStatus('failed')
    }
  }

  const handleSend = () => {
    if (!inputText.trim()) return

    // Your current backend is voice based.
    // We are keeping the text box as part of the UI for now.
    console.log('Text entered:', inputText)
  }

  return (
  <div className="app">

    {/* HEADER */}
    <header className="top-header">
      <div className="brand">
        <div className="brand-logo">
          <img src="/images/logo.png" alt="ISIRI Logo" />
        </div>

        <div>
          <h1>ISIRI 2.0</h1>
          <p>
            Intelligent Speech Interface
          </p>
        </div>
      </div>
    </header>

    {/* DECORATIVE IMAGES */}

    <img
      src="/images/roosters.png"
      alt=""
      className="decoration rooster"
    />

    <img
      src="/images/farmer-buffalo.png"
      alt=""
      className="decoration farmer"
    />

    <img
      src="/images/coconut.png"
      alt=""
      className="decoration coconut"
    />

    {/* MAIN CONTENT */}
    <main className="main-content">

      {/* MAIN ISIRI CARD */}
      <div className="isiri-card">

        {/* MICROPHONE */}
        <button
          className={`microphone-button ${
            recordingStatus === "recording" ? "recording-active" : ""
          }`}
          aria-label="Microphone"
          onClick={handleMicrophoneClick}
        >
          <img
            src="/images/mic.png"
            alt="Microphone"
            className="mic-image"
          />
        </button>

        {/* CONVERSATION */}

        {transcription && (
          <div className="message-block">
            <h3>You</h3>

            <div className="message user-message">
              {transcription}
            </div>
          </div>
        )}

        {reply && (
          <div className="message-block">
            <h3>ISIRI</h3>

            <div className="message isiri-message">
              <p>{reply}</p>

              {link && (
                <button
                  className="open-result"
                  onClick={() => window.open(link, "_blank")}
                >
                  Open Result →
                </button>
              )}
            </div>
          </div>
        )}

        {/* STATUS */}
        <div className="recording-status">

          {recordingStatus === "ready" && (
            <span className="status ready">
              Ready
            </span>
          )}

          {recordingStatus === "recording" && (
            <span className="status recording">
              <span className="status-dot"></span>
              Recording...
            </span>
          )}

          {recordingStatus === "complete" && uploadStatus && (
            <span className="status complete">
              <span className="status-dot"></span>
              Done
            </span>
          )}

        </div>

      </div>

      {/* TEXT INPUT */}
      <div className="input-area">

        <input
          type="text"
          className="text-input"
          placeholder="Type your message..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
        />

        <button className="send-button">
          Send
        </button>

      </div>

    </main>

  </div>
)
}
export default App