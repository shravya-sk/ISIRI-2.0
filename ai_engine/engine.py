"""
AI Engine Orchestrator

This module provides the main AI engine that coordinates all AI processing components.
The AIEngine class serves as a facade for the AI subsystem, hiding the complexity
of intent detection, entity extraction, planning, plugin execution, and response generation.

Responsibilities:
- Coordinate AI processing pipeline
- Manage AI component lifecycle
- Provide unified interface for voice pipeline
- Handle AI-specific errors and fallbacks
- Support conversation context

Usage:
    engine = AIEngine(config)
    engine.initialize()
    result = engine.process("What's the weather today?")
    engine.shutdown()
"""
from ai_engine.intent_detector import detect_intent
from ai_engine.entity_extractor import extract_entities
from ai_engine.planner import plan
from ai_engine.plugin_executor import execute_plugin
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging
import re


logger = logging.getLogger(__name__)


@dataclass
class AIEngineConfig:
    """Configuration for the AI engine."""
    context_enabled: bool = True
    max_context_turns: int = 5
    fallback_enabled: bool = True


class AIEngine:
    """
    Main AI engine orchestrator.
    
    This class provides a unified interface for AI processing by coordinating:
    - Intent detection
    - Entity extraction
    - Planning
    - Plugin execution
    - Response generation
    
    The voice pipeline should only call process() and never interact with
    individual AI components directly.
    """
    
    def __init__(self, config: Optional[AIEngineConfig] = None):
        """
        Initialize the AI engine.
        
        Args:
            config: AI engine configuration object
        """
        self.config = config or AIEngineConfig()
        self.components = {}
        self.context = {}
        self.is_initialized = False
        logger.info("AIEngine instance created")
    
    def initialize(self) -> None:
        """
        Initialize all AI components.
        
        This method loads and initializes:
        - Intent detector
        - Entity extractor
        - Planner
        - Plugin executor
        - Response generator
        
        Raises:
            RuntimeError: If initialization fails
        """
        logger.info("Initializing AI engine components")
        # TODO: Initialize intent detector
        # TODO: Initialize entity extractor
        # TODO: Initialize planner
        # TODO: Initialize plugin executor
        # TODO: Initialize response generator
        # TODO: Initialize context manager if enabled
        self.is_initialized = True
        logger.info("AI engine initialized successfully")
    
    def process(self, text: str) -> Dict[str, Any]:
        logger.info(f"Processing text: {text}")

        if not self.is_initialized:
            raise RuntimeError(
                "AI engine not initialized. Call initialize() first."
            )

        result = {
            "success": False,
            "intent": None,
            "entities": None,
            "response": None,
            "context": self.context,
            "error": None,
            "weather": None,
            "link": "",
        }

        fixed_response = self._get_fixed_response(text)

        if fixed_response:
            result["success"] = True
            result["intent"] = "conversation"
            result["entities"] = {}
            result["response"] = fixed_response

            if self.config.context_enabled:
                self._update_context(
                    text,
                    fixed_response,
                    "conversation",
                    {},
                )
                result["context"] = self.context

            return result

        try:
            intent = self._detect_intent(text)
            result["intent"] = intent

            entities = self._extract_entities(text, intent)

            if (
                intent == "unknown"
                and self.context.get("pending_intent") == "weather"
            ):
                location = entities.get("location")

                if not location and re.fullmatch(
                    r"[A-Za-z][A-Za-z\s-]{1,60}",
                    text.strip(),
                ):
                    location = text.strip().title()

                if location:
                    intent = "weather"
                    entities["location"] = location

                    previous_entities = self.context.get(
                        "last_entities",
                        {},
                    )

                    if (
                        "time" in previous_entities
                        and "time" not in entities
                    ):
                        entities["time"] = previous_entities["time"]

            result["intent"] = intent
            result["entities"] = entities

            execution_plan = self._plan_execution(
                intent,
                entities,
            )

            plugin_result = self._execute_plugin(
                execution_plan
            )

            result["link"] = plugin_result.get("link", "")
            result["weather"] = plugin_result.get("weather")

            response = self._generate_response(
                plugin_result,
                intent,
                entities,
            )

            if isinstance(response, dict):
                result["response"] = response.get("reply", "")
                result["link"] = response.get("link", "")
            else:
                result["response"] = response

            if self.config.context_enabled:
                self._update_context(
                    text,
                    result["response"],
                    intent,
                    entities,
                )
                result["context"] = self.context

            result["success"] = True
            logger.info("AI processing completed successfully")

        except Exception as error:
            logger.error(f"AI processing failed: {error}")
            result["error"] = str(error)

            if self.config.fallback_enabled:
                result["response"] = self._fallback_response(text)

        return result

    def _get_fixed_response(self, text: str):
        normalized_text = re.sub(
            r"[^\w\s]",
            "",
            text.lower(),
        ).strip()

        fixed_responses = {
            "how are you": "Yaan ushar ulle.",
            "how are you doing": "Yaan ushar ulle.",
            "what is your name": "Enna peru ISIRI 2.0.",
            "isiri kenunda": "Kenundu. Please tell me your command.",
        }

        return fixed_responses.get(normalized_text)
    
    def _detect_intent(self, text: str) -> str:
        """
        Detect user intent from text.
        
        Args:
            text: User input text
            
        Returns:
            Detected intent string
            
        Raises:
            RuntimeError: If intent detection fails
        """
        logger.debug("Detecting intent")
        # TODO: Call intent detector component
        # TODO: Provide context if available
        # TODO: Handle detection errors
        result = detect_intent(text)

        return result["intent"]
    
    def _extract_entities(self, text: str, intent: str) -> Dict[str, Any]:
        """
        Extract entities from text.
        
        Args:
            text: User input text
            intent: Detected intent for context
            
        Returns:
            Dictionary of extracted entities
            
        Raises:
            RuntimeError: If entity extraction fails
        """
        logger.debug("Extracting entities")
        # TODO: Call entity extractor component
        # TODO: Provide intent context
        # TODO: Handle extraction errors
        return extract_entities(text)
    
    def _plan_execution(self, intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plan execution based on intent and entities.
        
        Args:
            intent: Detected intent
            entities: Extracted entities
            
        Returns:
            Execution plan dictionary
            
        Raises:
            RuntimeError: If planning fails
        """
        logger.debug("Planning execution")
        # TODO: Call planner component
        # TODO: Provide intent and entities
        # TODO: Provide context if available
        # TODO: Handle planning errors
        return plan(intent, entities)
    
    def _execute_plugin(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the planned plugin.
        
        Args:
            plan: Execution plan with plugin and parameters
            
        Returns:
            Plugin execution result
            
        Raises:
            RuntimeError: If plugin execution fails
        """
        logger.debug("Executing plugin")
        # TODO: Call plugin executor component
        # TODO: Provide execution plan
        # TODO: Handle execution errors
        # TODO: Return plugin result
        return execute_plugin(plan)
    
    def _generate_response(
        self,
        plugin_result: Dict[str, Any],
        intent: str,
        entities: Dict[str, Any]
    ) -> str:
        """
        Generate response text from plugin result.
        
        Args:
            plugin_result: Plugin execution result
            intent: Detected intent
            entities: Extracted entities
            
        Returns:
            Response text for the user
            
        Raises:
            RuntimeError: If response generation fails
        """
        logger.debug("Generating response")
        # TODO: Call response generator component
        # TODO: Provide plugin result, intent, entities
        # TODO: Provide context if available
        # TODO: Handle generation errors
        return plugin_result.get("reply", "")
    
    def _update_context(
        self,
        user_input: str,
        assistant_response: str,
        intent: str,
        entities: Dict[str, Any]
    ) -> None:
        """
        Update conversation context.
        
        Args:
            user_input: User's input
            assistant_response: Assistant's response
            intent: Detected intent
            entities: Extracted entities
        """
        logger.debug("Updating context")
        # TODO: Add conversation turn to context
        # TODO: Prune old context if exceeds max turns
        # TODO: Update relevant context variables
        self.context["last_intent"] = intent
        self.context["last_entities"] = entities.copy()

        # Keep weather active only when ISIRI asked the user for a city.
        if intent == "weather" and not entities.get("location"):
            self.context["pending_intent"] = "weather"
        else:
            self.context.pop("pending_intent", None)
    
    def _fallback_response(self, text: str) -> str:
        """
        Generate fallback response when AI processing fails.
        
        Args:
            text: User input text
            
        Returns:
            Fallback response text
        """
        logger.debug("Generating fallback response")
        # TODO: Implement fallback logic
        # TODO: Could be generic or context-aware
        return "I'm sorry, I couldn't process that request. Please try again."
    
    def clear_context(self) -> None:
        """Clear conversation context."""
        logger.info("Clearing conversation context")
        self.context = {}
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get current conversation context.
        
        Returns:
            Current context dictionary
        """
        return self.context.copy()
    
    def shutdown(self) -> None:
        """
        Shutdown all AI engine components.
        
        Raises:
            RuntimeError: If shutdown fails
        """
        logger.info("Shutting down AI engine")
        # TODO: Shutdown intent detector
        # TODO: Shutdown entity extractor
        # TODO: Shutdown planner
        # TODO: Shutdown plugin executor
        # TODO: Shutdown response generator
        # TODO: Clear component references
        self.is_initialized = False
        logger.info("AI engine shutdown completed")
