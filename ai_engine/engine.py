"""
AI Engine Orchestrator
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
    context_enabled: bool = True
    max_context_turns: int = 5
    fallback_enabled: bool = True


class AIEngine:

    def __init__(self, config: Optional[AIEngineConfig] = None):
        self.config = config or AIEngineConfig()
        self.components = {}
        self.context = {}
        self.is_initialized = False
        logger.info("AIEngine instance created")

    def initialize(self) -> None:
        logger.info("Initializing AI engine components")
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
                    True,
                )
                result["context"] = self.context

            return result

        try:
            intent = self._detect_intent(text)
            result["intent"] = intent

            entities = self._extract_entities(text, intent)

            pending = self.context.get("pending_intent")

            if (
                intent == "unknown"
                and pending == "weather"
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

            if (
                pending == "spotify"
                and not entities.get("query")
            ):
                query = text.strip()
                if query:
                    intent = "spotify"
                    entities["query"] = query

            if (
                pending == "alarm"
                and not entities.get("alarm_time_text")
            ):
                time_reply = text.strip()
                if time_reply:
                    intent = "alarm"
                    entities["alarm_time_text"] = time_reply

            if (
                pending == "youtube"
                and not entities.get("video")
            ):
                video_reply = text.strip()
                if video_reply:
                    intent = "youtube"
                    entities["video"] = video_reply

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
                    plugin_result.get("success", True),
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
        logger.debug("Detecting intent")
        result = detect_intent(text)
        return result["intent"]

    def _extract_entities(self, text: str, intent: str) -> Dict[str, Any]:
        logger.debug("Extracting entities")
        return extract_entities(text)

    def _plan_execution(self, intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug("Planning execution")
        return plan(intent, entities)

    def _execute_plugin(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug("Executing plugin")
        return execute_plugin(plan)

    def _generate_response(
        self,
        plugin_result: Dict[str, Any],
        intent: str,
        entities: Dict[str, Any]
    ) -> str:
        logger.debug("Generating response")
        return plugin_result.get("reply", "")

    def _update_context(
        self,
        user_input: str,
        assistant_response: str,
        intent: str,
        entities: Dict[str, Any],
        success: bool = True,
    ) -> None:
        logger.debug("Updating context")
        self.context["last_intent"] = intent
        self.context["last_entities"] = entities.copy()

        if intent == "weather" and not entities.get("location"):
            self.context["pending_intent"] = "weather"
        elif (
            intent == "spotify"
            and not entities.get("query")
            and entities.get("spotify_action") != "open"
        ):
            self.context["pending_intent"] = "spotify"
        elif intent == "alarm" and not success:
            self.context["pending_intent"] = "alarm"
        elif intent == "youtube" and not entities.get("video"):
            self.context["pending_intent"] = "youtube"
        else:
            self.context.pop("pending_intent", None)

    def _fallback_response(self, text: str) -> str:
        logger.debug("Generating fallback response")
        return "I'm sorry, I couldn't process that request. Please try again."

    def clear_context(self) -> None:
        logger.info("Clearing conversation context")
        self.context = {}

    def get_context(self) -> Dict[str, Any]:
        return self.context.copy()

    def shutdown(self) -> None:
        logger.info("Shutting down AI engine")
        self.is_initialized = False
        logger.info("AI engine shutdown completed")