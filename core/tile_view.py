"""
Visual representation of an 8-Puzzle tile with liquid glass aesthetics,
smooth animations, hover states, and feedback effects.
"""
from ursina import Entity, Button, color, Vec3, curve, invoke, destroy, camera
import config
from config import rgba

class TileView:
    """
    Manages the visual presentation, animations, and interaction of a single tile.
    """

    def __init__(self, grid_index: int, value: int, position: Vec3, parent=camera.ui, on_click_callback=None):
        self.grid_index = grid_index
        self.value = value
        self.target_position = Vec3(position)
        self.on_click_callback = on_click_callback
        self.visual_state = "default"
        self.is_animating = False

        self.root = Entity(parent=parent, position=self.target_position)

        # 1. Shadow
        self.shadow = Entity(
            parent=self.root,
            model="quad",
            scale=(0.154, 0.154),
            position=(0.004, -0.005, 0.02),
            color=rgba(5, 2, 12, 140)
        )

        # 2. Border
        self.border = Entity(
            parent=self.root,
            model="quad",
            scale=(0.152, 0.152),
            position=(0, 0, 0.01),
            color=config.TILE_BORDER_COLOR
        )

        # 3. Main Body Button
        self.button = Button(
            parent=self.root,
            model="quad",
            scale=(0.146, 0.146),
            position=(0, 0, 0),
            color=config.TILE_COLOR,
            highlight_color=config.TILE_HOVER_COLOR,
            pressed_color=rgba(40, 24, 70, 240)
        )

        # 4. Highlight line at top
        self.highlight = Entity(
            parent=self.root,
            model="quad",
            scale=(0.138, 0.003),
            position=(0, 0.068, -0.01),
            color=config.GLASS_HIGHLIGHT_COLOR
        )

        if self.button.text_entity:
            self.button.text_entity.scale = self.button.text_entity.scale * 1.6
            self.button.text_entity.color = config.TEXT_PRIMARY_COLOR

        # Mouse hover hooks
        self.button.on_mouse_enter = self._on_mouse_enter
        self.button.on_mouse_exit = self._on_mouse_exit
        self.button.on_click = self._on_click

        self.set_value(value)

    def _on_mouse_enter(self):
        if self.value != 0 and not self.is_animating:
            self.border.color = config.TILE_BORDER_HOVER_COLOR
            self.root.animate_scale(Vec3(config.HOVER_SCALE, config.HOVER_SCALE, 1), duration=0.1, curve=curve.out_quad)

    def _on_mouse_exit(self):
        if self.value != 0 and not self.is_animating:
            self.update_border_by_state()
            self.root.animate_scale(Vec3(1, 1, 1), duration=0.1, curve=curve.out_quad)

    def _on_click(self):
        if self.on_click_callback and not self.is_animating:
            self.on_click_callback(self.grid_index)

    def set_value(self, value: int):
        """Updates tile value and visual appearance (empty vs numbered)."""
        self.value = value
        if value == 0:
            self.button.text = ""
            self.button.color = config.TILE_EMPTY_COLOR
            self.button.highlight_color = config.TILE_EMPTY_COLOR
            self.border.color = rgba(30, 20, 48, 80)
            self.shadow.enabled = False
            self.highlight.enabled = False
            self.button.collision = False
            self.button.disabled = True
        else:
            self.button.text = str(value)
            self.button.color = config.TILE_COLOR
            self.button.highlight_color = config.TILE_HOVER_COLOR
            self.shadow.enabled = True
            self.highlight.enabled = True
            self.button.collision = True
            self.button.disabled = False
            self.update_border_by_state()

    def update_border_by_state(self):
        """Sets border color depending on current visual state."""
        if self.value == 0:
            return
        if self.visual_state == "valid":
            self.border.color = config.TILE_BORDER_VALID_COLOR
        elif self.visual_state == "win":
            self.border.color = config.SUCCESS_COLOR
        else:
            self.border.color = config.TILE_BORDER_COLOR

    def set_visual_state(self, state_name: str):
        """Sets state (default, valid, hover, win)."""
        self.visual_state = state_name
        self.update_border_by_state()

    def set_position(self, target_pos: Vec3, animated: bool = False, duration: float = config.MOVE_ANIMATION_DURATION, on_complete=None):
        """Updates tile position, optionally with a smooth slide animation."""
        self.target_position = Vec3(target_pos)
        if animated and not config.MOVE_ANIMATION_DURATION == 0:
            self.is_animating = True
            anim = self.root.animate_position(self.target_position, duration=duration, curve=curve.out_quad)

            def finish():
                self.is_animating = False
                if on_complete:
                    on_complete()

            invoke(finish, delay=duration)
        else:
            self.root.position = self.target_position
            self.is_animating = False
            if on_complete:
                on_complete()

    def play_invalid_feedback(self):
        """Plays subtle horizontal wobble and flash border to signal invalid move."""
        orig_x = self.root.x
        orig_border_col = self.border.color
        self.border.color = config.ERROR_COLOR

        self.root.animate_x(orig_x + 0.012, duration=0.04, curve=curve.linear)
        def step2():
            self.root.animate_x(orig_x - 0.012, duration=0.06, curve=curve.linear)
        def step3():
            self.root.animate_x(orig_x, duration=0.04, curve=curve.linear)
            self.border.color = orig_border_col

        invoke(step2, delay=0.04)
        invoke(step3, delay=0.10)

    def play_win_effect(self, delay: float = 0.0):
        """Glow pulse animation when stage is completed."""
        if self.value == 0:
            return

        def trigger_pulse():
            self.border.color = config.SUCCESS_COLOR
            self.root.animate_scale(Vec3(1.08, 1.08, 1), duration=0.12, curve=curve.out_quad)
            def settle():
                self.root.animate_scale(Vec3(1.0, 1.0, 1), duration=0.15, curve=curve.in_quad)
            invoke(settle, delay=0.12)

        invoke(trigger_pulse, delay=delay)

    def destroy(self):
        """Destroys all visual entities."""
        destroy(self.root)
