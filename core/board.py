"""
Pure logic for 8-Puzzle board. No UI or engine dependencies.
"""
from typing import Tuple, List, Optional
import config

class BoardModel:
    """
    BoardModel encapsulates the 3x3 8-puzzle board rules, states, and solvability.
    Standard representation is a 9-element tuple where 0 represents the empty space.
    """

    def __init__(self, initial_state: Tuple[int, ...], goal_state: Tuple[int, ...] = config.GOAL_STATE):
        if not self.validate_state(initial_state):
            raise ValueError(f"Invalid initial state: {initial_state}")
        if not self.validate_state(goal_state):
            raise ValueError(f"Invalid goal state: {goal_state}")

        self.initial_state = tuple(initial_state)
        self.goal_state = tuple(goal_state)
        self.current_state = tuple(initial_state)

    @staticmethod
    def validate_state(state) -> bool:
        """Validates that state has exactly 9 elements and is a permutation of 0..8."""
        if not hasattr(state, '__len__') or len(state) != 9:
            return False
        return set(state) == set(range(9))

    def get_state(self) -> Tuple[int, ...]:
        """Returns the current state tuple."""
        return self.current_state

    def set_state(self, state: Tuple[int, ...]) -> None:
        """Sets the current state after validation."""
        if not self.validate_state(state):
            raise ValueError(f"Cannot set invalid state: {state}")
        self.current_state = tuple(state)

    def reset(self) -> None:
        """Resets the board to the initial state."""
        self.current_state = self.initial_state

    @staticmethod
    def index_to_row_col(index: int) -> Tuple[int, int]:
        """Converts a 0..8 index into (row, col) coordinates."""
        if not (0 <= index < 9):
            raise IndexError(f"Index {index} out of board range (0..8)")
        return index // 3, index % 3

    @staticmethod
    def row_col_to_index(row: int, col: int) -> int:
        """Converts (row, col) coordinates to a 0..8 index."""
        if not (0 <= row < 3 and 0 <= col < 3):
            raise IndexError(f"Coordinates ({row}, {col}) out of range")
        return row * 3 + col

    @staticmethod
    def are_adjacent(index_a: int, index_b: int) -> bool:
        """
        Returns True if indices a and b are strictly orthogonal neighbors on the 3x3 grid.
        Prevents row-wrap errors.
        """
        if not (0 <= index_a < 9 and 0 <= index_b < 9):
            return False
        ra, ca = index_a // 3, index_a % 3
        rb, cb = index_b // 3, index_b % 3
        return (abs(ra - rb) + abs(ca - cb)) == 1

    def find_empty(self, state: Optional[Tuple[int, ...]] = None) -> int:
        """Returns the index of the empty slot (0) in the given state or current state."""
        target_state = self.current_state if state is None else state
        return target_state.index(0)

    def can_move(self, tile_index: int) -> bool:
        """Checks if the tile at tile_index can legally slide into the empty slot."""
        if not (0 <= tile_index < 9):
            return False
        empty_index = self.find_empty()
        if tile_index == empty_index:
            return False
        return self.are_adjacent(tile_index, empty_index)

    def move_tile(self, tile_index: int) -> bool:
        """
        Executes a move if tile_index is adjacent to the empty slot.
        Swaps the tile with 0 and returns True. If invalid, returns False.
        """
        if not self.can_move(tile_index):
            return False

        empty_index = self.find_empty()
        new_state = list(self.current_state)
        new_state[empty_index], new_state[tile_index] = new_state[tile_index], new_state[empty_index]
        self.current_state = tuple(new_state)
        return True

    def get_valid_moves(self, state: Optional[Tuple[int, ...]] = None) -> List[int]:
        """Returns list of tile indices that can legally move in the state."""
        target_state = self.current_state if state is None else state
        empty_index = target_state.index(0)
        er, ec = empty_index // 3, empty_index % 3
        valid_indices = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = er + dr, ec + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                valid_indices.append(nr * 3 + nc)
        return valid_indices

    def get_neighbors(self, state: Optional[Tuple[int, ...]] = None) -> List[Tuple[int, ...]]:
        """
        Returns all valid next state tuples reachable in one legal move from state.
        Never mutates the current state.
        """
        target_state = self.current_state if state is None else tuple(state)
        empty_idx = target_state.index(0)
        er, ec = empty_idx // 3, empty_idx % 3
        neighbors = []

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = er + dr, ec + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                swap_idx = nr * 3 + nc
                state_list = list(target_state)
                state_list[empty_idx], state_list[swap_idx] = state_list[swap_idx], state_list[empty_idx]
                neighbors.append(tuple(state_list))

        return neighbors

    def is_goal(self, state: Optional[Tuple[int, ...]] = None) -> bool:
        """Returns True if the state matches the defined goal state."""
        target_state = self.current_state if state is None else tuple(state)
        return target_state == self.goal_state

    @staticmethod
    def count_inversions(state: Tuple[int, ...]) -> int:
        """Counts inversions among numbers 1..8, ignoring 0."""
        nums = [x for x in state if x != 0]
        inv = 0
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] > nums[j]:
                    inv += 1
        return inv

    @classmethod
    def check_solvability(cls, state: Tuple[int, ...], goal_state: Tuple[int, ...] = config.GOAL_STATE) -> bool:
        """
        Determines if state can reach goal_state in 3x3 sliding puzzle.
        In 3x3 grids, any legal slide preserves the parity of inversions (excluding 0).
        """
        if not cls.validate_state(state) or not cls.validate_state(goal_state):
            return False
        return (cls.count_inversions(state) % 2) == (cls.count_inversions(goal_state) % 2)

    def is_solvable(self, state: Optional[Tuple[int, ...]] = None, goal_state: Optional[Tuple[int, ...]] = None) -> bool:
        """Instance method for solvability check."""
        target_state = self.current_state if state is None else state
        target_goal = self.goal_state if goal_state is None else goal_state
        return self.check_solvability(target_state, target_goal)
