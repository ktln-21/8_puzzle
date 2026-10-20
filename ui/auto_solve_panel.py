"""
Auto-Solve control panel providing interface for AI search (A* and BFS),
step-by-step demonstration, speed control, and playback controls.
"""
import time as pytime
from ursina import Entity, Text, camera, invoke
import config
from config import rgba
from ui.liquid_glass import create_glass_panel, create_glass_button, set_glass_enabled, animate_panel_in

class AutoSolvePanel:
    """
    Panel for controlling and visualizing AI path solving.
    Cleanly docks in place of the right-hand HUD side panel so nothing overlaps.
    """

    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.root = Entity(parent=camera.ui, enabled=False, z=-0.02)

        # Right-aligned side panel (same slot as HUD.side_panel, which hides when this opens)
        self.panel = create_glass_panel(
            parent=self.root,
            position=(0.42, -0.04),
            scale=(0.48, 0.68),
            style="default"
        )

        # Header Title
        self.title = Text(
            parent=self.panel.content,
            text="BẢNG ĐIỀU KHIỂN AI SOLVER",
            position=(0, 0.285),
            origin=(0, 0),
            scale=1.25,
            color=config.ACCENT_CYAN
        )

        # Status & Progress Card
        self.status_card = create_glass_panel(
            parent=self.panel.content,
            position=(0, 0.175),
            scale=(0.42, 0.13),
            style="card"
        )

        self.lbl_status = Text(
            parent=self.status_card.content,
            text="Trạng thái: Sẵn sàng",
            position=(0, 0.026),
            origin=(0, 0),
            scale=0.95,
            color=config.TEXT_PRIMARY_COLOR
        )

        self.lbl_progress = Text(
            parent=self.status_card.content,
            text="Tiến độ: 0 / 0 bước",
            position=(0, -0.026),
            origin=(0, 0),
            scale=0.95,
            color=config.TEXT_SECONDARY_COLOR
        )

        # Algorithm Selector Row (A* vs BFS)
        self.selected_algo = "ASTAR"
        self.btn_algo_astar = create_glass_button(
            text="THUẬT TOÁN: A*",
            position=(-0.105, 0.065),
            scale=(0.19, 0.042),
            callback=lambda: self.set_algorithm("ASTAR"),
            style="primary",
            parent=self.panel.content
        )

        self.btn_algo_bfs = create_glass_button(
            text="THUẬT TOÁN: BFS",
            position=(0.105, 0.065),
            scale=(0.19, 0.042),
            callback=lambda: self.set_algorithm("BFS"),
            style="secondary",
            parent=self.panel.content
        )

        # Speed Selector Row
        speed_w, speed_h = 0.126, 0.040
        self.btn_speed_slow = create_glass_button(
            text="CHẬM 0.5x",
            position=(-0.137, 0.008),
            scale=(speed_w, speed_h),
            callback=lambda: self.set_speed(0.36, "0.5x"),
            style="secondary",
            parent=self.panel.content
        )

        self.btn_speed_med = create_glass_button(
            text="VỪA 1.0x",
            position=(0.0, 0.008),
            scale=(speed_w, speed_h),
            callback=lambda: self.set_speed(0.20, "1.0x"),
            style="primary",
            parent=self.panel.content
        )

        self.btn_speed_fast = create_glass_button(
            text="NHANH 2.0x",
            position=(0.137, 0.008),
            scale=(speed_w, speed_h),
            callback=lambda: self.set_speed(0.10, "2.0x"),
            style="secondary",
            parent=self.panel.content
        )

        btn_w, btn_h = 0.40, 0.048

        # 1. Find Solution Button
        self.btn_find = create_glass_button(
            text="TÌM LỜI GIẢI TỐI ƯU",
            position=(0, -0.058),
            scale=(btn_w, btn_h),
            callback=self.on_find_solution,
            style="action",
            parent=self.panel.content
        )

        # 2. Play / Pause Button
        self.btn_play_pause = create_glass_button(
            text="CHẠY TỰ ĐỘNG",
            position=(0, -0.120),
            scale=(btn_w, btn_h),
            callback=self.on_toggle_play,
            style="primary",
            parent=self.panel.content
        )

        # 3. Step Next & Stop Row
        self.btn_step = create_glass_button(
            text="BƯỚC TIẾP (+1)",
            position=(-0.105, -0.182),
            scale=(0.19, btn_h),
            callback=self.on_step_next,
            style="secondary",
            parent=self.panel.content
        )

        self.btn_stop = create_glass_button(
            text="DỪNG LẠI",
            position=(0.105, -0.182),
            scale=(0.19, btn_h),
            callback=self.on_stop,
            style="danger",
            parent=self.panel.content
        )

        # 4. Close Panel
        self.btn_close = create_glass_button(
            text="ĐÓNG BẢNG AI (CHƠI TAY)",
            position=(0, -0.252),
            scale=(btn_w, btn_h),
            callback=self.on_close,
            style="secondary",
            parent=self.panel.content
        )

        # Solver runtime state
        self.solution_path = []
        self.step_index = 0
        self.is_playing = False
        self.step_delay = 0.20
        self._run_token = 0

    def set_algorithm(self, algo_name: str):
        self.game_manager.sound_manager.play("click")
        self.selected_algo = algo_name
        is_astar = (algo_name == "ASTAR")
        self.btn_algo_astar.color = rgba(95, 60, 170, 220) if is_astar else rgba(55, 38, 92, 205)
        self.btn_algo_bfs.color = rgba(95, 60, 170, 220) if not is_astar else rgba(55, 38, 92, 205)
        self.btn_algo_astar._orig_color = self.btn_algo_astar.color
        self.btn_algo_bfs._orig_color = self.btn_algo_bfs.color
        if not self.is_playing:
            self.compute_solution()

    def set_speed(self, delay: float, label: str):
        self.game_manager.sound_manager.play("click")
        self.step_delay = delay
        for btn, l in [
            (self.btn_speed_slow, "0.5x"),
            (self.btn_speed_med, "1.0x"),
            (self.btn_speed_fast, "2.0x")
        ]:
            col = rgba(95, 60, 170, 220) if l == label else rgba(55, 38, 92, 205)
            btn.color = col
            btn._orig_color = col

    def show(self):
        self.root.enabled = True
        self.reset_state()
        animate_panel_in(self.panel, duration=0.18, direction="scale")
        # Automatically compute solution on open so user can immediately click Play or Step
        self.compute_solution()

    def hide(self):
        self.stop_playback()
        self.root.enabled = False

    def reset_state(self):
        self.stop_playback()
        self.solution_path = []
        self.step_index = 0
        self.lbl_status.text = "Trạng thái: Sẵn sàng"
        self.lbl_status.color = config.TEXT_PRIMARY_COLOR
        self.lbl_progress.text = "Tiến độ: 0 / 0 bước"
        self.btn_play_pause.text = "CHẠY TỰ ĐỘNG"
        set_glass_enabled(self.btn_play_pause, True)
        set_glass_enabled(self.btn_step, True)
        set_glass_enabled(self.btn_stop, False)
        set_glass_enabled(self.btn_find, True)

    def compute_solution(self) -> bool:
        """Runs the selected solver on the current board state."""
        current_state = self.game_manager.board.get_state()
        if self.game_manager.board.is_goal(current_state):
            self.solution_path = []
            self.step_index = 0
            self.lbl_status.text = "Bàn cờ đã ở trạng thái đích!"
            self.lbl_status.color = config.SUCCESS_COLOR
            self.lbl_progress.text = "Tiến độ: 0 / 0 bước"
            set_glass_enabled(self.btn_play_pause, False)
            set_glass_enabled(self.btn_step, False)
            return False

        t0 = pytime.perf_counter()
        solver = (
            self.game_manager.astar_solver
            if self.selected_algo == "ASTAR"
            else self.game_manager.bfs_solver
        )
        path = solver.solve(current_state, config.GOAL_STATE)
        elapsed_ms = (pytime.perf_counter() - t0) * 1000.0

        if path is None:
            self.solution_path = []
            self.lbl_status.text = "Không tìm thấy lời giải!"
            self.lbl_status.color = config.ERROR_COLOR
            set_glass_enabled(self.btn_play_pause, False)
            set_glass_enabled(self.btn_step, False)
            return False

        self.solution_path = path
        self.step_index = 0
        total_steps = len(path)
        algo_label = "A*" if self.selected_algo == "ASTAR" else "BFS"
        self.lbl_status.text = f"Lời giải {algo_label}: {total_steps} bước ({elapsed_ms:.0f}ms)"
        self.lbl_status.color = config.SUCCESS_COLOR
        self.lbl_progress.text = f"Tiến độ: 0 / {total_steps} bước"

        set_glass_enabled(self.btn_play_pause, True)
        set_glass_enabled(self.btn_step, True)
        set_glass_enabled(self.btn_stop, True)
        return True

    def on_find_solution(self):
        self.game_manager.sound_manager.play("click")
        if self.is_playing:
            self.stop_playback()
        self.compute_solution()

    def on_toggle_play(self):
        self.game_manager.sound_manager.play("click")
        if not self.solution_path or self.step_index >= len(self.solution_path):
            if not self.compute_solution():
                return

        if self.is_playing:
            self.pause_playback()
        else:
            self.start_playback()

    def start_playback(self):
        if not self.solution_path or self.step_index >= len(self.solution_path):
            return
        self.is_playing = True
        self._run_token += 1
        current_token = self._run_token
        self.btn_play_pause.text = "TẠM DỪNG CHẠY"
        self.lbl_status.text = "Đang trình diễn tự động..."
        self.lbl_status.color = config.ACCENT_CYAN
        set_glass_enabled(self.btn_stop, True)
        self.game_manager.input_controller.set_input_enabled(False)
        self._schedule_next_step(current_token)

    def pause_playback(self):
        self.is_playing = False
        self._run_token += 1
        self.btn_play_pause.text = "TIẾP TỤC CHẠY"
        self.lbl_status.text = "Đã tạm dừng trình diễn"
        self.lbl_status.color = config.ACCENT_LAVENDER

    def stop_playback(self):
        self.is_playing = False
        self._run_token += 1
        self.btn_play_pause.text = "CHẠY TỰ ĐỘNG"
        self.game_manager.input_controller.set_input_enabled(True)

    def _schedule_next_step(self, token: int):
        if not self.is_playing or token != self._run_token:
            return
        if self.step_index >= len(self.solution_path):
            self.stop_playback()
            self.lbl_status.text = "Đã hoàn thành lời giải!"
            self.lbl_status.color = config.SUCCESS_COLOR
            return

        next_state = self.solution_path[self.step_index]
        self.step_index += 1
        total_steps = len(self.solution_path)
        self.lbl_progress.text = f"Tiến độ: {self.step_index} / {total_steps} bước"

        anim_dur = min(config.MOVE_ANIMATION_DURATION, self.step_delay * 0.8)
        self.game_manager.apply_ai_step(next_state, anim_duration=anim_dur)

        if self.step_index >= total_steps:
            self.is_playing = False
            self._run_token += 1
            self.lbl_status.text = "Đã hoàn thành lời giải!"
            self.lbl_status.color = config.SUCCESS_COLOR
            return

        invoke(lambda: self._schedule_next_step(token), delay=self.step_delay)

    def on_step_next(self):
        self.game_manager.sound_manager.play("click")
        if self.is_playing:
            self.pause_playback()

        if not self.solution_path or self.step_index >= len(self.solution_path):
            if not self.compute_solution():
                return

        next_state = self.solution_path[self.step_index]
        self.step_index += 1
        total_steps = len(self.solution_path)
        self.lbl_progress.text = f"Tiến độ: {self.step_index} / {total_steps} bước"
        self.game_manager.apply_ai_step(next_state)

        if self.step_index >= total_steps:
            self.lbl_status.text = "Đã hoàn thành lời giải!"
            self.lbl_status.color = config.SUCCESS_COLOR
            set_glass_enabled(self.btn_step, False)
            set_glass_enabled(self.btn_play_pause, False)

    def on_stop(self):
        self.game_manager.sound_manager.play("click")
        self.stop_playback()
        # Recompute from current stopped state so user can resume or play manually
        self.compute_solution()

    def on_close(self):
        self.game_manager.sound_manager.play("click")
        self.stop_playback()
        self.hide()
        self.game_manager.close_auto_solve()
