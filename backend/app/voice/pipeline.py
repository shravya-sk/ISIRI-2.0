"""
Voice Pipeline Orchestrator

This module provides the main orchestration class for the voice interaction pipeline.
The VoicePipeline class coordinates all voice components in a sequence to enable
complete voice interactions with the ISIRI assistant.

Responsibilities:
- Orchestrate the complete voice interaction pipeline
- Manage component lifecycle (initialization, shutdown)
- Coordinate between voice modules and AI engine
- Manage assistant state transitions
- Handle errors and provide fallback mechanisms
- Support both single-turn and continuous conversation modes

Design Principles:
- Single Responsibility: Only orchestrates, delegates business logic
- Open/Closed: Extensible for new voice components
- Dependency Inversion: Depends on abstractions (AIEngine, voice modules)

Usage:
    pipeline = VoicePipeline(config)
    pipeline.initialize()
    pipeline.run_once()  # For single interaction
    # or
    pipeline.run_conversation()  # For continuous listening
    pipeline.shutdown()
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

from ai_engine.engine import AIEngine, AIEngineConfig
from backend.app.voice.state import AssistantState, StateManager
from backend.app.voice.speech_to_text import SpeechToTextEngine, STTConfig
from backend.app.voice.text_to_speech import TextToSpeechEngine, TTSConfig
from ai_engine.translator import translate_to_english


logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for the voice pipeline."""
    wake_word_enabled: bool = False
    vad_enabled: bool = False
    translation_enabled: bool = False
    language: str = "en"  # "en" for English, "tu" for Tulu
    hardware_integration: bool = False


class VoicePipeline:
    """
    Main voice pipeline orchestrator.
    
    This class coordinates the complete voice interaction pipeline by delegating
    to specialized modules. It does not contain business logic.
    
    Pipeline Stages:
    #1. Wake word detection (optional) -> delegates to WakeWordDetector
    #2. Voice recording with VAD (optional) -> delegates to Recorder + VAD
    #3. Speech-to-text conversion -> delegates to SpeechToTextEngine
    #4. Translation (optional) -> delegates to TranslationModule
    #5. AI processing -> delegates to AIEngine
    #6. Text-to-speech -> delegates to TextToSpeechEngine
    
    State Management:
    - Uses StateManager to track and transition between states
    - All state changes are logged and can be monitored
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize the voice pipeline.
        
        Args:
            config: Pipeline configuration object
        """
        self.config = config or PipelineConfig()
        self.state_manager = StateManager(AssistantState.IDLE)
        self.ai_engine: Optional[AIEngine] = None
        self.stt_engine: Optional[SpeechToTextEngine] = None
        self.tts_engine: Optional[TextToSpeechEngine] = None
        self.voice_components = {}
        self.is_initialized = False
        logger.info("VoicePipeline instance created")
    
    def initialize(self) -> None:
        """
        Initialize all voice and AI components.
        
        This method loads and initializes:
        - AI engine
        - Speech-to-text engine
        - Text-to-speech engine
        - Wake word detector (if enabled) - TODO
        - Audio recorder - TODO
        - VAD detector (if enabled) - TODO
        - Translation model (if enabled) - TODO
        
        Raises:
            RuntimeError: If initialization fails
        """
        logger.info("Initializing voice pipeline components")
        
        # Initialize AI engine
        ai_config = AIEngineConfig()
        self.ai_engine = AIEngine(ai_config)
        self.ai_engine.initialize()
        
        # Initialize speech-to-text engine
        stt_config = STTConfig(
            model_name="base",
            language=self.config.language,
            backend="whisper",
            device="cpu",
            sample_rate=16000
        )
        self.stt_engine = SpeechToTextEngine(stt_config)
        
        # Initialize text-to-speech engine
        tts_config = TTSConfig(
            engine="pyttsx3",
            language=self.config.language,
            rate=170,
            volume=1.0,
            output_format="wav"
        )
        self.tts_engine = TextToSpeechEngine(tts_config)
        
        # TODO: Initialize wake word detector if enabled
        # TODO: Initialize audio recorder
        # TODO: Initialize VAD detector if enabled
        # TODO: Initialize translation model if enabled
        
        self.is_initialized = True
        logger.info("Voice pipeline initialized successfully")
    
    def wait_for_wake_word(self) -> bool:
        """
        Wait for wake word detection.
        
        This method delegates to WakeWordDetector to continuously monitor
        audio input for the wake word and blocks until detection or cancellation.
        
        State Transition: IDLE -> WAKE_WORD -> LISTENING (on detection) or IDLE (on cancel)
        
        Returns:
            True if wake word detected, False if cancelled
            
        Raises:
            RuntimeError: If wake word detection fails
        """
        logger.info("Waiting for wake word...")
        self.state_manager.transition_to(AssistantState.WAKE_WORD)
        
        # TODO: Delegate to WakeWordDetector
        # TODO: Wait for detection event
        # TODO: Handle detection or cancellation
        
        self.state_manager.transition_to(AssistantState.LISTENING)
        logger.debug("Wake word detection completed")
        return True
    
    def record_command(self) -> Optional[bytes]:
        """
        Record user voice command.
        
        This method delegates to Recorder to capture audio from the microphone
        with optional voice activity detection to automatically stop recording.
        
        State Transition: LISTENING -> TRANSCRIBING (on completion) or ERROR (on failure)
        
        Returns:
            Recorded audio data as bytes, or None if recording failed
            
        Raises:
            RuntimeError: If recording fails
        """
        logger.info("Recording voice command...")
        
        # TODO: Delegate to Recorder
        # TODO: Delegate to VAD if enabled
        # TODO: Handle recording completion or failure
        
        self.state_manager.transition_to(AssistantState.TRANSCRIBING)
        logger.debug("Recording completed")
        return None
    
    def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """
        Transcribe audio data to text.
        
        This method delegates to SpeechToTextEngine to convert recorded
        audio to text using the configured speech recognition engine.
        
        State Transition: TRANSCRIBING -> TRANSLATING (if enabled) or UNDERSTANDING
        
        Args:
            audio_data: Raw audio data bytes
            
        Returns:
            Transcribed text, or None if transcription failed
            
        Raises:
            RuntimeError: If transcription fails
        """
        logger.info("Transcribing audio...")
        
        try:
            if self.stt_engine:
                # Delegate to SpeechToTextEngine
                transcription = self.stt_engine.transcribe_audio(audio_data)
                
                
                if self.config.translation_enabled:
                    self.state_manager.transition_to(AssistantState.TRANSLATING)
                else:
                    self.state_manager.transition_to(AssistantState.UNDERSTANDING)
                
                logger.debug("Transcription completed")
                return transcription
            else:
                raise RuntimeError("Speech-to-text engine not initialized")
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            self.state_manager.transition_to(AssistantState.ERROR)
            raise RuntimeError(f"Transcription failed: {e}")
    
    def translate_command(self, text: str) -> str:
        logger.info(f"Translating command: {text}")

        translated_text = translate_to_english(text)

        logger.info(
            f"Command after translation: {translated_text}"
        )

        return translated_text

    def process_with_ai(self, text: str) -> Dict[str, Any]:
        logger.info(
            f"Processing text with AI engine: {text}"
        )

        if self.state_manager.current_state == AssistantState.RESPONDING:
            self.state_manager.transition_to(AssistantState.IDLE)

        if self.state_manager.current_state == AssistantState.IDLE:
            self.state_manager.transition_to(
                AssistantState.UNDERSTANDING
            )

        try:
            if not self.ai_engine:
                raise RuntimeError("AI engine not initialized")

            processed_text = text

            if self.config.translation_enabled:
                processed_text = self.translate_command(text)

            self.state_manager.transition_to(
                AssistantState.EXECUTING
            )

            ai_result = self.ai_engine.process(processed_text)

            self.state_manager.transition_to(
                AssistantState.RESPONDING
            )

            self.state_manager.transition_to(AssistantState.IDLE)

            return ai_result

        except Exception as error:
            logger.error(f"AI processing failed: {error}")

            if self.state_manager.current_state != AssistantState.ERROR:
                self.state_manager.transition_to(
                    AssistantState.ERROR
                )

            raise RuntimeError(
                f"AI processing failed: {error}"
            )
    
    def translate_response(self, text: str) -> str:
        """
        Translate response text if needed.
        
        This method delegates to TranslationModule to translate the response
        text to the target language if translation is enabled.
        
        Args:
            text: Response text to translate
            
        Returns:
            Translated response text (or original if no translation needed)
            
        Raises:
           RuntimeError: If translation fails
        """
        logger.info(f"Translating response: {text}")
        
        # TODO: Delegate to TranslationModule
        # TODO: Handle translation errors
        
        logger.debug("Response translation completed")
        return text
    
    def speak_response(self, text: str) -> None:
        """
        Convert response text to speech and play audio.
        
        This method delegates to TextToSpeechEngine to convert the response
        text to audio and plays it through the audio output.
        
        State Transition: RESPONDING -> IDLE (on success) or ERROR (on failure)
        
        Args:
            text: Response text to speak
            
        Raises:
            RuntimeError: If TTS or playback fails
        """
        logger.info(f"Speaking response: {text}")
        
        try:
            if self.tts_engine:
                # Delegate to TextToSpeechEngine
                self.tts_engine.speak(text)
                
                self.state_manager.transition_to(AssistantState.IDLE)
                logger.debug("Response spoken successfully")
            else:
                raise RuntimeError("Text-to-speech engine not initialized")
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            self.state_manager.transition_to(AssistantState.ERROR)
            raise RuntimeError(f"TTS failed: {e}")
    
    def run_once(self) -> Dict[str, Any]:
        """
        Execute a single voice interaction.
        
        This method orchestrates the complete pipeline by delegating to
        specialized modules. It manages state transitions throughout.
        
        Pipeline Flow:
        1. Wait for wake word (if enabled) -> WakeWordDetector
        2. Record command -> Recorder + VAD
        3. Transcribe audio -> SpeechToTextEngine
        4. Translate command (if enabled) -> TranslationModule
        5. Process with AI -> AIEngine
        6. Translate response (if enabled) -> TranslationModule
        7. Speak response -> TextToSpeechEngine
        
        Returns:
            Dictionary with interaction results
            
        Raises:
            RuntimeError: If pipeline execution fails
        """
        logger.info("Starting single voice interaction")
        
        if not self.is_initialized:
            raise RuntimeError("Pipeline not initialized. Call initialize() first.")
        
        result = {
            "success": False,
            "transcription": None,
            "ai_result": None,
            "response": None,
            "error": None
        }
        
        try:
            # Step 1: Wait for wake word (if enabled)
            if self.config.wake_word_enabled:
                self.wait_for_wake_word()
            
            # Step 2: Record command
            audio_data = self.record_command()
            if audio_data is None:
                raise RuntimeError("Recording failed")
            
            # Step 3: Transcribe audio
            transcription = self.transcribe_audio(audio_data)
            if transcription is None:
                raise RuntimeError("Transcription failed")
            result["transcription"] = transcription
            
            # Step 4: Translate command (if enabled)
            translated_text = self.translate_command(transcription)
            
            # Step 5: Process with AI engine
            ai_result = self.process_with_ai(translated_text)
            result["ai_result"] = ai_result
            
            if not ai_result.get("success"):
                raise RuntimeError(f"AI processing failed: {ai_result.get('error')}")
            
            response = ai_result.get("response", "")
            result["response"] = response
            
            # Step 6: Translate response (if enabled)
            translated_response = self.translate_response(response)
            
            # Step 7: Speak response
            self.speak_response(translated_response)
            
            result["success"] = True
            logger.info("Voice interaction completed successfully")
            
        except Exception as e:
            logger.error(f"Voice interaction failed: {e}")
            self.state_manager.transition_to(AssistantState.ERROR)
            result["error"] = str(e)
        
        return result
    
    async def run_conversation(self) -> None:
        """
        Run continuous conversation loop.
        
        This method continuously listens for wake words and executes
        voice interactions until shutdown is requested.
        
        State Transition: IDLE -> WAKE_WORD (on start) -> SHUTDOWN (on stop)
        
        Raises:
            RuntimeError: If conversation loop fails
        """
        logger.info("Starting continuous conversation loop")
        
        if not self.is_initialized:
            raise RuntimeError("Pipeline not initialized. Call initialize() first.")
        
        self.state_manager.transition_to(AssistantState.WAKE_WORD)
        
        # TODO: Implement continuous listening loop
        # TODO: Delegate to WakeWordDetector for continuous listening
        # TODO: Execute run_once() on detection
        # TODO: Handle shutdown signal
        # TODO: Manage conversation state
        
        self.state_manager.transition_to(AssistantState.SHUTDOWN)
        logger.info("Conversation loop stopped")
    
    def shutdown(self) -> None:
        """
        Shutdown all voice pipeline components.
        
        This method cleans up resources and properly shuts down
        all initialized components by delegating to their shutdown methods.
        
        State Transition: Any -> SHUTDOWN
        
        Raises:
            RuntimeError: If shutdown fails
        """
        logger.info("Shutting down voice pipeline")
        self.state_manager.transition_to(AssistantState.SHUTDOWN)
        
        # Shutdown AI engine
        if self.ai_engine:
            try:
                self.ai_engine.shutdown()
                logger.info("AI engine shutdown completed")
            except Exception as e:
                logger.error(f"Error shutting down AI engine: {e}")
        
        # Shutdown speech-to-text engine
        if self.stt_engine:
            try:
                # STT engine doesn't have explicit shutdown in template, but we clear reference
                self.stt_engine = None
                logger.info("Speech-to-text engine shutdown completed")
            except Exception as e:
                logger.error(f"Error shutting down speech-to-text engine: {e}")
        
        # Shutdown text-to-speech engine
        if self.tts_engine:
            try:
                self.tts_engine.stop()
                logger.info("Text-to-speech engine shutdown completed")
            except Exception as e:
                logger.error(f"Error shutting down text-to-speech engine: {e}")
        
        # TODO: Delegate shutdown to wake word detector
        # TODO: Delegate shutdown to audio recorder
        # TODO: Delegate shutdown to translation model if loaded
        # TODO: Delegate shutdown to VAD detector
        
        self.is_initialized = False
        logger.info("Voice pipeline shutdown completed")
