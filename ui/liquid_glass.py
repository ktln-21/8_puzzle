"""
Liquid Glass purple UI components: layered translucent panels, glowing borders,
and styled interactive glass buttons.
"""
from ursina import Entity, Button, Text, color, Vec2, Vec3, camera, curve, invoke
import config
from config import rgba

class GlassPanel(Entity):
    """
    Composite Entity with multi-layered visual structure:
    1. Shadow layer (dark, soft offset)
    2. Border layer (fine lavender/white-purple line)
    3. Body layer (semi-transparent purple glass)
    4. Highlight reflection line (subtle top glint)
    5. Content container (where UI children reside)
    """

    def __init__(self, parent=camera.ui, position=(0, 0), scale=(0.5, 0.5), style="default", **kwargs):
        super().__init__(parent=parent, position=position, **kwargs)
        self.panel_scale = scale
        w, h = scale[0], scale[1]

        # 1. Soft Shadow
        self.shadow = Entity(
            parent=self,
            model="quad",
            scale=(w + 0.02, h + 0.02),
            position=(0.006, -0.008, 0.02),
            color=rgba(5, 2, 12, 140)
        )

        # 2. Border
        border_thickness = 0.004
        border_color = config.GLASS_BORDER_COLOR
        if style == "card":
            border_color = rgba(200, 185, 245, 90)
        elif style == "modal":
            border_color = rgba(240, 230, 255, 140)

        self.border = Entity(
            parent=self,
            model="quad",
            scale=(w + border_thickness, h + border_thickness),
            position=(0, 0, 0.01),
            color=border_color
        )

        # 3. Body (translucent glass)
        body_color = config.GLASS_BASE_COLOR
        if style == "card":
            body_color = config.GLASS_CARD_COLOR
        elif style == "dark":
            body_color = rgba(24, 16, 42, 220)

        self.body = Entity(
            parent=self,
            model="quad",
            scale=(w, h),
            position=(0, 0, 0.005),
            color=body_color
        )

        # 4. Highlight reflection line
        self.highlight = Entity(
            parent=self,
            model="quad",
            scale=(w * 0.96, 0.003),
            position=(0, (h / 2) - 0.004, 0.002),
            color=config.GLASS_HIGHLIGHT_COLOR
        )

        # 5. Content Root (in front of body, highlight, and border)
        self.content = Entity(parent=self, position=(0, 0, -0.01))

def create_glass_panel(parent=camera.ui, position=(0, 0), scale=(0.5, 0.5), style="default") -> GlassPanel:
    """Helper to instantiate a GlassPanel."""
    return GlassPanel(parent=parent, position=position, scale=scale, style=style)

def create_glass_button(
    text: str,
    position=(0, 0),
    scale=(0.2, 0.06),
    callback=None,
    style="primary",
    parent=camera.ui
) -> Button:
    """
    Creates a styled glass button with clean text, hover state, and pressed response.
    """
    btn = Button(
        parent=parent,
        text=text,
        position=position,
        scale=scale,
        model="quad"
    )

    # Style definitions using safe rgba
    if style == "primary":
        base_col = rgba(95, 60, 170, 220)
        hover_col = rgba(135, 90, 225, 245)
        pressed_col = rgba(70, 42, 130, 255)
        text_col = config.TEXT_PRIMARY_COLOR
    elif style == "cyan" or style == "action":
        base_col = rgba(38, 120, 165, 220)
        hover_col = rgba(55, 175, 225, 245)
        pressed_col = rgba(28, 85, 120, 255)
        text_col = config.TEXT_PRIMARY_COLOR
    elif style == "danger":
        base_col = rgba(135, 45, 80, 210)
        hover_col = rgba(185, 60, 105, 240)
        pressed_col = rgba(95, 30, 55, 255)
        text_col = config.TEXT_PRIMARY_COLOR
    elif style == "success":
        base_col = rgba(40, 125, 90, 220)
        hover_col = rgba(55, 175, 125, 245)
        pressed_col = rgba(28, 95, 70, 255)
        text_col = config.TEXT_PRIMARY_COLOR
    else:  # secondary / default
        base_col = rgba(55, 38, 92, 205)
        hover_col = rgba(88, 62, 142, 235)
        pressed_col = rgba(40, 24, 70, 255)
        text_col = config.TEXT_PRIMARY_COLOR

    btn.color = base_col
    btn.highlight_color = hover_col
    btn.pressed_color = pressed_col
    btn.disabled_color = rgba(30, 22, 45, 140)

    if btn.text_entity:
        btn.text_entity.color = text_col
        # Proportional scale adjustment that preserves aspect ratio
        btn.text_entity.scale = btn.text_entity.scale * 0.94

    orig_scale = Vec3(scale[0], scale[1], 1)
    hover_scale = Vec3(scale[0] * config.HOVER_SCALE, scale[1] * config.HOVER_SCALE, 1)

    # Hover animations
    def on_enter():
        if btn.enabled and getattr(btn, "_is_glass_enabled", True):
            btn.animate_scale(hover_scale, duration=0.1, curve=curve.out_quad)

    def on_exit():
        if btn.enabled and getattr(btn, "_is_glass_enabled", True):
            btn.animate_scale(orig_scale, duration=0.1, curve=curve.out_quad)

    btn.on_mouse_enter = on_enter
    btn.on_mouse_exit = on_exit

    if callback:
        btn.on_click = callback

    btn._is_glass_enabled = True
    btn._orig_color = base_col
    btn._orig_scale = orig_scale
    btn._hover_scale = hover_scale

    return btn

def set_glass_enabled(element: Button, enabled: bool) -> None:
    """Enables or disables a glass button, visually fading it and toggling collider."""
    element._is_glass_enabled = enabled
    element.disabled = not enabled
    element.collision = enabled

    if enabled:
        element.color = getattr(element, "_orig_color", element.color)
        if element.text_entity:
            element.text_entity.color = config.TEXT_PRIMARY_COLOR
    else:
        element.color = rgba(30, 22, 45, 140)
        if element.text_entity:
            element.text_entity.color = config.TEXT_MUTED_COLOR

def animate_panel_in(panel: Entity, duration: float = 0.2, direction: str = "fade") -> None:
    """Animates panel entrance via scale pop or subtle slide."""
    panel.enabled = True
    if direction == "scale":
        orig_scale = panel.scale
        panel.scale = orig_scale * 0.95
        panel.animate_scale(orig_scale, duration=duration, curve=curve.out_back)
    elif direction == "slide_up":
        target_y = panel.y
        panel.y = target_y - 0.05
        panel.animate_y(target_y, duration=duration, curve=curve.out_quad)
    elif direction == "slide_right":
        target_x = panel.x
        panel.x = target_x + 0.05
        panel.animate_x(target_x, duration=duration, curve=curve.out_quad)
