import { useState, useEffect } from 'react'
import { getBackendMessage } from './api'
import './App.css'

function App() {
  const [inputText, setInputText] = useState('')
  const [backendMessage, setBackendMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [transcription, setTranscription] = useState("");
  const [intent, setIntent] = useState("");
const [entities, setEntities] = useState({});
  const [recordingStatus, setRecordingStatus] = useState('ready')
  const [mediaRecorder, setMediaRecorder] = useState(null)
  const [audioChunks, setAudioChunks] = useState([])
  const [audioBlob, setAudioBlob] = useState(null)
  const [uploadStatus, setUploadStatus] = useState(null)
  const [reply, setReply] = useState("");

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
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    const recorder = new MediaRecorder(stream);

    const chunks = [];   // <-- Local array

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    };

    recorder.onstop = () => {
      const blob = new Blob(chunks, { type: "audio/webm" });

      console.log("Blob size:", blob.size);

      setAudioBlob(blob);

      stream.getTracks().forEach(track => track.stop());

      uploadAudio(blob);
    };

    recorder.start();

    setMediaRecorder(recorder);
    setRecordingStatus("recording");

  } catch (err) {
    console.error(err);
  }
};

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop()
      setRecordingStatus('complete')
    }
  }

  const handleMicrophoneClick = () => {
    if (recordingStatus === 'ready' || recordingStatus === 'complete') {
      setAudioChunks([])
      setAudioBlob(null)
      setUploadStatus(null)
      startRecording()
    } else if (recordingStatus === 'recording') {
      stopRecording()
    }
  }

  const uploadAudio = async (blob) => {
  try {
    console.log("Uploading blob size:", blob.size);
    const formData = new FormData();
    formData.append("audio", blob, "recording.webm");

    const response = await fetch("http://127.0.0.1:8000/upload-audio", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    console.log("Backend Response:", data);

    if (response.ok && data.success) {
    setUploadStatus("Upload Successful ✅");

    setTranscription(data.transcription);
    setIntent(data.intent);
    setEntities(data.entities);
    setReply(data.reply);

    console.log("Intent:", data.intent);
    console.log("Entities:", data.entities);
  } else {
      setUploadStatus("Upload Failed ❌");
      console.log(data);
    }
  } catch (err) {
    console.error(err);
    setUploadStatus("Upload Failed ❌");
  }
};

  return (
    <div className="landing-page">
      <header className="header">
        <h1 className="title">ISIRI 2.0</h1>
        <p className="subtitle">Intelligent Speech Interface for Regional Interaction</p>
        <div className="backend-status">
          {loading ? (
            <p className="status-text loading">Connecting to backend...</p>
          ) : error ? (
            <p className="status-text error">{error}</p>
          ) : (
            <p className="status-text success">{backendMessage}</p>
          )}
        </div>
      </header>

      <main className="main-content">
        <div className="interaction-area">
          <button 
            className="microphone-button" 
            aria-label="Microphone"
            onClick={handleMicrophoneClick}
          >
            <svg className="microphone-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 1C9.23858 1 7 3.23858 7 6V12C7 14.7614 9.23858 17 12 17C14.7614 17 17 14.7614 17 12V6C17 3.23858 14.7614 1 12 1Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M12 19C8.13401 19 5 15.866 5 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M19 12C19 15.866 15.866 19 12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M12 23V19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M8 23H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          <div className="recording-status">
            {transcription && (
  <div style={{ marginTop: "20px" }}>
    <h3>Transcription</h3>
    <p>{transcription}</p>
  </div>
)}

{reply && (
  <div style={{ marginTop: "20px" }}>
    <h3>ISIRI Response</h3>
    <p>{reply}</p>
  </div>
)}

{intent && (
  <div style={{ marginTop: "20px" }}>
    <h3>Intent</h3>
    <p>{intent}</p>
  </div>
)}

{Object.keys(entities).length > 0 && (
  <div style={{ marginTop: "20px" }}>
    <h3>Entities</h3>
    <pre>{JSON.stringify(entities, null, 2)}</pre>
  </div>
)}
            {recordingStatus === 'ready' && (
              <p className="recording-status-text ready">Ready</p>
            )}
            {recordingStatus === 'recording' && (
              <p className="recording-status-text recording">Recording...</p>
            )}
            {recordingStatus === 'complete' && uploadStatus && (
              <p className="recording-status-text complete">{uploadStatus}</p>
            )}
            {recordingStatus === 'complete' && !uploadStatus && (
              <p className="recording-status-text complete">Recording Complete</p>
            )}
          </div>

          <div className="input-area">
            <input
              type="text"
              className="text-input"
              placeholder="Type your message..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />
            <button className="send-button">Send</button>
          </div>
        </div>

        <section className="recent-conversations">
          <h2 className="section-title">Recent Conversations</h2>
          <div className="conversation-cards">
            <div className="conversation-card">
              <h3 className="card-title">Weather Inquiry</h3>
              <p className="card-preview">"What's the weather like today?"</p>
              <span className="card-time">2 hours ago</span>
            </div>
            <div className="conversation-card">
              <h3 className="card-title">Translation Request</h3>
              <p className="card-preview">"Translate this to Spanish..."</p>
              <span className="card-time">Yesterday</span>
            </div>
            <div className="conversation-card">
              <h3 className="card-title">General Question</h3>
              <p className="card-preview">"How does the system work?"</p>
              <span className="card-time">3 days ago</span>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
