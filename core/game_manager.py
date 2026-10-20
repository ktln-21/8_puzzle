"""
GameManager: central coordinator for state transitions, board logic, UI screens,
move validations, victory conditions, random 60-level mode, and data persistence.
"""
from typing import List, Tuple, Optional
from enum import Enum
from ursina import Entity, camera, Vec3, invoke
import config
from core.board import BoardModel
from core.level_manager import LevelManager
from core.save_manager import SaveManager
from core.sound_manager import SoundManager
from core.tile_view import TileView
from core.input_controller import InputController
from ui.liquid_glass import create_glass_panel
from ui.hud import HUD
from ui.main_menu import MainMenu
from ui.level_select import LevelSelectMenu
from ui.pause_menu import PauseMenu
from ui.result_panel import ResultPanel
from ui.auto_solve_panel import AutoSolvePanel
from ui.settings_menu import SettingsMenu
from solver.astar_solver import AStarSolver
from solver.bfs_solver import BFSSolver

class GameState(Enum):
    MENU = "MENU"
    LEVEL_SELECT = "LEVEL_SELECT"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    ANIMATING = "ANIMATING"
    SOLVING = "SOLVING"
    LEVEL_COMPLETE = "LEVEL_COMPLETE"
    GAME_COMPLETE = "GAME_COMPLETE"

class GameManager:
    """
    Central controller orchestrating gameplay, view entities, and solvers.
    """

    def __init__(self):
        # 1. Subsystems
        self.save_manager = SaveManager()
        self.level_manager = LevelManager()
        self.sound_manager = SoundManager(self.save_manager)
        self.input_controller = InputController(self)
        self.astar_solver = AStarSolver()
        self.bfs_solver = BFSSolver()

        # 2. State & Metrics
        self.state = GameState.MENU
        self.current_level_id = 1
        self.current_moves = 0
        self.elapsed_seconds = 0.0
        self.move_history: List[Tuple[int, ...]] = []
        self.is_animating_move = False

        # Random Sequential 60-Level Mode tracking
        self.is_random_mode = False
        self.random_sequence: List[int] = []
        self.random_index = 0

        # 3. Board Logical Model
        lvl1_state = self.level_manager.get_start_state(1)
        self.board = BoardModel(lvl1_state, config.GOAL_STATE)

        # 4. Board Visual Container
        self.board_root = Entity(parent=camera.ui, enabled=False)

        # Large Glass Frame for 3x3 Board
        self.board_frame = create_glass_panel(
            parent=self.board_root,
            position=(-0.20, -0.04),
            scale=(0.58, 0.58),
            style="default"
        )

        # Precompute 3x3 Grid Positions (centered inside frame)
        self.grid_spacing = 0.16
        self.board_center_x = -0.20
        self.board_center_y = -0.04

        self.grid_positions: List[Vec3] = []
        for idx in range(9):
            r, c = idx // 3, idx % 3
            gx = self.board_center_x + (c - 1) * self.grid_spacing
            gy = self.board_center_y - (r - 1) * self.grid_spacing
            self.grid_positions.append(Vec3(gx, gy, -0.02))

        # Instantiate 9 TileViews
        self.tile_views: List[TileView] = []
        for idx in range(9):
            tv = TileView(
                grid_index=idx,
                value=lvl1_state[idx],
                position=self.grid_positions[idx],
                parent=self.board_root,
                on_click_callback=self.input_controller.on_tile_clicked
            )
            self.tile_views.append(tv)

        # 5. UI Overlays and Menus
        self.hud = HUD(self.input_controller)
        self.main_menu = MainMenu(self)
        self.level_select = LevelSelectMenu(self)
        self.pause_menu = PauseMenu(self)
        self.result_panel = ResultPanel(self)
        self.auto_solve_panel = AutoSolvePanel(self)
        self.settings_menu = SettingsMenu(self)

    def _hide_all_overlays(self):
        """Ensures all menus and popups are cleanly hidden before switching screens."""
        self.main_menu.hide()
        self.level_select.hide()
        self.pause_menu.hide()
        self.result_panel.hide()
        self.auto_solve_panel.hide()
        self.settings_menu.hide()

    def show_main_menu(self):
        """Displays main menu and hides board / HUD."""
        self.state = GameState.MENU
        self.board_root.enabled = False
        self.hud.hide()
        self._hide_all_overlays()

        save_data = self.save_manager.load_progress()
        has_save = save_data.get("current_moves", 0) > 0 or len(save_data.get("completed_levels", [])) > 0
        self.main_menu.show(has_save=has_save)

    def resume_saved_or_new_game(self):
        """Resumes campaign game from last saved level or starts level 1."""
        self.is_random_mode = False
        save_data = self.save_manager.load_progress()
        level_id = save_data.get("current_level", 1)
        curr_state = save_data.get("current_state")

        self._hide_all_overlays()
        self.start_level(level_id, resume_state=curr_state, is_random_mode=False)

    def start_random_60_mode(self):
        """Starts or resumes a randomized sequential playthrough of all 60 levels."""
        save_data = self.save_manager.load_progress()
        saved_seq = save_data.get("random_sequence", [])
        saved_idx = save_data.get("random_index", 0)

        if len(saved_seq) == config.TOTAL_LEVELS and 0 <= saved_idx < config.TOTAL_LEVELS:
            self.random_sequence = saved_seq
            self.random_index = saved_idx
        else:
            self.random_sequence = self.level_manager.generate_random_sequence()
            self.random_index = 0
            save_data["random_sequence"] = self.random_sequence
            save_data["random_index"] = 0
            self.save_manager.save_progress(save_data)

        self.is_random_mode = True
        target_level_id = self.random_sequence[self.random_index]
        self._hide_all_overlays()
        self.start_level(target_level_id, resume_state=None, is_random_mode=True)
        self.hud.show_message(f"Chế độ ngẫu nhiên 60 bàn: Bàn {self.random_index + 1:02d}/60", duration=2.5)

    def show_level_select(self):
        """Shows paginated 60-level selection menu."""
        self.state = GameState.LEVEL_SELECT
        self.board_root.enabled = False
        self.hud.hide()
        self._hide_all_overlays()
        self.level_select.show()

    def show_settings(self, from_menu: str = "main_menu"):
        """Shows settings configuration menu without overlapping other modals."""
        if from_menu == "pause":
            self.pause_menu.hide()
        elif from_menu == "main_menu":
            self.main_menu.hide()
        self.settings_menu.show(from_menu=from_menu)

    def start_level(self, level_id: int, resume_state=None, is_random_mode: Optional[bool] = None):
        """Initializes and starts a level."""
        self._hide_all_overlays()
        if is_random_mode is not None:
            self.is_random_mode = is_random_mode

        self.current_level_id = level_id
        lvl_info = self.level_manager.get_level(level_id)

        if (
            not self.is_random_mode
            and resume_state
            and BoardModel.validate_state(resume_state)
            and not self.board.is_goal(resume_state)
        ):
            initial_state = tuple(resume_state)
            save_data = self.save_manager.load_progress()
            self.current_moves = save_data.get("current_moves", 0)
            self.elapsed_seconds = save_data.get("elapsed_seconds", 0.0)
        else:
            initial_state = tuple(lvl_info["start_state"])
            self.current_moves = 0
            self.elapsed_seconds = 0.0

        self.move_history = []
        self.is_animating_move = False
        self.board.set_state(initial_state)

        # Update tile views
        for idx in range(9):
            val = initial_state[idx]
            tv = self.tile_views[idx]
            tv.grid_index = idx
            tv.set_value(val)
            tv.set_position(self.grid_positions[idx], animated=False)
            tv.set_visual_state("default")

        self.board_root.enabled = True
        self.hud.show()
        self.hud.set_side_panel_visible(True)
        self.hud.update_level(
            level_id,
            config.TOTAL_LEVELS,
            lvl_info.get("difficulty", "Dễ"),
            is_random_mode=self.is_random_mode,
            random_step=(self.random_index + 1)
        )
        self.hud.update_moves(self.current_moves)
        self.hud.update_timer(self.elapsed_seconds)
        self.hud.set_buttons_enabled(True)

        self.state = GameState.PLAYING
        self.input_controller.set_input_enabled(True)
        self.update_tile_hints()
        self.save_current_progress()

    def restart_level(self):
        """Restarts the current level back to its start_state."""
        self.start_level(self.current_level_id, resume_state=None, is_random_mode=self.is_random_mode)

    def undo_move(self):
        """Reverts board to previous state in history."""
        if self.state != GameState.PLAYING or not self.move_history or self.is_animating_move:
            return

        prev_state = self.move_history.pop()
        self.board.set_state(prev_state)
        self.current_moves += 1  # Fair move count tracking
        self.hud.update_moves(self.current_moves)

        # Sync views immediately
        for idx in range(9):
            val = prev_state[idx]
            self.tile_views[idx].grid_index = idx
            self.tile_views[idx].set_value(val)
            self.tile_views[idx].set_position(self.grid_positions[idx], animated=False)

        self.sound_manager.play("move")
        self.update_tile_hints()
        self.save_current_progress()

    def toggle_pause(self):
        """Toggles game pause overlay."""
        if self.state == GameState.PLAYING:
            if self.auto_solve_panel.is_playing:
                self.auto_solve_panel.pause_playback()
            self.state = GameState.PAUSED
            self.input_controller.set_input_enabled(False)
            self.pause_menu.show()
        elif self.state == GameState.PAUSED:
            self.pause_menu.hide()
            self.settings_menu.hide()
            self.state = GameState.PLAYING
            if not self.auto_solve_panel.root.enabled:
                self.input_controller.set_input_enabled(True)

    def request_move(self, tile_index: int, source: str = "player") -> bool:
        """Processes player's request to slide a tile."""
        if self.state != GameState.PLAYING or self.is_animating_move:
            return False

        if not self.board.can_move(tile_index):
            self.tile_views[tile_index].play_invalid_feedback()
            self.sound_manager.play("invalid")
            self.hud.show_message("Ô không kề ô trống!", is_error=True)
            return False

        # Legal move
        old_state = self.board.get_state()
        self.move_history.append(old_state)

        empty_index = self.board.find_empty()
        self.board.move_tile(tile_index)

        self.is_animating_move = True
        self.input_controller.set_input_enabled(False)

        # Slide animation
        moving_tv = self.tile_views[tile_index]
        empty_tv = self.tile_views[empty_index]

        moving_tv.set_position(self.grid_positions[empty_index], animated=True)
        empty_tv.set_position(self.grid_positions[tile_index], animated=False)

        # Swap tracking in tile_views list
        self.tile_views[tile_index], self.tile_views[empty_index] = self.tile_views[empty_index], self.tile_views[tile_index]
        self.tile_views[tile_index].grid_index = tile_index
        self.tile_views[empty_index].grid_index = empty_index

        self.current_moves += 1
        self.hud.update_moves(self.current_moves)
        self.sound_manager.play("move")

        def on_anim_done():
            self.is_animating_move = False
            self.input_controller.set_input_enabled(True)
            self.update_tile_hints()
            self.save_current_progress()
            self.check_win()

        invoke(on_anim_done, delay=config.MOVE_ANIMATION_DURATION)
        return True

    def apply_ai_step(self, next_state: Tuple[int, ...], anim_duration: float = config.MOVE_ANIMATION_DURATION):
        """Applies a single state from AI solver with smooth slide animation."""
        curr_state = self.board.get_state()
        if curr_state == next_state:
            return

        e_curr = curr_state.index(0)
        e_next = next_state.index(0)
        tile_to_move = e_next  # The tile at e_next slides into e_curr

        self.move_history.append(curr_state)
        self.board.set_state(next_state)

        moving_tv = self.tile_views[tile_to_move]
        empty_tv = self.tile_views[e_curr]

        moving_tv.set_position(self.grid_positions[e_curr], animated=True, duration=anim_duration)
        empty_tv.set_position(self.grid_positions[tile_to_move], animated=False)

        self.tile_views[tile_to_move], self.tile_views[e_curr] = self.tile_views[e_curr], self.tile_views[tile_to_move]
        self.tile_views[tile_to_move].grid_index = tile_to_move
        self.tile_views[e_curr].grid_index = e_curr

        self.current_moves += 1
        self.hud.update_moves(self.current_moves)
        self.sound_manager.play("move")

        if self.board.is_goal():
            invoke(lambda: self.complete_level(is_ai=True), delay=anim_duration)

    def update_tile_hints(self):
        """Highlights valid movable tiles if setting is enabled."""
        if self.state != GameState.PLAYING:
            return
        settings = self.save_manager.load_settings()
        show_hints = settings.get("show_valid_move_hint", True)
        valid_indices = set(self.board.get_valid_moves())

        for idx, tv in enumerate(self.tile_views):
            if tv.value != 0:
                if show_hints and idx in valid_indices:
                    tv.set_visual_state("valid")
                else:
                    tv.set_visual_state("default")

    def check_win(self):
        """Checks if current board reached GOAL_STATE."""
        if self.board.is_goal():
            self.complete_level(is_ai=False)

    def complete_level(self, is_ai: bool = False):
        """Handles stage completion victory sequence."""
        if self.state == GameState.LEVEL_COMPLETE:
            return
        self.state = GameState.LEVEL_COMPLETE
        self.input_controller.set_input_enabled(False)

        # Close AutoSolve panel if open so ResultPanel does not overlap it
        if self.auto_solve_panel.root.enabled:
            self.auto_solve_panel.hide()
            self.hud.set_side_panel_visible(True)

        self.sound_manager.play("win")

        # 1. Clockwise glow sweep around the 8 outer tiles
        clockwise_order = [0, 1, 2, 5, 8, 7, 6, 3]
        for step_idx, grid_idx in enumerate(clockwise_order):
            delay = step_idx * config.WIN_STEP_DELAY
            self.tile_views[grid_idx].play_win_effect(delay=delay)

        # 2. Update save data
        save_data = self.save_manager.load_progress()
        completed = set(save_data.get("completed_levels", []))
        completed.add(self.current_level_id)
        save_data["completed_levels"] = sorted(list(completed))

        # Unlock next level
        current_unlocked = save_data.get("unlocked_level", 1)
        save_data["unlocked_level"] = LevelManager.unlock_next_level(self.current_level_id, current_unlocked)

        # Update best records (only for human player)
        is_new_record = False
        if not is_ai:
            records = {r["level_id"]: r for r in save_data.get("best_records", []) if "level_id" in r}
            current_rec = records.get(self.current_level_id)
            if current_rec is None or self.current_moves < current_rec["best_moves"]:
                records[self.current_level_id] = {
                    "level_id": self.current_level_id,
                    "best_moves": self.current_moves,
                    "best_time_seconds": round(self.elapsed_seconds, 2)
                }
                is_new_record = True
            save_data["best_records"] = list(records.values())

        if self.current_level_id >= config.TOTAL_LEVELS:
            save_data["game_completed"] = True

        # If in Random Mode, advance saved random_index for next stage
        completed_random_step = self.random_index + 1
        if self.is_random_mode:
            if self.random_index + 1 < config.TOTAL_LEVELS:
                save_data["random_index"] = self.random_index + 1
            else:
                # Completed all 60 random stages! Reset for next run
                save_data["random_sequence"] = []
                save_data["random_index"] = 0

        save_data["current_moves"] = 0
        save_data["elapsed_seconds"] = 0.0
        self.save_manager.save_progress(save_data)

        # 3. Present victory modal after clockwise animation finishes
        total_anim_time = (len(clockwise_order) * config.WIN_STEP_DELAY) + 0.35
        lvl_info = self.level_manager.get_level(self.current_level_id)
        opt_moves = lvl_info.get("optimal_moves", 0)

        def show_result():
            self.result_panel.show_level_result(
                level_id=self.current_level_id,
                moves=self.current_moves,
                elapsed_seconds=self.elapsed_seconds,
                optimal_moves=opt_moves,
                is_new_record=is_new_record,
                is_random_mode=self.is_random_mode,
                random_step=completed_random_step
            )

        invoke(show_result, delay=total_anim_time)

    def advance_after_win(self):
        """Advances to next stage in either Random Sequential 60 Mode or Campaign Mode."""
        if self.is_random_mode:
            if self.random_index + 1 < len(self.random_sequence):
                self.random_index += 1
                next_lid = self.random_sequence[self.random_index]
                self.start_level(next_lid, is_random_mode=True)
            else:
                self.show_main_menu()
        else:
            target = min(config.TOTAL_LEVELS, self.current_level_id + 1)
            self.start_level(target, is_random_mode=False)

    def next_level(self):
        """Advances to next level (or next random stage in Random Mode)."""
        if self.is_random_mode:
            if self.random_index + 1 < len(self.random_sequence):
                self.random_index += 1
                self.start_level(self.random_sequence[self.random_index], is_random_mode=True)
            else:
                self.hud.show_message("Đang ở bàn cuối (60/60)!", is_error=True)
            return

        save_data = self.save_manager.load_progress()
        unlocked = save_data.get("unlocked_level", 1)
        target = self.current_level_id + 1
        if target <= unlocked and target <= config.TOTAL_LEVELS:
            self.start_level(target, is_random_mode=False)
        else:
            self.hud.show_message(f"Màn {target:02d} chưa mở khóa!", is_error=True)

    def prev_level(self):
        """Goes to previous level (or previous random stage in Random Mode)."""
        if self.is_random_mode:
            if self.random_index > 0:
                self.random_index -= 1
                self.start_level(self.random_sequence[self.random_index], is_random_mode=True)
            else:
                self.hud.show_message("Đang ở bàn đầu tiên (01/60)!", is_error=True)
            return

        target = max(1, self.current_level_id - 1)
        self.start_level(target, is_random_mode=False)

    def open_auto_solve(self):
        """Opens auto solver control panel cleanly in place of the right HUD panel."""
        if self.state != GameState.PLAYING:
            return
        self.hud.set_side_panel_visible(False)
        self.auto_solve_panel.show()

    def close_auto_solve(self):
        """Closes auto solver control panel and restores manual HUD panel."""
        self.auto_solve_panel.hide()
        self.hud.set_side_panel_visible(True)
        self.input_controller.set_input_enabled(True)
        self.update_tile_hints()

    def update_timer(self, dt: float):
        """Updates gameplay timer every frame."""
        if self.state == GameState.PLAYING and not self.is_animating_move:
            self.elapsed_seconds += dt
            self.hud.update_timer(self.elapsed_seconds)

    def save_current_progress(self):
        """Persists current game state to save.json."""
        save_data = self.save_manager.load_progress()
        if not self.is_random_mode:
            save_data["current_level"] = self.current_level_id
            save_data["current_state"] = list(self.board.get_state())
            save_data["current_moves"] = self.current_moves
            save_data["elapsed_seconds"] = round(self.elapsed_seconds, 2)
        else:
            save_data["random_sequence"] = self.random_sequence
            save_data["random_index"] = self.random_index
        self.save_manager.save_progress(save_data)
