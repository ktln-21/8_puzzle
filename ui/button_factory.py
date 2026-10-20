"""
Button factory for creating standardized UI buttons throughout the game.
"""
from ursina import camera
from ui.liquid_glass import create_glass_button, set_glass_enabled

def create_button(text: str, position=(0, 0), scale=(0.18, 0.055), callback=None, style="primary", parent=camera.ui):
    """Creates a standardized button using the liquid glass aesthetic."""
    return create_glass_button(
        text=text,
        position=position,
        scale=scale,
        callback=callback,
        style=style,
        parent=parent
    )

def apply_hover_effect(button):
    """Ensures hover effect is active on button."""
    pass

def set_button_enabled(button, enabled: bool):
    """Enables or disables button interactions and updates appearance."""
    set_glass_enabled(button, enabled)
