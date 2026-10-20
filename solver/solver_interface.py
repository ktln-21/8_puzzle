"""
Abstract base contract for 8-Puzzle solvers.
"""
from typing import Tuple, List, Optional
import config

class SolverInterface:
    """
    Interface definition for all 8-puzzle solvers.
    Decoupled from UI and game loop.
    """

    def solve(
        self,
        start_state: Tuple[int, ...],
        goal_state: Tuple[int, ...] = config.GOAL_STATE
    ) -> Optional[List[Tuple[int, ...]]]:
        """
        Solves the puzzle from start_state to goal_state.
        Returns a list of consecutive states representing the path (excluding start_state,
        including goal_state).
        Returns [] if start_state == goal_state.
        Returns None if no solution exists or cancelled.
        """
        raise NotImplementedError

    def cancel(self) -> None:
        """Signals solver to abort execution if search is underway."""
        raise NotImplementedError
