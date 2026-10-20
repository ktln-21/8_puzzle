"""
Save and settings management with atomic file writing and schema validation.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any
import config
from core.board import BoardModel

logger = logging.getLogger(__name__)

DEFAULT_PROGRESS: Dict[str, Any] = {
    "schema_version": 1,
    "unlocked_level": 1,
    "completed_levels": [],
    "current_level": 1,
    "current_state": list(config.GOAL_STATE),
    "current_moves": 0,
    "elapsed_seconds": 0.0,
    "best_records": [],
    "game_completed": False,
    "random_sequence": [],
    "random_index": 0
}

DEFAULT_SETTINGS: Dict[str, Any] = {
    "schema_version": 1,
    "sound_enabled": True,
    "music_enabled": True,
    "sound_volume": 0.7,
    "music_volume": 0.4,
    "animation_speed": 1.0,
    "panel_alpha": 0.28,
    "glass_glow_enabled": True,
    "background_particles_enabled": True,
    "reduced_motion": False,
    "show_valid_move_hint": True,
    "window_width": 1280,
    "window_height": 720
}

class SaveManager:
    """
    Handles persisting and loading game progress and user settings.
    Ensures atomic writes and graceful fallback on corrupted data.
    """

    def __init__(self, save_path: Path = config.SAVE_FILE, settings_path: Path = config.SETTINGS_FILE):
        self.save_path = Path(save_path)
        self.settings_path = Path(settings_path)
        self.save_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def load_json(path: Path, default_data: Dict[str, Any]) -> Dict[str, Any]:
        """Loads JSON file. Returns default_data if missing or corrupted."""
        path = Path(path)
        if not path.exists():
            return default_data.copy()

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                logger.warning(f"File {path} root is not a dict. Falling back to default.")
                return default_data.copy()
        except Exception as e:
            logger.error(f"Failed to read JSON from {path}: {e}")
            try:
                backup = path.with_suffix(".corrupt.bak")
                path.rename(backup)
                logger.info(f"Backed up corrupt file to {backup}")
            except Exception:
                pass
            return default_data.copy()

    @staticmethod
    def save_json_atomic(path: Path, data: Dict[str, Any]) -> bool:
        """Writes JSON to a temporary file first, then atomically replaces target."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(".tmp.json")

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            temp_path.replace(path)
            return True
        except Exception as e:
            logger.error(f"Failed to atomically save JSON to {path}: {e}")
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
            return False

    def validate_progress(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validates progress fields and returns sanitized progress dictionary."""
        valid_data = DEFAULT_PROGRESS.copy()
        max_lvl = config.TOTAL_LEVELS

        unlocked = data.get("unlocked_level", 1)
        if isinstance(unlocked, int) and 1 <= unlocked <= max_lvl:
            valid_data["unlocked_level"] = unlocked

        curr_lvl = data.get("current_level", 1)
        if isinstance(curr_lvl, int) and 1 <= curr_lvl <= max_lvl:
            valid_data["current_level"] = curr_lvl

        completed = data.get("completed_levels", [])
        if isinstance(completed, list):
            valid_data["completed_levels"] = [
                lvl for lvl in completed if isinstance(lvl, int) and 1 <= lvl <= max_lvl
            ]

        curr_state = data.get("current_state")
        if curr_state and BoardModel.validate_state(curr_state):
            valid_data["current_state"] = list(curr_state)
        else:
            valid_data["current_state"] = list(config.GOAL_STATE)

        moves = data.get("current_moves", 0)
        valid_data["current_moves"] = max(0, int(moves)) if isinstance(moves, (int, float)) else 0

        seconds = data.get("elapsed_seconds", 0.0)
        valid_data["elapsed_seconds"] = max(0.0, float(seconds)) if isinstance(seconds, (int, float)) else 0.0

        records = data.get("best_records", [])
        if isinstance(records, list):
            clean_records = []
            for r in records:
                if isinstance(r, dict) and "level_id" in r:
                    clean_records.append({
                        "level_id": int(r["level_id"]),
                        "best_moves": int(r.get("best_moves", 0)),
                        "best_time_seconds": round(float(r.get("best_time_seconds", 0.0)), 2)
                    })
            valid_data["best_records"] = clean_records

        valid_data["game_completed"] = bool(data.get("game_completed", False))

        rand_seq = data.get("random_sequence", [])
        if isinstance(rand_seq, list) and all(isinstance(x, int) and 1 <= x <= max_lvl for x in rand_seq):
            valid_data["random_sequence"] = rand_seq
        else:
            valid_data["random_sequence"] = []

        rand_idx = data.get("random_index", 0)
        if isinstance(rand_idx, int) and 0 <= rand_idx < max_lvl:
            valid_data["random_index"] = rand_idx
        else:
            valid_data["random_index"] = 0

        return valid_data

    def load_progress(self) -> Dict[str, Any]:
        """Loads and validates saved game progress."""
        raw = self.load_json(self.save_path, DEFAULT_PROGRESS)
        return self.validate_progress(raw)

    def save_progress(self, progress_data: Dict[str, Any]) -> bool:
        """Validates and saves game progress atomically."""
        validated = self.validate_progress(progress_data)
        return self.save_json_atomic(self.save_path, validated)

    def validate_settings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validates and clamps settings values to valid ranges."""
        valid_settings = DEFAULT_SETTINGS.copy()

        for key, val in data.items():
            if key in ("sound_enabled", "music_enabled", "glass_glow_enabled",
                        "background_particles_enabled", "reduced_motion", "show_valid_move_hint"):
                valid_settings[key] = bool(val)
            elif key in ("sound_volume", "music_volume", "panel_alpha"):
                if isinstance(val, (int, float)):
                    valid_settings[key] = max(0.0, min(1.0, float(val)))
            elif key == "animation_speed":
                if isinstance(val, (int, float)):
                    valid_settings[key] = max(0.2, min(3.0, float(val)))
            elif key in ("window_width", "window_height"):
                if isinstance(val, int) and val > 200:
                    valid_settings[key] = val

        return valid_settings

    def load_settings(self) -> Dict[str, Any]:
        """Loads and validates user settings."""
        raw = self.load_json(self.settings_path, DEFAULT_SETTINGS)
        return self.validate_settings(raw)

    def save_settings(self, settings_data: Dict[str, Any]) -> bool:
        """Validates and saves user settings atomically."""
        validated = self.validate_settings(settings_data)
        return self.save_json_atomic(self.settings_path, validated)
