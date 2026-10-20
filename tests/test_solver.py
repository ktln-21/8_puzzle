"""
Unit tests for A* and BFS solvers.
"""
import unittest
import config
from solver.astar_solver import AStarSolver
from solver.bfs_solver import BFSSolver
from core.board import BoardModel
from core.level_manager import LevelManager

class TestSolvers(unittest.TestCase):

    def setUp(self):
        self.goal = config.GOAL_STATE
        self.astar = AStarSolver()
        self.bfs = BFSSolver()
        self.level_manager = LevelManager(config.LEVELS_FILE)

    def test_start_equals_goal(self):
        """If start state is already goal, returns empty list []."""
        self.assertEqual(self.astar.solve(self.goal, self.goal), [])
        self.assertEqual(self.bfs.solve(self.goal, self.goal), [])

    def test_unsolvable_returns_none(self):
        """Unsolvable state returns None."""
        unsolvable = (2, 1, 3, 8, 0, 4, 7, 6, 5)
        self.assertIsNone(self.astar.solve(unsolvable, self.goal))
        self.assertIsNone(self.bfs.solve(unsolvable, self.goal))

    def test_solve_level_1_and_validate_path(self):
        """Solves level 1 (2 moves optimal) and validates every consecutive step."""
        lvl1 = self.level_manager.get_level(1)
        start = tuple(lvl1["start_state"])

        path = self.astar.solve(start, self.goal)
        self.assertIsNotNone(path)
        self.assertEqual(len(path), lvl1["optimal_moves"])

        # Validate path transitions
        curr = start
        dummy_board = BoardModel(start, self.goal)
        for next_state in path:
            neighbors = dummy_board.get_neighbors(curr)
            self.assertIn(next_state, neighbors, f"State {next_state} is not a valid neighbor of {curr}")
            curr = next_state
        self.assertEqual(curr, self.goal)

    def test_compare_astar_and_bfs_on_early_levels(self):
        """Compares A* and BFS optimal move lengths on levels 1 to 4."""
        for lid in range(1, 5):
            lvl = self.level_manager.get_level(lid)
            start = tuple(lvl["start_state"])

            astar_path = self.astar.solve(start, self.goal)
            bfs_path = self.bfs.solve(start, self.goal)

            self.assertEqual(len(astar_path), lvl["optimal_moves"])
            self.assertEqual(len(bfs_path), lvl["optimal_moves"])

    def test_astar_solves_all_60_levels(self):
        """Verifies A* solves all 60 levels with optimal path length."""
        for lvl in self.level_manager.levels:
            lid = lvl["id"]
            start = tuple(lvl["start_state"])
            path = self.astar.solve(start, self.goal)
            self.assertIsNotNone(path, f"A* failed to solve level {lid}")
            self.assertEqual(len(path), lvl["optimal_moves"], f"Level {lid} non-optimal path")
            self.assertEqual(path[-1], self.goal)

if __name__ == "__main__":
    unittest.main()
