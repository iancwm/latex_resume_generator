import unittest
import copy
from src.undo_manager import UndoManager


class TestUndoManager(unittest.TestCase):

    def setUp(self):
        self.manager = UndoManager()

    def tearDown(self):
        pass

    def test_set_initial_state(self):
        """Test setting the initial state."""
        initial_state = {"resume": "content", "template": "modern"}
        self.manager.set_initial_state(initial_state)

        # After set_initial_state, can_undo is True (initial state is undoable)
        self.assertTrue(self.manager.can_undo())
        
        # Undo returns the initial state
        result = self.manager.undo()
        self.assertEqual(result, initial_state)

    def test_push_state_adds_to_undo_stack(self):
        """Test that push_state adds a new state to the undo stack."""
        self.manager.set_initial_state({"step": 1})
        self.manager.push_state({"step": 2})
        self.manager.push_state({"step": 3})

        # Should have multiple undo states available
        self.assertTrue(self.manager.can_undo())

    def test_push_state_clears_redo_stack(self):
        """Test that push_state clears the redo stack."""
        self.manager.set_initial_state({"step": 1})
        self.manager.push_state({"step": 2})

        # Undo once
        self.manager.undo()

        # Now redo should be available
        self.assertTrue(self.manager.can_redo())

        # Push a new state - should clear redo
        self.manager.push_state({"step": 3})

        # Redo should no longer be available
        self.assertFalse(self.manager.can_redo())

    def test_undo_returns_previous_state(self):
        """Test that undo returns the previous state."""
        initial = {"step": 1}
        state2 = {"step": 2}
        state3 = {"step": 3}

        self.manager.set_initial_state(initial)
        self.manager.push_state(state2)
        self.manager.push_state(state3)

        # Undo returns state2 (the state before current state3)
        result = self.manager.undo()
        self.assertEqual(result, state2)

        # Undo again returns initial
        result = self.manager.undo()
        self.assertEqual(result, initial)

    def test_undo_returns_deep_copy(self):
        """Test that undo returns a deep copy of the state."""
        initial_state = {"data": [1, 2, 3]}
        self.manager.set_initial_state(initial_state)
        self.manager.push_state({"data": [1, 2, 3]})

        result = self.manager.undo()

        # Modifying result should not affect internal state
        result["data"].append(4)

        # Undo again should return original state
        self.manager.push_state({"data": [1, 2, 3]})
        result2 = self.manager.undo()
        self.assertEqual(result2["data"], [1, 2, 3])

    def test_undo_when_empty_returns_none(self):
        """Test that undo returns None when stack is empty."""
        result = self.manager.undo()
        self.assertIsNone(result)

    def test_redo_returns_next_state(self):
        """Test that redo returns the next state."""
        initial = {"step": 1}
        state2 = {"step": 2}
        state3 = {"step": 3}

        self.manager.set_initial_state(initial)
        self.manager.push_state(state2)
        self.manager.push_state(state3)

        # Undo twice
        self.manager.undo()
        self.manager.undo()

        # Redo to state2
        result = self.manager.redo()
        self.assertEqual(result, state2)

        # Redo to state3
        result = self.manager.redo()
        self.assertEqual(result, state3)

    def test_redo_returns_deep_copy(self):
        """Test that redo returns a deep copy of the state."""
        initial_state = {"data": [1, 2, 3]}
        self.manager.set_initial_state(initial_state)
        self.manager.push_state({"data": [1, 2, 3]})

        # Undo then redo
        self.manager.undo()
        result = self.manager.redo()

        # Modifying result should not affect internal state
        result["data"].append(4)

        # Redo again should return original state
        self.manager.undo()
        result2 = self.manager.redo()
        self.assertEqual(result2["data"], [1, 2, 3])

    def test_redo_when_empty_returns_none(self):
        """Test that redo returns None when stack is empty."""
        result = self.manager.redo()
        self.assertIsNone(result)

    def test_can_undo_initial_false(self):
        """Test that can_undo returns False initially."""
        self.assertFalse(self.manager.can_undo())

    def test_can_undo_after_set_initial_state(self):
        """Test that can_undo returns True after set_initial_state."""
        self.manager.set_initial_state({"data": "test"})
        self.assertTrue(self.manager.can_undo())

    def test_can_undo_after_all_undos(self):
        """Test that can_undo returns False after undoing all states."""
        self.manager.set_initial_state({"step": 1})

        # Undo to exhaust stack
        self.manager.undo()

        self.assertFalse(self.manager.can_undo())

    def test_can_redo_initial_false(self):
        """Test that can_redo returns False initially."""
        self.assertFalse(self.manager.can_redo())

    def test_can_redo_after_push_state(self):
        """Test that can_redo returns False after push_state (clears redo)."""
        self.manager.set_initial_state({"step": 1})
        self.manager.push_state({"step": 2})

        # Undo to enable redo
        self.manager.undo()
        self.assertTrue(self.manager.can_redo())

        # Push new state clears redo
        self.manager.push_state({"step": 3})
        self.assertFalse(self.manager.can_redo())

    def test_can_redo_after_all_redos(self):
        """Test that can_redo returns False after redoing all states."""
        self.manager.set_initial_state({"step": 1})
        self.manager.push_state({"step": 2})

        # Undo then redo
        self.manager.undo()
        self.manager.redo()

        # No more redo states
        self.assertFalse(self.manager.can_redo())

    def test_commit_clears_stacks(self):
        """Test that commit clears both undo and redo stacks."""
        self.manager.set_initial_state({"step": 1})
        self.manager.push_state({"step": 2})
        self.manager.undo()

        # Commit should clear everything
        self.manager.commit()

        self.assertFalse(self.manager.can_undo())
        self.assertFalse(self.manager.can_redo())

    def test_clear_resets_all_state(self):
        """Test that clear resets all state."""
        self.manager.set_initial_state({"step": 1})
        self.manager.push_state({"step": 2})

        # Clear should reset everything
        self.manager.clear()

        self.assertFalse(self.manager.can_undo())
        self.assertFalse(self.manager.can_redo())

        # Should be able to set new initial state
        self.manager.set_initial_state({"new": "state"})
        self.assertTrue(self.manager.can_undo())

    def test_max_states_fifo_limit(self):
        """Test that max_states enforces FIFO limit."""
        manager = UndoManager(max_states=3)

        # Set initial + push 4 more states (should only keep 3)
        manager.set_initial_state({"step": 1})
        manager.push_state({"step": 2})
        manager.push_state({"step": 3})
        manager.push_state({"step": 4})
        manager.push_state({"step": 5})

        # Should only have 3 states available (oldest dropped)
        # Undo should return step 4, then 3, then 2
        result1 = manager.undo()
        self.assertEqual(result1, {"step": 4})

        result2 = manager.undo()
        self.assertEqual(result2, {"step": 3})

        result3 = manager.undo()
        self.assertEqual(result3, {"step": 2})

        # No more undo states
        self.assertFalse(manager.can_undo())

    def test_max_states_default_50(self):
        """Test that default max_states is 50."""
        manager = UndoManager()

        # Should be able to push 50 states
        manager.set_initial_state({"step": 0})
        for i in range(1, 51):
            manager.push_state({"step": i})

        # Should still have undo available
        self.assertTrue(manager.can_undo())

    def test_state_isolation_with_nested_structures(self):
        """Test that nested structures are properly isolated via deep copy."""
        initial = {"resume": {"sections": [{"title": "Experience"}]}}
        self.manager.set_initial_state(initial)

        # Modify and push
        modified = {"resume": {"sections": [{"title": "Experience"}, {"title": "Education"}]}}
        self.manager.push_state(modified)

        # Undo should return isolated copy
        result = self.manager.undo()

        # Modify the result
        result["resume"]["sections"].append({"title": "Skills"})

        # Push a new state and undo again to verify internal state is unchanged
        self.manager.push_state({"resume": {"sections": [{"title": "Experience"}]}})
        result2 = self.manager.undo()
        self.assertEqual(len(result2["resume"]["sections"]), 1)


if __name__ == "__main__":
    unittest.main()
