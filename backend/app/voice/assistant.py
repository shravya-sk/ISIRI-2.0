"""
Voice Assistant Entry Point

This module serves as the main entry point for the ISIRI voice assistant.
It creates and runs a VoicePipeline instance for a single-turn interaction.

The assistant:
- Creates a VoicePipeline instance
- Initializes all components
- Runs a single voice interaction
- Prints the result for debugging
- Shuts down gracefully

This is a single-turn assistant with no wake word, no VAD, and no continuous conversation.
"""

import logging
from backend.app.voice.pipeline import VoicePipeline, PipelineConfig


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for the voice assistant.
    
    This function:
    1. Creates a VoicePipeline instance with appropriate configuration
    2. Initializes all components
    3. Runs a single voice interaction
    4. Prints the result for debugging
    5. Shuts down gracefully
    """
    print("=" * 50)
    print("          ISIRI 2.0 Voice Assistant")
    print("=" * 50)
    
    # Create pipeline configuration
    config = PipelineConfig(
        wake_word_enabled=False,  # No wake word for single-turn
        vad_enabled=False,  # No VAD for single-turn
        translation_enabled=False,  # No translation yet
        language="en",  # English language
        hardware_integration=False  # No hardware integration yet
    )
    
    # Create voice pipeline
    pipeline = VoicePipeline(config)
    
    try:
        # Initialize all components
        logger.info("Initializing voice pipeline...")
        pipeline.initialize()
        logger.info("Voice pipeline initialized successfully")
        
        # Run single voice interaction
        logger.info("Starting voice interaction...")
        result = pipeline.run_once()
        
        # Print result for debugging
        print("\n" + "=" * 50)
        print("Interaction Result:")
        print("=" * 50)
        print(f"Success: {result.get('success')}")
        print(f"Transcription: {result.get('transcription')}")
        print(f"AI Result: {result.get('ai_result')}")
        print(f"Response: {result.get('response')}")
        if result.get('error'):
            print(f"Error: {result.get('error')}")
        print("=" * 50)
        
    except Exception as e:
        logger.error(f"Voice assistant failed: {e}")
        print(f"\nError: {e}")
        
    finally:
        # Shutdown gracefully
        logger.info("Shutting down voice pipeline...")
        pipeline.shutdown()
        logger.info("Voice pipeline shutdown completed")
        print("\nGoodbye!")


if __name__ == "__main__":
    main()