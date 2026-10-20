"""
Main Menu screen with Liquid Glass styling, game branding, and primary navigation.
"""
from ursina import Entity, Text, camera, application
import config
from ui.liquid_glass import create_glass_panel, create_glass_button, animate_panel_in

class MainMenu:
    """
    Main menu screen.
    """

    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.root = Entity(parent=camera.ui, enabled=False)

        # Central Glass Card
        self.panel = create_glass_panel(
            parent=self.root,
            position=(0, 0),
            scale=(0.62, 0.78),
            style="default"
        )

        # Title and Subtitle
        self.title_top = Text(
            parent=self.panel.content,
            text="NEON CLOCKWORK",
            position=(0, 0.28),
            origin=(0, 0),
            scale=1.9,
            color=config.ACCENT_LAVENDER
        )

        self.title_bot = Text(
            parent=self.panel.content,
            text="8  P U Z Z L E",
            position=(0, 0.20),
            origin=(0, 0),
            scale=1.5,
            color=config.TEXT_PRIMARY_COLOR
        )

        self.subtitle = Text(
            parent=self.panel.content,
            text="60 Man choi - Che do tuan tu & Ngau nhien - AI Solver",
            position=(0, 0.14),
            origin=(0, 0),
            scale=0.85,
            color=config.TEXT_MUTED_COLOR
        )

        btn_w, btn_h = 0.42, 0.056

        # 1. Continue / Play Campaign
        self.btn_play = create_glass_button(
            text="CHƠI THEO MÀN",
            position=(0, 0.05),
            scale=(btn_w, btn_h),
            callback=self.on_continue_clicked,
            style="primary",
            parent=self.panel.content
        )

        # 2. Random Sequential 60 Levels Mode
        self.btn_random = create_glass_button(
            text="CHẾ ĐỘ NGẪU NHIÊN (60 BÀN)",
            position=(0, -0.03),
            scale=(btn_w, btn_h),
            callback=self.on_random_mode_clicked,
            style="action",
            parent=self.panel.content
        )

        # 3. Level Select (60 levels)
        self.btn_levels = create_glass_button(
            text="CHỌN MÀN CHƠI (60 MÀN)",
            position=(0, -0.11),
            scale=(btn_w, btn_h),
            callback=self.on_level_select_clicked,
            style="secondary",
            parent=self.panel.content
        )

        # 4. Settings
        self.btn_settings = create_glass_button(
            text="CÀI ĐẶT",
            position=(0, -0.19),
            scale=(btn_w, btn_h),
            callback=self.on_settings_clicked,
            style="secondary",
            parent=self.panel.content
        )

        # 5. Quit
        self.btn_quit = create_glass_button(
            text="THOÁT GAME",
            position=(0, -0.27),
            scale=(btn_w, btn_h),
            callback=self.on_quit_clicked,
            style="danger",
            parent=self.panel.content
        )

    def show(self, has_save: bool = True):
        self.btn_play.text = "CHƠI TIẾP (THEO MÀN)" if has_save else "BẮT ĐẦU CHƠI (THEO MÀN)"
        self.root.enabled = True
        animate_panel_in(self.panel, duration=0.22, direction="scale")

    def hide(self):
        self.root.enabled = False

    def on_continue_clicked(self):
        self.game_manager.sound_manager.play("click")
        self.hide()
        self.game_manager.resume_saved_or_new_game()

    def on_random_mode_clicked(self):
        self.game_manager.sound_manager.play("click")
        self.hide()
        self.game_manager.start_random_60_mode()

    def on_level_select_clicked(self):
        self.game_manager.sound_manager.play("click")
        self.hide()
        self.game_manager.show_level_select()

    def on_settings_clicked(self):
        self.game_manager.sound_manager.play("click")
        self.hide()
        self.game_manager.show_settings(from_menu="main_menu")

    def on_quit_clicked(self):
        self.game_manager.sound_manager.play("click")
        application.quit()
