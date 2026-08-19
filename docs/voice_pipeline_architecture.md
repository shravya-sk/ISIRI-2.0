# ISIRI 2.0 Voice Pipeline Architecture

## Overview

The ISIRI 2.0 voice pipeline is designed as a modular, extensible system that follows SOLID principles. The architecture separates concerns into distinct modules that can be independently developed, tested, and replaced.

## Module Responsibilities

### 1. Assistant (`assistant.py`)

**Responsibilities:**
- Orchestrate the complete voice interaction pipeline
- Manage conversation state and context
- Coordinate between voice components and AI engine
- Handle errors and fallback mechanisms
- Support multi-language processing (Tulu-English)
- Manage lifecycle of all voice components

**Design Principles:**
- Single Responsibility: Only orchestrates, doesn't implement voice logic
- Open/Closed: Extensible for new voice features
- Dependency Inversion: Depends on abstractions, not concrete implementations

---

### 2. Speech-to-Text (`speech_to_text.py`)

**Responsibilities:**
- Convert audio input to text using speech recognition
- Support multiple backends (Whisper, Google, etc.)
- Handle multi-language transcription
- Provide audio preprocessing (resampling, noise reduction)
- Support both file-based and real-time transcription
- Manage model loading and caching

**Sub-components:**
- `SpeechToTextEngine`: Main interface for STT operations
- `WhisperEngine`: Whisper-specific implementation
- `AudioPreprocessor`: Audio normalization and preprocessing

**Design Principles:**
- Strategy Pattern: Multiple STT backends interchangeable
- Factory Pattern: Model creation and management
- Single Responsibility: Only handles speech recognition

---

### 3. Text-to-Speech (`text_to_speech.py`)

**Responsibilities:**
- Convert text responses to audio output
- Support multiple TTS engines (pyttsx3, gTTS, custom)
- Handle voice customization (rate, volume, voice selection)
- Support multi-language synthesis
- Manage audio playback control
- Save audio to file when needed

**Sub-components:**
- `TextToSpeechEngine`: Main interface for TTS operations
- `Pyttsx3Engine`: pyttsx3-specific implementation
- `AudioPlayer`: Audio playback and device management

**Design Principles:**
- Strategy Pattern: Multiple TTS backends interchangeable
- Observer Pattern: Playback state notifications
- Single Responsibility: Only handles speech synthesis

---

### 4. Wake Word Detection (`wake_word.py`)

**Responsibilities:**
- Detect wake word "Hey iSiri" in audio stream
- Continuous audio monitoring with low latency
- Support multiple wake words
- Reduce false positives with debouncing
- Provide callback mechanism for detection events
- Support multiple detection engines

**Sub-components:**
- `WakeWordDetector`: Main detection orchestrator
- `KeywordSpottingEngine`: Porcupine/Myrtle-based detection
- `SpeechRecognitionDetector`: STT-based detection

**Design Principles:**
- Observer Pattern: Callback on wake word detection
- Strategy Pattern: Multiple detection engines
- Single Responsibility: Only handles wake word detection

---

### 5. Recorder (`recorder.py`)

**Responsibilities:**
- Capture audio from microphone
- Manage audio stream lifecycle
- Support different audio formats and sample rates
- Handle hardware audio devices
- Provide audio chunks for processing
- Support Raspberry Pi audio hardware

**Sub-components:**
- `AudioRecorder`: Main recording interface
- `StreamManager`: Audio stream lifecycle
- `DeviceManager`: Audio device enumeration and selection

**Design Principles:**
- Factory Pattern: Device creation and management
- Single Responsibility: Only handles audio capture
- Hardware Abstraction: Supports multiple audio backends

---

### 6. Voice Activity Detection (`vad.py`)

**Responsibilities:**
- Detect speech vs silence in audio stream
- Automatically stop recording after silence
- Provide speech segments for processing
- Configurable sensitivity and timeout
- Support multiple VAD algorithms
- Optimize for different environments

**Sub-components:**
- `VADDetector`: Main VAD interface
- `SileroVAD`: Silero-based VAD implementation
- `WebRTCVAD`: WebRTC VAD implementation
- `SpeechSegmenter`: Segment audio into speech chunks

**Design Principles:**
- Strategy Pattern: Multiple VAD algorithms
- Observer Pattern: Notify on speech events
- Single Responsibility: Only handles speech detection

---

## Module Call Hierarchy

```
Assistant (Orchestrator)
├── WakeWordDetector (Optional - for continuous listening)
│   └── KeywordSpottingEngine / SpeechRecognitionDetector
│
├── Recorder (Audio capture)
│   ├── StreamManager
│   └── DeviceManager
│
├── VADDetector (Optional - for automatic stop)
│   ├── SileroVAD / WebRTCVAD
│   └── SpeechSegmenter
│
├── SpeechToTextEngine (Transcription)
│   ├── WhisperEngine
│   └── AudioPreprocessor
│
├── AI Engine (Intent, Entity, Plan, Execute)
│   ├── IntentDetector
│   ├── EntityExtractor
│   ├── Planner
│   └── PluginExecutor
│
└── TextToSpeechEngine (Response)
    ├── Pyttsx3Engine
    └── AudioPlayer
```

## Data Flow

### Standard Conversation Flow

```
1. Wake Word Detection (Optional)
   Audio Stream → WakeWordDetector → Detection Event
                                    ↓
                            Assistant.trigger()

2. Recording Phase
   Assistant → Recorder.start()
   Microphone → Recorder → Audio Chunks
                ↓
            VADDetector (Optional)
                ↓
            Speech Detection → Recorder.stop()

3. Transcription Phase
   Recorder → Audio Data → SpeechToTextEngine.transcribe()
                              ↓
                          AudioPreprocessor
                              ↓
                          WhisperEngine
                              ↓
                          Transcribed Text

4. AI Processing Phase
   Transcribed Text → IntentDetector → Intent
                     → EntityExtractor → Entities
                     → Planner → Plan
                     → PluginExecutor → Response

5. Response Phase
   Response → TextToSpeechEngine.speak()
              → Pyttsx3Engine → Audio Data
              → AudioPlayer → Speaker Output
```

### Continuous Listening Flow

```
Background Thread:
Audio Stream → WakeWordDetector (Continuous)
                    ↓
                Detection Event
                    ↓
            Assistant.trigger()
                    ↓
            [Standard Conversation Flow]
```

## Sequence Diagram

```
User          Assistant      WakeWord      Recorder      VAD          STT          AI Engine      TTS
 │                │              │            │            │            │               │            │
 │ Speak "Hey iSiri"           │            │            │            │               │            │
 ├───────────────>│             │            │            │            │               │            │
 │                │────────────>│            │            │            │               │            │
 │                │<────────────│ (Detected) │            │            │               │            │
 │                │────────────>│            │            │            │               │            │
 │                │             │            │            │            │               │            │
 │ Speak Command  │             │            │            │            │               │            │
 ├───────────────>│────────────>│            │            │            │               │            │
 │                │             ├────────────>│            │            │               │            │
 │                │             │            ├────────────>│            │               │            │
 │                │             │            │<────────────│ (Speech)  │               │            │
 │                │             │            ├────────────>│            │               │            │
 │                │             │            │<────────────│ (Silence) │               │            │
 │                │             │<────────────│ (Stop)     │            │               │            │
 │                │<────────────│ (Audio)     │            │            │               │            │
 │                │────────────────────────>│            │            │               │            │
 │                │             │            │            ├────────────>│               │            │
 │                │             │            │            │<────────────│ (Text)        │            │
 │                │────────────────────────────────────────────────────>│               │            │
 │                │             │            │            │            ├──────────────>│            │
 │                │             │            │            │            ├──────────────>│            │
 │                │             │            │            │            ├──────────────>│            │
 │                │             │            │            │            │<──────────────│ (Response) │
 │                │             │            │            │            │<──────────────│ (Plan)     │
 │                │             │            │            │            │<──────────────│ (Result)   │
 │                │──────────────────────────────────────────────────────────────────>│            │
 │                │             │            │            │            │               ├───────────>│
 │                │             │            │            │            │               │<───────────│
 │                │<──────────────────────────────────────────────────────────────────│ (Audio)    │
 │<───────────────│ (Response)  │            │            │            │               │            │
 │                │             │            │            │            │               │            │
```

## Future Integration Points

### 1. Whisper Integration

**Location:** `speech_to_text.py` → `WhisperEngine`

**Integration Points:**
- Model loading in `WhisperEngine.load_model()`
- Transcription in `WhisperEngine.transcribe()`
- Multi-language support in `WhisperEngine.set_language()`
- Timestamp generation in `WhisperEngine.transcribe_with_timestamps()`

**Benefits:**
- Offline speech recognition
- Multi-language support (Tulu, English)
- High accuracy transcription
- Word-level timestamps for alignment

---

### 2. OpenWakeWord Integration

**Location:** `wake_word.py` → `KeywordSpottingEngine`

**Integration Points:**
- Model loading in `KeywordSpottingEngine.load_model()`
- Frame processing in `KeywordSpottingEngine.process_frame()`
- Multi-keyword support in `WakeWordDetector.add_wake_word()`

**Benefits:**
- Low-latency wake word detection
- Low CPU usage for continuous listening
- Custom wake word training
- Raspberry Pi optimized

---

### 3. Voice Activity Detection Integration

**Location:** `vad.py` → `VADDetector`

**Integration Points:**
- VAD algorithm selection in `VADDetector.__init__()`
- Speech detection in `VADDetector.detect()`
- Speech segmentation in `SpeechSegmenter.segment()`
- Integration with Recorder in `Recorder.stop_on_silence()`

**Benefits:**
- Automatic recording stop after silence
- Reduced false positives
- Better audio quality
- Optimized processing

**Supported Algorithms:**
- Silero VAD (neural network, high accuracy)
- WebRTC VAD (lightweight, fast)
- Custom VAD models

---

### 4. Translation Model Integration

**Location:** New module `translation.py` or integrated in `assistant.py`

**Integration Points:**
- Between STT and AI Engine for input translation
- Between AI Engine and TTS for output translation
- Language detection and switching
- Context-aware translation

**Architecture:**
```
STT → Translation (Tulu → English) → AI Engine → Translation (English → Tulu) → TTS
```

**Benefits:**
- Seamless Tulu-English conversation
- Context-aware translations
- Custom domain translations
- Support for multiple language pairs

---

### 5. Raspberry Pi Hardware Integration

**Location:** Multiple modules

**Integration Points:**

**Recorder (`recorder.py`):**
- USB microphone support via `DeviceManager`
- I2S microphone support for HATs
- Audio device configuration for Pi hardware

**Text-to-Speech (`text_to_speech.py`):**
- `AudioPlayer.set_device()` for Pi audio output
- 3.5mm jack, HDMI, USB audio support
- Hardware audio mixer control

**Wake Word (`wake_word.py`):**
- Optimized models for Pi CPU/ARM
- Hardware acceleration if available
- Low-power continuous listening

**General (`assistant.py`):**
- GPIO integration for LED indicators
- Button triggers for manual activation
- Hardware status monitoring

**Hardware Abstraction Layer:**
```python
class HardwareManager:
    def get_audio_devices() -> list
    def set_led_state(pin: str, state: bool) -> None
    def read_button_state(pin: str) -> bool
    def get_system_info() -> dict
```

---

## SOLID Principles Application

### Single Responsibility Principle
- Each module has one clear responsibility
- `assistant.py`: Orchestration only
- `speech_to_text.py`: Speech recognition only
- `text_to_speech.py`: Speech synthesis only
- `wake_word.py`: Wake word detection only
- `recorder.py`: Audio capture only
- `vad.py`: Speech detection only

### Open/Closed Principle
- Open for extension: New STT/TTS engines can be added
- Closed for modification: Existing code doesn't need changes
- Strategy pattern for interchangeable implementations
- Configuration-based engine selection

### Liskov Substitution Principle
- All STT engines implement common interface
- All TTS engines implement common interface
- All VAD engines implement common interface
- Subclasses can replace parent without breaking functionality

### Interface Segregation Principle
- Small, focused interfaces for each module
- Clients only depend on methods they use
- Separate interfaces for recording, playback, detection
- No fat interfaces with unused methods

### Dependency Inversion Principle
- High-level modules depend on abstractions
- `Assistant` depends on `STTInterface`, not `WhisperEngine`
- Concrete implementations injected via configuration
- Easy to swap implementations for testing

---

## Extension Points

### Adding New STT Engine
1. Implement `STTInterface` in new class
2. Add to `SpeechToTextEngine._load_engine()`
3. Update configuration options
4. No changes to other modules needed

### Adding New TTS Engine
1. Implement `TTSInterface` in new class
2. Add to `TextToSpeechEngine._load_engine()`
3. Update configuration options
4. No changes to other modules needed

### Adding New Wake Word
1. Add to `WakeWordConfig.keywords`
2. Train or download model
3. Load in `KeywordSpottingEngine`
4. No architecture changes needed

### Adding New Language
1. Add language code to configuration
2. Ensure STT/TTS models support it
3. Add translation model if needed
4. Update language detection logic

### Adding Hardware Support
1. Implement hardware-specific driver
2. Add to `HardwareManager`
3. Configure device selection
4. No changes to voice logic needed

---

## Error Handling Strategy

### Graceful Degradation
- STT failure: Fallback to text input
- TTS failure: Display text response
- Wake word failure: Manual trigger button
- VAD failure: Manual stop button

### Retry Mechanisms
- Transcription retry with different backend
- TTS retry with different voice
- Recording retry on device error

### Logging
- Structured logging for all voice operations
- Error context preservation
- Performance metrics collection

---

## Performance Considerations

### Model Loading
- Lazy loading of models on first use
- Model caching in memory
- Background preloading for critical models

### Real-time Processing
- Chunked audio processing
- Pipeline parallelization
- Non-blocking I/O operations

### Resource Management
- Memory cleanup after operations
- Audio buffer size optimization
- CPU usage monitoring

---

## Testing Strategy

### Unit Tests
- Each module tested independently
- Mock dependencies for isolation
- Test all error paths

### Integration Tests
- Test module interactions
- Test data flow between modules
- Test with real audio hardware

### End-to-End Tests
- Complete conversation flows
- Multi-turn dialogues
- Error recovery scenarios

---

## Configuration Management

### Centralized Config
```python
@dataclass
class VoiceConfig:
    stt: STTConfig
    tts: TTSConfig
    wake_word: WakeWordConfig
    recorder: RecorderConfig
    vad: VADConfig
    hardware: HardwareConfig
```

### Environment-Specific Configs
- Development: Debug logging, mock engines
- Production: Optimized models, hardware acceleration
- Testing: Mock implementations, deterministic behavior

---

## Deployment Considerations

### Docker Support
- Containerized voice components
- Hardware passthrough for audio devices
- Model volume mounting

### Raspberry Pi Deployment
- ARM-optimized models
- Reduced memory footprint
- Hardware-specific configurations

### Cloud Deployment
- GPU support for STT/TTS
- Scalable architecture
- Load balancing for multiple users
