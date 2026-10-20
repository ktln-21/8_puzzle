"""
Pause menu modal overlay with glass aesthetics.
"""
from ursina import Entity, Text, color, camera
import config
from config import rgba
from ui.liquid_glass import create_glass_panel, create_glass_button, animate_panel_in

class PauseMenu:
    """
    Pause menu modal.
    """

    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.root = Entity(parent=camera.ui, enabled=False, z=-0.15)

        # Backdrop dimming layer (covers full screen and intercepts background clicks)
        self.dimmer = Entity(
            parent=self.root,
            model="quad",
            scale=(2.5, 2.0),
            position=(0, 0, 0.01),
            color=rgba(10, 6, 20, 215),
            collider="box"
        )

        # Central Modal Glass Panel
        self.panel = create_glass_panel(
            parent=self.root,
            position=(0, 0),
            scale=(0.48, 0.62),
            style="modal"
        )

        # Title
        self.title = Text(
            parent=self.panel.content,
            text="TẠM DỪNG",
            position=(0, 0.22),
            origin=(0, 0),
            scale=1.6,
            color=config.ACCENT_LAVENDER
        )

        btn_w, btn_h = 0.34, 0.055

        # 1. Resume
        self.btn_resume = create_glass_button(
            text="TIẾP TỤC",
            position=(0, 0.09),
            scale=(btn_w, btn_h),
            callback=self.on_resume,
            style="primary",
            parent=self.panel.content
        )

        # 2. Restart
        self.btn_restart = create_glass_button(
            text="LÀM LẠI MÀN",
            position=(0, 0.01),
            scale=(btn_w, btn_h),
            callback=self.on_restart,
            style="secondary",
            parent=self.panel.content
        )

        # 3. Level Select
        self.btn_levels = create_glass_button(
            text="CHỌN MÀN CHƠI",
            position=(0, -0.07),
            scale=(btn_w, btn_h),
            callback=self.on_level_select,
            style="secondary",
            parent=self.panel.content
        )

        # 4. Settings
        self.btn_settings = create_glass_button(
            text="CÀI ĐẶT",
            position=(0, -0.15),
            scale=(btn_w, btn_h),
            callback=self.on_settings,
            style="secondary",
            parent=self.panel.content
        )

        # 5. Main Menu
        self.btn_menu = create_glass_button(
            text="VỀ MENU CHÍNH",
            position=(0, -0.23),
            scale=(btn_w, btn_h),
            callback=self.on_back_to_menu,
            style="danger",
            parent=self.panel.content
        )

    def show(self):
        self.root.enabled = True
        animate_panel_in(self.panel, duration=0.18, direction="scale")

    def hide(self):
        self.root.enabled = False

    def on_resume(self):
        self.game_manager.sound_manager.play("click")
        self.game_manager.toggle_pause()

    def on_restart(self):
        self.game_manager.sound_manager.play("click")
        self.hide()
        self.game_manager.restart_level()

    def on_level_select(self):
        self.game_manager.sound_manager.play("click")
        self.hide()
        self.game_manager.show_level_select()

    def on_settings(self):
        self.game_manager.sound_manager.play("click")
        self.game_manager.show_settings(from_menu="pause")

    def on_back_to_menu(self):
        self.game_manager.sound_manager.play("click")
        self.hide()
        self.game_manager.show_main_menu()
