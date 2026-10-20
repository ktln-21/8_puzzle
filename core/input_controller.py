"""
Input controller: bridges user input events (clicks, keypresses) to GameManager.
Manages input locking during animations and solver execution.
"""
from typing import Any

class InputController:
    """
    Decouples raw player inputs from game logic state.
    """

    def __init__(self, game_manager: Any):
        self.game_manager = game_manager
        self.input_enabled = True

    def set_input_enabled(self, enabled: bool):
        """Enables or locks board user input."""
        self.input_enabled = enabled

    def on_tile_clicked(self, tile_index: int):
        """Dispatched when a tile on the board is clicked."""
        if not self.input_enabled:
            return
        self.game_manager.request_move(tile_index, source="player")

    def on_button_action(self, action_name: str, **kwargs):
        """Dispatched when a HUD or menu action button is triggered."""
        if action_name == "pause":
            self.game_manager.toggle_pause()
        elif action_name == "restart":
            self.game_manager.restart_level()
        elif action_name == "undo":
            self.game_manager.undo_move()
        elif action_name == "auto_solve":
            self.game_manager.open_auto_solve()
        elif action_name == "next_level":
            self.game_manager.next_level()
        elif action_name == "prev_level":
            self.game_manager.prev_level()
        elif action_name == "menu":
            self.game_manager.show_main_menu()
        elif action_name == "level_select":
            self.game_manager.show_level_select()
        elif action_name == "settings":
            self.game_manager.show_settings()

    def handle_key(self, key: str):
        """Handles keyboard shortcuts."""
        if key == "escape":
            self.game_manager.toggle_pause()
        elif key in ("u", "z") and self.input_enabled:
            self.game_manager.undo_move()
        elif key == "r" and self.input_enabled:
            self.game_manager.restart_level()
