"""
Level Selection screen displaying all 60 stages with pagination (3 pages x 20 levels),
status, difficulty, and best records.
"""
from ursina import Entity, Text, camera
import config
from config import rgba
from ui.liquid_glass import create_glass_panel, create_glass_button, set_glass_enabled, animate_panel_in

class LevelSelectMenu:
    """
    Paginated level selection screen for 60 predefined levels (20 per page).
    """

    LEVELS_PER_PAGE = 20
    TOTAL_PAGES = 3

    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.root = Entity(parent=camera.ui, enabled=False)
        self.current_page = 0  # 0, 1, 2

        # Main Glass Panel
        self.panel = create_glass_panel(
            parent=self.root,
            position=(0, 0),
            scale=(1.32, 0.84),
            style="default"
        )

        # Header Title
        self.title = Text(
            parent=self.panel.content,
            text="CHỌN MÀN CHƠI (TRANG 1 / 3)",
            position=(0, 0.35),
            origin=(0, 0),
            scale=1.45,
            color=config.ACCENT_LAVENDER
        )

        self.slot_buttons = []
        self._build_grid()

        # Bottom Navigation Bar: Prev Page, Back to Menu, Next Page
        self.btn_prev_page = create_glass_button(
            text="< TRANG TRƯỚC",
            position=(-0.38, -0.35),
            scale=(0.24, 0.052),
            callback=self.on_prev_page,
            style="secondary",
            parent=self.panel.content
        )

        self.btn_back = create_glass_button(
            text="QUAY LẠI MENU",
            position=(0, -0.35),
            scale=(0.28, 0.052),
            callback=self.on_back_clicked,
            style="primary",
            parent=self.panel.content
        )

        self.btn_next_page = create_glass_button(
            text="TRANG TIẾP >",
            position=(0.38, -0.35),
            scale=(0.24, 0.052),
            callback=self.on_next_page,
            style="secondary",
            parent=self.panel.content
        )

    def _build_grid(self):
        """Constructs 5 columns x 4 rows grid of 20 slot buttons."""
        cols = 5
        start_x = -0.46
        spacing_x = 0.23
        start_y = 0.21
        spacing_y = 0.13

        for slot_idx in range(self.LEVELS_PER_PAGE):
            col_idx = slot_idx % cols
            row_idx = slot_idx // cols

            bx = start_x + (col_idx * spacing_x)
            by = start_y - (row_idx * spacing_y)

            btn = create_glass_button(
                text=f"MÀN {slot_idx + 1:02d}\n[SẴN SÀNG]",
                position=(bx, by),
                scale=(0.20, 0.105),
                callback=lambda s=slot_idx: self.on_slot_clicked(s),
                style="secondary",
                parent=self.panel.content
            )
            self.slot_buttons.append(btn)

    def refresh(self):
        """Updates the 20 slot buttons for the current page based on save data."""
        save_data = self.game_manager.save_manager.load_progress()
        unlocked = save_data.get("unlocked_level", 1)
        completed = set(save_data.get("completed_levels", []))
        best_records = {r["level_id"]: r for r in save_data.get("best_records", []) if "level_id" in r}

        start_lvl = self.current_page * self.LEVELS_PER_PAGE + 1
        end_lvl = min(config.TOTAL_LEVELS, start_lvl + self.LEVELS_PER_PAGE - 1)
        self.title.text = f"CHỌN MÀN CHƠI: MÀN {start_lvl:02d} - {end_lvl:02d} (TRANG {self.current_page + 1}/{self.TOTAL_PAGES})"

        set_glass_enabled(self.btn_prev_page, self.current_page > 0)
        set_glass_enabled(self.btn_next_page, self.current_page < self.TOTAL_PAGES - 1)

        for slot_idx, btn in enumerate(self.slot_buttons):
            lid = start_lvl + slot_idx
            if lid > config.TOTAL_LEVELS:
                btn.enabled = False
                continue

            btn.enabled = True
            is_unlocked = (lid <= unlocked)
            is_completed = (lid in completed)

            if is_completed:
                set_glass_enabled(btn, True)
                rec = best_records.get(lid)
                if rec:
                    btn.text = f"MÀN {lid:02d}\n[{rec['best_moves']} BƯỚC]"
                else:
                    btn.text = f"MÀN {lid:02d}\n[ĐÃ XONG]"
                btn.color = rgba(36, 92, 72, 225)
                btn.highlight_color = rgba(52, 128, 102, 245)
                btn._orig_color = btn.color
                if btn.text_entity:
                    btn.text_entity.color = config.SUCCESS_COLOR
            elif is_unlocked:
                set_glass_enabled(btn, True)
                btn.text = f"MÀN {lid:02d}\n[SẴN SÀNG]"
                btn.color = rgba(82, 52, 142, 220)
                btn.highlight_color = rgba(115, 78, 195, 245)
                btn._orig_color = btn.color
                if btn.text_entity:
                    btn.text_entity.color = config.TEXT_PRIMARY_COLOR
            else:
                set_glass_enabled(btn, False)
                btn.text = f"MÀN {lid:02d}\n[KHÓA]"
                btn.color = rgba(28, 18, 42, 170)
                btn.highlight_color = rgba(28, 18, 42, 170)
                btn._orig_color = btn.color
                if btn.text_entity:
                    btn.text_entity.color = config.TEXT_MUTED_COLOR

    def on_prev_page(self):
        if self.current_page > 0:
            self.game_manager.sound_manager.play("click")
            self.current_page -= 1
            self.refresh()

    def on_next_page(self):
        if self.current_page < self.TOTAL_PAGES - 1:
            self.game_manager.sound_manager.play("click")
            self.current_page += 1
            self.refresh()

    def on_slot_clicked(self, slot_idx: int):
        lid = self.current_page * self.LEVELS_PER_PAGE + slot_idx + 1
        if 1 <= lid <= config.TOTAL_LEVELS:
            self.game_manager.sound_manager.play("click")
            self.hide()
            self.game_manager.start_level(lid, is_random_mode=False)

    def show(self):
        # Jump to page of current level
        curr_lvl = getattr(self.game_manager, "current_level_id", 1)
        self.current_page = max(0, min(self.TOTAL_PAGES - 1, (curr_lvl - 1) // self.LEVELS_PER_PAGE))
        self.refresh()
        self.root.enabled = True
        animate_panel_in(self.panel, duration=0.2, direction="scale")

    def hide(self):
        self.root.enabled = False

    def on_back_clicked(self):
        self.game_manager.sound_manager.play("click")
        self.hide()
        self.game_manager.show_main_menu()
