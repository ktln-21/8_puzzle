"""
In-game HUD displaying stats, level information, timer, notifications,
and action buttons.
"""
from ursina import Entity, Text, color, Vec3, camera, invoke, destroy
import config
from ui.liquid_glass import create_glass_panel, create_glass_button, set_glass_enabled
from ui.button_factory import create_button

class HUD:
    """
    In-game heads-up display.
    """

    def __init__(self, input_controller):
        self.input_controller = input_controller
        self.root = Entity(parent=camera.ui, enabled=False)

        # Top Bar Panel
        self.top_panel = create_glass_panel(
            parent=self.root,
            position=(0, 0.44),
            scale=(1.45, 0.08),
            style="default"
        )

        self.title_text = Text(
            parent=self.top_panel.content,
            text="NEON CLOCKWORK 8 PUZZLE",
            position=(-0.65, 0.015),
            scale=1.1,
            color=config.ACCENT_LAVENDER
        )

        self.level_badge = Text(
            parent=self.top_panel.content,
            text="MÀN 01 / 21",
            position=(0.0, 0.015),
            origin=(0, 0),
            scale=1.2,
            color=config.TEXT_PRIMARY_COLOR
        )

        # Top right quick action buttons
        self.btn_pause = create_glass_button(
            text="TẠM DỪNG",
            position=(0.46, 0),
            scale=(0.14, 0.045),
            callback=lambda: self.input_controller.on_button_action("pause"),
            style="secondary",
            parent=self.top_panel.content
        )

        self.btn_menu = create_glass_button(
            text="MENU",
            position=(0.61, 0),
            scale=(0.11, 0.045),
            callback=lambda: self.input_controller.on_button_action("menu"),
            style="secondary",
            parent=self.top_panel.content
        )

        # Side Control Panel (Right)
        self.side_panel = create_glass_panel(
            parent=self.root,
            position=(0.42, -0.04),
            scale=(0.48, 0.68),
            style="default"
        )

        # Level Info Header
        self.lbl_difficulty = Text(
            parent=self.side_panel.content,
            text="ĐỘ KHÓ: RẤT DỄ",
            position=(0, 0.28),
            origin=(0, 0),
            scale=1.15,
            color=config.ACCENT_CYAN
        )

        # Stats Container
        self.stats_panel = create_glass_panel(
            parent=self.side_panel.content,
            position=(0, 0.17),
            scale=(0.42, 0.14),
            style="card"
        )

        self.lbl_moves = Text(
            parent=self.stats_panel.content,
            text="Nước đi: 0",
            position=(-0.16, 0.02),
            scale=1.2,
            color=config.TEXT_PRIMARY_COLOR
        )

        self.lbl_time = Text(
            parent=self.stats_panel.content,
            text="Thời gian: 00:00",
            position=(-0.16, -0.03),
            scale=1.2,
            color=config.TEXT_SECONDARY_COLOR
        )

        # Action Buttons on Side Panel
        btn_w, btn_h = 0.19, 0.05
        btn_y_start = 0.04

        # Row 1: Restart & Undo
        self.btn_restart = create_glass_button(
            text="LÀM LẠI",
            position=(-0.105, btn_y_start),
            scale=(btn_w, btn_h),
            callback=lambda: self.input_controller.on_button_action("restart"),
            style="secondary",
            parent=self.side_panel.content
        )

        self.btn_undo = create_glass_button(
            text="HOÀN TÁC",
            position=(0.105, btn_y_start),
            scale=(btn_w, btn_h),
            callback=lambda: self.input_controller.on_button_action("undo"),
            style="secondary",
            parent=self.side_panel.content
        )

        # Row 2: Auto Solve (Prominent action)
        self.btn_auto_solve = create_glass_button(
            text="TỰ ĐỘNG GIẢI (AI)",
            position=(0, btn_y_start - 0.07),
            scale=(0.40, btn_h),
            callback=lambda: self.input_controller.on_button_action("auto_solve"),
            style="action",
            parent=self.side_panel.content
        )

        # Row 3: Prev & Next level
        self.btn_prev = create_glass_button(
            text="MÀN TRƯỚC",
            position=(-0.105, btn_y_start - 0.14),
            scale=(btn_w, btn_h),
            callback=lambda: self.input_controller.on_button_action("prev_level"),
            style="secondary",
            parent=self.side_panel.content
        )

        self.btn_next = create_glass_button(
            text="MÀN TIẾP",
            position=(0.105, btn_y_start - 0.14),
            scale=(btn_w, btn_h),
            callback=lambda: self.input_controller.on_button_action("next_level"),
            style="secondary",
            parent=self.side_panel.content
        )

        # Row 4: Level Select
        self.btn_select_level = create_glass_button(
            text="CHỌN MÀN CHƠI",
            position=(0, btn_y_start - 0.21),
            scale=(0.40, btn_h),
            callback=lambda: self.input_controller.on_button_action("level_select"),
            style="secondary",
            parent=self.side_panel.content
        )

        # Notification message line
        self.lbl_message = Text(
            parent=self.side_panel.content,
            text="",
            position=(0, -0.28),
            origin=(0, 0),
            scale=0.95,
            color=config.ACCENT_LAVENDER
        )
        self._msg_invoke = None

    def show(self):
        self.root.enabled = True
        self.side_panel.enabled = True

    def hide(self):
        self.root.enabled = False

    def set_side_panel_visible(self, visible: bool):
        self.side_panel.enabled = visible

    def update_moves(self, count: int):
        self.lbl_moves.text = f"Nước đi: {count:03d}"

    def update_timer(self, seconds: float):
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        self.lbl_time.text = f"Thời gian: {mins:02d}:{secs:02d}"

    def update_level(
        self,
        level_id: int,
        total_levels: int,
        difficulty: str = "Dễ",
        is_random_mode: bool = False,
        random_step: int = 1
    ):
        if is_random_mode:
            self.level_badge.text = f"NGẪU NHIÊN {random_step:02d}/{total_levels:02d} (MÀN {level_id:02d})"
        else:
            self.level_badge.text = f"MÀN {level_id:02d} / {total_levels:02d}"
        self.lbl_difficulty.text = f"ĐỘ KHÓ: {difficulty.upper()}"

    def set_buttons_enabled(self, enabled: bool):
        for btn in (self.btn_restart, self.btn_undo, self.btn_auto_solve,
                    self.btn_prev, self.btn_next, self.btn_select_level):
            set_glass_enabled(btn, enabled)

    def show_message(self, message: str, duration: float = 2.0, is_error: bool = False):
        self.lbl_message.text = message
        self.lbl_message.color = config.ERROR_COLOR if is_error else config.ACCENT_LAVENDER

        def clear():
            if self.lbl_message.text == message:
                self.lbl_message.text = ""

        invoke(clear, delay=duration)
