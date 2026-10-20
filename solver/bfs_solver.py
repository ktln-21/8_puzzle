"""
Breadth-First Search (BFS) solver for 8-Puzzle with custom goal state.
Guaranteed optimal path length. Useful for verification and comparative analysis.
"""
from collections import deque
from typing import Tuple, List, Optional, Dict
import config
from core.board import BoardModel
from solver.solver_interface import SolverInterface

class BFSSolver(SolverInterface):
    """
    BFS solver explores level-by-level to find the shortest path.
    """

    def __init__(self):
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

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

        queue = deque([start])
        visited: Dict[Tuple[int, ...], Optional[Tuple[int, ...]]] = {start: None}
        dummy_board = BoardModel(start, goal)

        while queue:
            if self._cancelled:
                return None

            current = queue.popleft()

            if current == goal:
                path = []
                curr = current
                while visited[curr] is not None:
                    path.append(curr)
                    curr = visited[curr]
                path.reverse()
                return path

            for neighbor in dummy_board.get_neighbors(current):
                if neighbor not in visited:
                    visited[neighbor] = current
                    queue.append(neighbor)

        return None
