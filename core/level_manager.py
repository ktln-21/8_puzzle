"""
Level manager responsible for loading, validating, and querying level configurations.
"""
import json
import random
from pathlib import Path
from typing import Dict, Any, List, Tuple
import config
from core.board import BoardModel

class LevelManager:
    """
    Manages the 60 predefined levels of the game.
    """

    def __init__(self, levels_path: Path = config.LEVELS_FILE):
        self.levels_path = Path(levels_path)
        self.levels: List[Dict[str, Any]] = []
        self.level_map: Dict[int, Dict[str, Any]] = {}
        self.goal_state = config.GOAL_STATE
        self.load_levels(self.levels_path)

    def load_levels(self, path: Path) -> None:
        """Loads and validates levels from the given JSON path."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Levels file not found at: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.validate_levels(data)

        self.levels = data["levels"]
        self.level_map = {lvl["id"]: lvl for lvl in self.levels}
        if "goal_state" in data:
            self.goal_state = tuple(data["goal_state"])

    def validate_levels(self, data: Dict[str, Any]) -> None:
        """
        Validates schema, level counts, boards, states, and solvability.
        Raises ValueError if data is invalid.
        """
        if not isinstance(data, dict):
            raise ValueError("Level data root must be a JSON object")

        if "levels" not in data or not isinstance(data["levels"], list):
            raise ValueError("Missing 'levels' array in levels.json")

        levels = data["levels"]
        expected_total = config.TOTAL_LEVELS
        if len(levels) != expected_total:
            raise ValueError(f"Expected exactly {expected_total} levels, got {len(levels)}")

        goal_state = tuple(data.get("goal_state", config.GOAL_STATE))
        if not BoardModel.validate_state(goal_state):
            raise ValueError(f"Invalid goal state in levels.json: {goal_state}")

        seen_ids = set()
        seen_states = set()
        prev_optimal = -1

        for lvl in levels:
            lid = lvl.get("id")
            if not isinstance(lid, int) or lid < 1 or lid > expected_total:
                raise ValueError(f"Level id {lid} is invalid (must be 1..{expected_total})")
            if lid in seen_ids:
                raise ValueError(f"Duplicate level id: {lid}")
            seen_ids.add(lid)

            start_state = lvl.get("start_state")
            if not BoardModel.validate_state(start_state):
                raise ValueError(f"Level {lid} has invalid start_state: {start_state}")

            start_tuple = tuple(start_state)
            if start_tuple == goal_state:
                raise ValueError(f"Level {lid} start_state is already at GOAL_STATE")
            if start_tuple in seen_states:
                raise ValueError(f"Duplicate start_state in level {lid}")
            seen_states.add(start_tuple)

            # Check solvability relative to goal
            if not BoardModel.check_solvability(start_tuple, goal_state):
                raise ValueError(f"Level {lid} start_state is unsolvable relative to goal_state!")

            start_board = lvl.get("start_board")
            if not (isinstance(start_board, list) and len(start_board) == 3):
                raise ValueError(f"Level {lid} start_board must be 3x3 list")
            flattened = [val for row in start_board for val in row]
            if flattened != list(start_state):
                raise ValueError(f"Level {lid} start_board does not match start_state")

            optimal = lvl.get("optimal_moves")
            if not isinstance(optimal, int) or optimal <= 0:
                raise ValueError(f"Level {lid} optimal_moves must be positive integer")
            if optimal < prev_optimal:
                raise ValueError(f"Level {lid} optimal_moves ({optimal}) decreased from previous ({prev_optimal})")
            prev_optimal = optimal

    def get_level(self, level_id: int) -> Dict[str, Any]:
        """Retrieves level configuration by ID (1..60)."""
        if level_id not in self.level_map:
            raise KeyError(f"Level ID {level_id} not found")
        return self.level_map[level_id]

    def get_start_state(self, level_id: int) -> Tuple[int, ...]:
        """Returns the starting state tuple for a level."""
        return tuple(self.get_level(level_id)["start_state"])

    def get_level_count(self) -> int:
        """Returns total number of levels (60)."""
        return len(self.levels)

    def generate_random_sequence(self) -> List[int]:
        """Returns a randomized permutation of all 60 level IDs for Random Sequential Mode."""
        ids = list(range(1, len(self.levels) + 1))
        random.shuffle(ids)
        return ids

    def is_unlocked(self, level_id: int, unlocked_max: int) -> bool:
        """Checks if level_id is unlocked."""
        return 1 <= level_id <= unlocked_max

    @staticmethod
    def unlock_next_level(completed_level_id: int, current_unlocked: int) -> int:
        """Calculates next unlocked level up to TOTAL_LEVELS."""
        if completed_level_id >= current_unlocked:
            return min(config.TOTAL_LEVELS, completed_level_id + 1)
        return current_unlocked
