"""
Unit tests for BoardModel logic.
"""
import unittest
from core.board import BoardModel
import config

class TestBoardModel(unittest.TestCase):

    def setUp(self):
        self.goal = config.GOAL_STATE  # (1, 2, 3, 8, 0, 4, 7, 6, 5)
        self.board = BoardModel(self.goal)

    def test_goal_recognition(self):
        """Goal state is correctly identified as goal."""
        self.assertTrue(self.board.is_goal())
        self.assertTrue(self.board.is_goal(self.goal))
        # Non-goal state
        other = (1, 2, 3, 8, 4, 0, 7, 6, 5)
        self.assertFalse(self.board.is_goal(other))

    def test_edge_wrap_not_adjacent(self):
        """Ensure row-wrap indices (e.g. index 2 and 3, index 5 and 6) are NOT adjacent."""
        self.assertFalse(BoardModel.are_adjacent(2, 3))
        self.assertFalse(BoardModel.are_adjacent(3, 2))
        self.assertFalse(BoardModel.are_adjacent(5, 6))
        self.assertFalse(BoardModel.are_adjacent(6, 5))
        # Valid adjacent
        self.assertTrue(BoardModel.are_adjacent(0, 1))
        self.assertTrue(BoardModel.are_adjacent(1, 2))
        self.assertTrue(BoardModel.are_adjacent(1, 4))
        self.assertTrue(BoardModel.are_adjacent(4, 5))

    def test_valid_move(self):
        """Moving adjacent tile succeeds and updates state correctly."""
        # Goal state has 0 at index 4 (center).
        # Adjacent indices to center: 1 (top), 3 (left), 5 (right), 7 (bottom).
        self.assertEqual(self.board.find_empty(), 4)
        self.assertTrue(self.board.can_move(1))
        self.assertTrue(self.board.can_move(3))
        self.assertTrue(self.board.can_move(5))
        self.assertTrue(self.board.can_move(7))
        # Corner indices are not adjacent to center
        self.assertFalse(self.board.can_move(0))
        self.assertFalse(self.board.can_move(2))
        self.assertFalse(self.board.can_move(6))
        self.assertFalse(self.board.can_move(8))
        self.assertFalse(self.board.can_move(4))  # empty tile itself

        # Execute move of tile 1 (value is 2)
        old_state = self.board.get_state()
        success = self.board.move_tile(1)
        self.assertTrue(success)
        new_state = self.board.get_state()
        self.assertNotEqual(old_state, new_state)
        self.assertEqual(new_state[1], 0)
        self.assertEqual(new_state[4], 2)
        # Permutation set preserved
        self.assertEqual(set(new_state), set(range(9)))

    def test_invalid_move_rejected(self):
        """Moving non-adjacent tile returns False and state remains unchanged."""
        old_state = self.board.get_state()
        self.assertFalse(self.board.move_tile(0))
        self.assertEqual(self.board.get_state(), old_state)

    def test_get_neighbors_immutability(self):
        """get_neighbors returns valid states and does not mutate the current state."""
        original = self.board.get_state()
        neighbors = self.board.get_neighbors()
        self.assertEqual(self.board.get_state(), original)
        # Center empty has exactly 4 neighbors
        self.assertEqual(len(neighbors), 4)
        for n in neighbors:
            self.assertEqual(len(n), 9)
            self.assertEqual(set(n), set(range(9)))
            self.assertNotEqual(n, original)

    def test_solvability(self):
        """Solvability correctly distinguishes reachable vs unreachable states."""
        self.assertTrue(BoardModel.check_solvability(self.goal, self.goal))
        # Swap two adjacent non-zero numbers in goal to flip parity: (2, 1, 3, 8, 0, 4, 7, 6, 5)
        unsolvable_state = (2, 1, 3, 8, 0, 4, 7, 6, 5)
        self.assertFalse(BoardModel.check_solvability(unsolvable_state, self.goal))

if __name__ == "__main__":
    unittest.main()
