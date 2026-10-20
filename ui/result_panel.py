"""
Result and victory modal displayed upon solving a level or completing the game.
"""
from ursina import Entity, Text, camera
import config
from config import rgba
from ui.liquid_glass import create_glass_panel, create_glass_button, animate_panel_in

class ResultPanel:
    """
    Victory modal displayed when a stage is solved.
    Placed on top modal layer (z=-0.15) with a full-screen click-blocking dimmer.
    """

    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.root = Entity(parent=camera.ui, enabled=False, z=-0.15)

        # Full-screen dark dimmer that hides background clutter and blocks clicks
        self.dimmer = Entity(
            parent=self.root,
            model="quad",
            scale=(2.5, 2.0),
            position=(0, 0, 0.01),
            color=rgba(10, 6, 20, 220),
            collider="box"
        )

        # Glass Panel
        self.panel = create_glass_panel(
            parent=self.root,
            position=(0, 0),
            scale=(0.58, 0.66),
            style="modal"
        )

        # Header Title
        self.title = Text(
            parent=self.panel.content,
            text="CHIẾN THẮNG!",
            position=(0, 0.24),
            origin=(0, 0),
            scale=1.7,
            color=config.SUCCESS_COLOR
        )

        self.subtitle = Text(
            parent=self.panel.content,
            text="HOÀN THÀNH MÀN 01",
            position=(0, 0.17),
            origin=(0, 0),
            scale=1.15,
            color=config.ACCENT_LAVENDER
        )

        # Stats Card
        self.stats_card = create_glass_panel(
            parent=self.panel.content,
            position=(0, 0.05),
            scale=(0.46, 0.15),
            style="card"
        )

        self.lbl_moves = Text(
            parent=self.stats_card.content,
            text="Số nước đi: 0 (Tối ưu: 0)",
            position=(0, 0.03),
            origin=(0, 0),
            scale=1.05,
            color=config.TEXT_PRIMARY_COLOR
        )

        self.lbl_time = Text(
            parent=self.stats_card.content,
            text="Thời gian: 00:00",
            position=(0, -0.03),
            origin=(0, 0),
            scale=1.05,
            color=config.TEXT_SECONDARY_COLOR
        )

        self.lbl_record = Text(
            parent=self.panel.content,
            text=">> KY LUC MOI! <<",
            position=(0, -0.06),
            origin=(0, 0),
            scale=1.1,
            color=config.ACCENT_CYAN,
            enabled=False
        )

        btn_w, btn_h = 0.40, 0.054

        # 1. Next Level
        self.btn_next = create_glass_button(
            text="MÀN TIẾP THEO",
            position=(0, -0.13),
            scale=(btn_w, btn_h),
            callback=self.on_next_level,
            style="primary",
            parent=self.panel.content
        )

        # 2. Replay
        self.btn_replay = create_glass_button(
            text="CHƠI LẠI MÀN NÀY",
            position=(0, -0.20),
            scale=(btn_w, btn_h),
            callback=self.on_replay,
            style="secondary",
            parent=self.panel.content
        )

        # 3. Select Level
        self.btn_levels = create_glass_button(
            text="CHỌN MÀN KHÁC",
            position=(0, -0.27),
            scale=(btn_w, btn_h),
            callback=self.on_level_select,
            style="secondary",
            parent=self.panel.content
        )

        self.current_level_id = 1

    def show_level_result(
        self,
        level_id: int,
        moves: int,
        elapsed_seconds: float,
        optimal_moves: int,
        is_new_record: bool = False,
        is_random_mode: bool = False,
        random_step: int = 1
    ):
        self.current_level_id = level_id
        mins = int(elapsed_seconds) // 60
        secs = int(elapsed_seconds) % 60
        total_lvls = config.TOTAL_LEVELS

        if is_random_mode:
            if random_step >= total_lvls:
                self.title.text = "PHÁ ĐẢO 60 BÀN NGẪU NHIÊN!"
                self.subtitle.text = f"HOÀN THÀNH BÀN {total_lvls}/{total_lvls} (MÀN GỐC {level_id:02d})"
                self.btn_next.text = "VỀ MENU CHÍNH"
                self.btn_next.on_click = self.on_menu
            else:
                self.title.text = "CHIẾN THẮNG!"
                self.subtitle.text = f"NGẪU NHIÊN: BÀN {random_step:02d}/{total_lvls} (MÀN {level_id:02d})"
                self.btn_next.text = f"BÀN NGẪU NHIÊN TIẾP ({random_step + 1:02d}/{total_lvls})"
                self.btn_next.on_click = self.on_next_level
        else:
            if level_id >= total_lvls:
                self.title.text = "PHÁ ĐẢO TOÀN BỘ!"
                self.subtitle.text = f"CHÚC MỪNG BẠN ĐÃ VƯỢT QUA {total_lvls} MÀN CHƠI!"
                self.btn_next.text = "CHỌN MÀN CHƠI"
                self.btn_next.on_click = self.on_level_select
            else:
                self.title.text = "CHIẾN THẮNG!"
                self.subtitle.text = f"HOÀN THÀNH MÀN {level_id:02d} / {total_lvls:02d}"
                self.btn_next.text = "MÀN TIẾP THEO"
                self.btn_next.on_click = self.on_next_level

        self.lbl_moves.text = f"Số nước đi: {moves} (Tối ưu: {optimal_moves})"
        self.lbl_time.text = f"Thời gian: {mins:02d}:{secs:02d}"
        self.lbl_record.enabled = is_new_record

        self.root.enabled = True
        animate_panel_in(self.panel, duration=0.22, direction="scale")

    def hide(self):
        self.root.enabled = False

    def on_next_level(self):
        self.game_manager.sound_manager.play("click")
        self.hide()
        self.game_manager.advance_after_win()

    def on_replay(self):
        self.game_manager.sound_manager.play("click")
        self.hide()
        self.game_manager.restart_level()

    def on_level_select(self):
        self.game_manager.sound_manager.play("click")
        self.hide()
        self.game_manager.show_level_select()

    def on_menu(self):
        self.game_manager.sound_manager.play("click")
        self.hide()
        self.game_manager.show_main_menu()
