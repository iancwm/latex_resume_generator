import copy
from collections import deque


class UndoManager:
    """
    Manages undo/redo functionality using the Command pattern.
    Uses deque for efficient FIFO stack operations with configurable max size.
    
    The undo stack stores states that can be undone to. The initial state
    is stored as the first undoable state.
    """

    def __init__(self, max_states=50):
        """
        Initialize UndoManager.

        Args:
            max_states: Maximum number of states to keep in undo stack (default: 50)
        """
        self.max_states = max_states
        # Undo stack stores states we can undo TO (previous states, not including current)
        self._undo_stack = deque(maxlen=max_states)
        # Redo stack stores states we can redo TO
        self._redo_stack = deque(maxlen=max_states)
        # Current state (separate from stacks)
        self._current_state = None

    def set_initial_state(self, state):
        """
        Set the initial state. This becomes the first undoable state.
        After calling this, can_undo() returns True.

        Args:
            state: The initial state to store (will be deep copied)
        """
        # Clear any existing state
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._current_state = None

        # Push initial state to undo stack as the first undoable state
        self._undo_stack.append(copy.deepcopy(state))

    def push_state(self, state):
        """
        Push current state to undo stack, set new state as current.
        Clears the redo stack (new action invalidates redo history).

        Args:
            state: The new state to store (will be deep copied)
        """
        # Move current state to undo stack (if we have one)
        if self._current_state is not None:
            self._undo_stack.append(copy.deepcopy(self._current_state))

        # Clear redo stack on new action
        self._redo_stack.clear()

        # Set new state as current
        self._current_state = copy.deepcopy(state)

    def undo(self):
        """
        Return the previous state from undo stack.
        Current state moves to redo stack.

        Returns:
            Deep copy of the previous state, or None if no undo available
        """
        if not self._undo_stack:
            return None

        # Move current state to redo stack
        if self._current_state is not None:
            self._redo_stack.append(copy.deepcopy(self._current_state))

        # Pop previous state and make it current
        self._current_state = self._undo_stack.pop()

        # Return deep copy
        return copy.deepcopy(self._current_state)

    def redo(self):
        """
        Return the next state from redo stack.
        Current state moves back to undo stack.

        Returns:
            Deep copy of the next state, or None if no redo available
        """
        if not self._redo_stack:
            return None

        # Move current state to undo stack
        if self._current_state is not None:
            self._undo_stack.append(copy.deepcopy(self._current_state))

        # Pop next state and make it current
        self._current_state = self._redo_stack.pop()

        # Return deep copy
        return copy.deepcopy(self._current_state)

    def commit(self):
        """
        Clear both undo and redo stacks.
        Used to finalize changes and prevent undo/redo.
        """
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._current_state = None

    def can_undo(self):
        """
        Check if undo is available.
        Returns True if we have states on undo stack.

        Returns:
            True if undo is available, False otherwise
        """
        return len(self._undo_stack) > 0

    def can_redo(self):
        """
        Check if redo is available.

        Returns:
            True if redo is available, False otherwise
        """
        return len(self._redo_stack) > 0

    def clear(self):
        """
        Reset all state (same as commit).
        Clears both undo and redo stacks.
        """
        self.commit()
