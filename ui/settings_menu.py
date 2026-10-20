"""
Settings menu modal allowing players to configure sound, animation speed, and visual hints.
"""
from ursina import Entity, Text, color, camera
import config
from config import rgba
from ui.liquid_glass import create_glass_panel, create_glass_button, animate_panel_in

class SettingsMenu:
    """
    Settings configuration dialog.
    """

    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.root = Entity(parent=camera.ui, enabled=False, z=-0.18)
        self.from_menu = "main_menu"

        # Dimmer covers full screen and blocks background clicks
        self.dimmer = Entity(
            parent=self.root,
            model="quad",
            scale=(2.5, 2.0),
            position=(0, 0, 0.01),
            color=rgba(10, 6, 20, 215),
            collider="box"
        )

        # Panel
        self.panel = create_glass_panel(
            parent=self.root,
            position=(0, 0),
            scale=(0.52, 0.62),
            style="modal"
        )

        # Title
        self.title = Text(
            parent=self.panel.content,
            text="CÀI ĐẶT TRÒ CHƠI",
            position=(0, 0.23),
            origin=(0, 0),
            scale=1.5,
            color=config.ACCENT_LAVENDER
        )

        btn_w, btn_h = 0.36, 0.052

        # 1. Sound Toggle
        self.btn_sound = create_glass_button(
            text="ÂM THANH: BẬT",
            position=(0, 0.11),
            scale=(btn_w, btn_h),
            callback=self.toggle_sound,
            style="secondary",
            parent=self.panel.content
        )

        # 2. Hint Toggle
        self.btn_hint = create_glass_button(
            text="GỢI Ý NƯỚC ĐI: BẬT",
            position=(0, 0.02),
            scale=(btn_w, btn_h),
            callback=self.toggle_hint,
            style="secondary",
            parent=self.panel.content
        )

        # 3. Animation Speed
        self.btn_speed = create_glass_button(
            text="TỐC ĐỘ HOẠT ẢNH: 1.0X",
            position=(0, -0.07),
            scale=(btn_w, btn_h),
            callback=self.cycle_speed,
            style="secondary",
            parent=self.panel.content
        )

        # 4. Reset Progress Option (safe)
        self.btn_reset_save = create_glass_button(
            text="ĐẶT LẠI TIẾN TRÌNH",
            position=(0, -0.16),
            scale=(btn_w, btn_h),
            callback=self.reset_progress,
            style="danger",
            parent=self.panel.content
        )

        # 5. Back / Close
        self.btn_close = create_glass_button(
            text="LƯU & ĐÓNG",
            position=(0, -0.25),
            scale=(btn_w, btn_h),
            callback=self.on_close,
            style="primary",
            parent=self.panel.content
        )

    def refresh_ui(self):
        settings = self.game_manager.save_manager.load_settings()
        sound_on = settings.get("sound_enabled", True)
        self.btn_sound.text = f"ÂM THANH: {'BẬT' if sound_on else 'TẮT'}"

        hint_on = settings.get("show_valid_move_hint", True)
        self.btn_hint.text = f"GỢI Ý NƯỚC ĐI: {'BẬT' if hint_on else 'TẮT'}"

        speed = settings.get("animation_speed", 1.0)
        self.btn_speed.text = f"TỐC ĐỘ HOẠT ẢNH: {speed:.1f}X"

    def show(self, from_menu: str = "main_menu"):
        self.from_menu = from_menu
        self.refresh_ui()
        self.root.enabled = True
        animate_panel_in(self.panel, duration=0.18, direction="scale")

    def hide(self):
        self.root.enabled = False

    def toggle_sound(self):
        self.game_manager.sound_manager.play("click")
        settings = self.game_manager.save_manager.load_settings()
        settings["sound_enabled"] = not settings.get("sound_enabled", True)
        self.game_manager.save_manager.save_settings(settings)
        self.refresh_ui()

    def toggle_hint(self):
        self.game_manager.sound_manager.play("click")
        settings = self.game_manager.save_manager.load_settings()
        settings["show_valid_move_hint"] = not settings.get("show_valid_move_hint", True)
        self.game_manager.save_manager.save_settings(settings)
        self.refresh_ui()
        self.game_manager.update_tile_hints()

    def cycle_speed(self):
        self.game_manager.sound_manager.play("click")
        settings = self.game_manager.save_manager.load_settings()
        speeds = [0.5, 1.0, 2.0]
        curr = settings.get("animation_speed", 1.0)
        next_speed = speeds[(speeds.index(curr) + 1) % len(speeds)] if curr in speeds else 1.0
        settings["animation_speed"] = next_speed
        self.game_manager.save_manager.save_settings(settings)
        config.MOVE_ANIMATION_DURATION = 0.14 / next_speed
        self.refresh_ui()

    def reset_progress(self):
        self.game_manager.sound_manager.play("click")
        from core.save_manager import DEFAULT_PROGRESS
        self.game_manager.save_manager.save_progress(DEFAULT_PROGRESS)
        if hasattr(self.game_manager, "level_select"):
            self.game_manager.level_select.refresh()

    def on_close(self):
        self.game_manager.sound_manager.play("click")
        self.hide()
        if self.from_menu == "pause":
            self.game_manager.pause_menu.show()
        elif self.from_menu == "main_menu":
            self.game_manager.show_main_menu()
