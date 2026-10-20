"""
Unit tests for level configuration and verification of all 60 levels.
"""
import unittest
import config
from core.level_manager import LevelManager
from core.board import BoardModel

class TestLevels(unittest.TestCase):

    def setUp(self):
        self.manager = LevelManager(config.LEVELS_FILE)

    def test_level_count(self):
        """Must have exactly 60 levels with IDs 1..60."""
        self.assertEqual(self.manager.get_level_count(), config.TOTAL_LEVELS)
        ids = [lvl["id"] for lvl in self.manager.levels]
        self.assertEqual(ids, list(range(1, config.TOTAL_LEVELS + 1)))

    def test_level_states_and_boards(self):
        """Every level must have a unique valid 9-element permutation and matching 3x3 board."""
        seen_states = set()
        for lvl in self.manager.levels:
            lid = lvl["id"]
            start_state = tuple(lvl["start_state"])
            self.assertTrue(BoardModel.validate_state(start_state), f"Level {lid} invalid start_state")
            self.assertNotEqual(start_state, config.GOAL_STATE, f"Level {lid} start_state already at goal")
            self.assertNotIn(start_state, seen_states, f"Level {lid} duplicate start_state")
            seen_states.add(start_state)

            # Check 3x3 board matches 1D state
            board_flattened = [val for row in lvl["start_board"] for val in row]
            self.assertEqual(board_flattened, list(start_state), f"Level {lid} board does not match state")

    def test_all_levels_solvable(self):
        """Every level's start state must be solvable relative to GOAL_STATE."""
        for lvl in self.manager.levels:
            lid = lvl["id"]
            start_state = tuple(lvl["start_state"])
            self.assertTrue(
                BoardModel.check_solvability(start_state, config.GOAL_STATE),
                f"Level {lid} is NOT solvable to GOAL_STATE"
            )

    def test_optimal_moves_monotonic(self):
        """Optimal moves must be positive and non-decreasing across levels 1..60."""
        prev = 0
        for lvl in self.manager.levels:
            opt = lvl["optimal_moves"]
            self.assertGreater(opt, 0)
            self.assertGreaterEqual(opt, prev)
            prev = opt

    def test_random_sequence_generation(self):
        """Random 60-level sequence must be a permutation of 1..60."""
        seq = self.manager.generate_random_sequence()
        self.assertEqual(len(seq), config.TOTAL_LEVELS)
        self.assertEqual(sorted(seq), list(range(1, config.TOTAL_LEVELS + 1)))

if __name__ == "__main__":
    unittest.main()
