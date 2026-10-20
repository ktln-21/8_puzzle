"""
A* search algorithm implementation for 8-Puzzle with custom goal state.
"""
import heapq
from typing import Tuple, List, Optional, Dict
import config
from core.board import BoardModel
from solver.solver_interface import SolverInterface

class AStarSolver(SolverInterface):
    """
    A* solver using Manhattan distance heuristic relative to the custom goal state.
    Guarantees shortest (optimal) number of moves.
    """

    def __init__(self):
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    @staticmethod
    def _get_goal_positions(goal_state: Tuple[int, ...]) -> Dict[int, Tuple[int, int]]:
        """Precomputes coordinates for each number in the goal state."""
        return {val: (idx // 3, idx % 3) for idx, val in enumerate(goal_state)}

    @staticmethod
    def manhattan_distance(state: Tuple[int, ...], goal_positions: Dict[int, Tuple[int, int]]) -> int:
        """Calculates sum of Manhattan distances of all non-zero tiles to their goal coordinates."""
        distance = 0
        for idx, val in enumerate(state):
            if val != 0:
                tr, tc = goal_positions[val]
                r, c = idx // 3, idx % 3
                distance += abs(r - tr) + abs(c - tc)
        return distance

    def solve(
        self,
        start_state: Tuple[int, ...],
        goal_state: Tuple[int, ...] = config.GOAL_STATE
    ) -> Optional[List[Tuple[int, ...]]]:
        self._cancelled = False
        start = tuple(start_state)
        goal = tuple(goal_state)

        if not BoardModel.check_solvability(start, goal):
            return None

        if start == goal:
            return []

        goal_positions = self._get_goal_positions(goal)
        initial_h = self.manhattan_distance(start, goal_positions)

        # Priority queue entry: (f_score, g_score, counter, state)
        # Counter used as tie-breaker to avoid comparing states directly
        counter = 0
        open_set = [(initial_h, 0, counter, start)]
        g_scores: Dict[Tuple[int, ...], int] = {start: 0}
        came_from: Dict[Tuple[int, ...], Tuple[int, ...]] = {start: None}

        # Board helper for neighbors
        dummy_board = BoardModel(start, goal)

        while open_set:
            if self._cancelled:
                return None

            _, g, _, current = heapq.heappop(open_set)

            if current == goal:
                # Reconstruct path
                path = []
                curr = current
                while came_from[curr] is not None:
                    path.append(curr)
                    curr = came_from[curr]
                path.reverse()
                return path

            if g > g_scores.get(current, float('inf')):
                continue

            for neighbor in dummy_board.get_neighbors(current):
                tentative_g = g + 1
                if tentative_g < g_scores.get(neighbor, float('inf')):
                    g_scores[neighbor] = tentative_g
                    came_from[neighbor] = current
                    counter += 1
                    f = tentative_g + self.manhattan_distance(neighbor, goal_positions)
                    heapq.heappush(open_set, (f, tentative_g, counter, neighbor))

        return None
