"""
Voice Assistant State Management

This module defines the state machine for the voice assistant.
The AssistantState enum represents all possible states the assistant
can be in during its operation.

Responsibilities:
- Define assistant states
- Provide state transitions
- Enable state-based behavior
- Support state monitoring

Usage:
    from backend.app.voice.state import AssistantState
    
    current_state = AssistantState.IDLE
    if current_state == AssistantState.LISTENING:
        # Handle listening state
"""

from enum import Enum
from typing import Optional, Dict, Any
import logging


logger = logging.getLogger(__name__)


class AssistantState(Enum):
    """
    Enumeration of all possible assistant states.
    
    The voice assistant transitions through these states during operation:
    - IDLE: Assistant is ready and waiting
    - WAKE_WORD: Listening for wake word activation
    - LISTENING: Recording user voice command
    - TRANSCRIBING: Converting audio to text
    - TRANSLATING: Translating text (if translation enabled)
    - UNDERSTANDING: AI processing (intent, entities, planning)
    - EXECUTING: Executing plugin/action
    - RESPONDING: Generating and speaking response
    - ERROR: Error state for recovery
    - SHUTDOWN: Assistant is shutting down
    """
    
    IDLE = "idle"
    WAKE_WORD = "wake_word"
    LISTENING = "listening"
    TRANSCRIBING = "transcribing"
    TRANSLATING = "translating"
    UNDERSTANDING = "understanding"
    EXECUTING = "executing"
    RESPONDING = "responding"
    ERROR = "error"
    SHUTDOWN = "shutdown"
    
    def __str__(self) -> str:
        """Return string representation of state."""
        return self.value
    
    def is_active(self) -> bool:
        """
        Check if state is an active processing state.
        
        Returns:
            True if state is actively processing, False otherwise
        """
        return self in {
            AssistantState.WAKE_WORD,
            AssistantState.LISTENING,
            AssistantState.TRANSCRIBING,
            AssistantState.TRANSLATING,
            AssistantState.UNDERSTANDING,
            AssistantState.EXECUTING,
            AssistantState.RESPONDING
        }
    
    def is_terminal(self) -> bool:
        """
        Check if state is a terminal state.
        
        Returns:
            True if state is terminal (IDLE, ERROR, SHUTDOWN), False otherwise
        """
        return self in {
            AssistantState.IDLE,
            AssistantState.ERROR,
            AssistantState.SHUTDOWN
        }
    
    def can_transition_to(self, target_state: 'AssistantState') -> bool:
        """
        Check if transition to target state is valid.
        
        Args:
            target_state: Target state to transition to
            
        Returns:
            True if transition is valid, False otherwise
        """
        # Define valid transitions
        valid_transitions = {
            AssistantState.IDLE: {
                AssistantState.WAKE_WORD,
                AssistantState.LISTENING,
                AssistantState.UNDERSTANDING,
                AssistantState.SHUTDOWN
            },
            AssistantState.WAKE_WORD: {
                AssistantState.LISTENING,
                AssistantState.IDLE,
                AssistantState.ERROR,
                AssistantState.SHUTDOWN
            },
            AssistantState.LISTENING: {
                AssistantState.TRANSCRIBING,
                AssistantState.IDLE,
                AssistantState.ERROR
            },
            AssistantState.TRANSCRIBING: {
                AssistantState.TRANSLATING,
                AssistantState.UNDERSTANDING,
                AssistantState.ERROR
            },
            AssistantState.TRANSLATING: {
                AssistantState.UNDERSTANDING,
                AssistantState.ERROR
            },
            AssistantState.UNDERSTANDING: {
                AssistantState.EXECUTING,
                AssistantState.RESPONDING,
                AssistantState.ERROR
            },
            AssistantState.EXECUTING: {
                AssistantState.RESPONDING,
                AssistantState.ERROR
            },
            AssistantState.RESPONDING: {
                AssistantState.IDLE,
                AssistantState.WAKE_WORD,
                AssistantState.ERROR
            },
            AssistantState.ERROR: {
                AssistantState.IDLE,
                AssistantState.SHUTDOWN
            },
            AssistantState.SHUTDOWN: set()
        }
        
        return target_state in valid_transitions.get(self, set())


class StateManager:
    """
    Manages assistant state transitions.
    
    This class provides a thread-safe way to manage state transitions
    and notify listeners of state changes.
    """
    
    def __init__(self, initial_state: AssistantState = AssistantState.IDLE):
        """
        Initialize state manager.
        
        Args:
            initial_state: Starting state
        """
        self._current_state = initial_state
        self._state_history = []
        self._listeners = []
        logger.info(f"StateManager initialized with state: {initial_state}")
    
    @property
    def current_state(self) -> AssistantState:
        """Get current state."""
        return self._current_state
    
    def transition_to(self, new_state: AssistantState) -> bool:
        """
        Transition to a new state.
        
        Args:
            new_state: Target state
            
        Returns:
            True if transition succeeded, False otherwise
            
        Raises:
            ValueError: If transition is invalid
        """
        if not self._current_state.can_transition_to(new_state):
            error_msg = f"Invalid transition from {self._current_state} to {new_state}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        old_state = self._current_state
        self._current_state = new_state
        self._state_history.append((old_state, new_state))
        
        logger.info(f"State transition: {old_state} -> {new_state}")
        self._notify_listeners(old_state, new_state)
        
        return True
    
    def reset(self) -> None:
        """Reset to IDLE state."""
        logger.info("Resetting state to IDLE")
        self.transition_to(AssistantState.IDLE)
        self._state_history.clear()
    
    def get_history(self) -> list:
        """
        Get state transition history.
        
        Returns:
            List of (old_state, new_state) tuples
        """
        return self._state_history.copy()
    
    def add_listener(self, callback) -> None:
        """
        Add a state change listener.
        
        Args:
            callback: Function to call on state change (old_state, new_state)
        """
        self._listeners.append(callback)
        logger.debug(f"Added state change listener: {callback}")
    
    def remove_listener(self, callback) -> None:
        """
        Remove a state change listener.
        
        Args:
            callback: Function to remove from listeners
        """
        if callback in self._listeners:
            self._listeners.remove(callback)
            logger.debug(f"Removed state change listener: {callback}")
    
    def _notify_listeners(self, old_state: AssistantState, new_state: AssistantState) -> None:
        """
        Notify all listeners of state change.
        
        Args:
            old_state: Previous state
            new_state: New state
        """
        for callback in self._listeners:
            try:
                callback(old_state, new_state)
            except Exception as e:
                logger.error(f"Error in state change listener: {e}")
