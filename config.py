"""
Configuration and constants for Neon Clockwork 8 Puzzle.
"""
from pathlib import Path
from ursina import color

def rgba(r: float, g: float, b: float, a: float = 255.0) -> color.Color:
    """Safe helper returning Ursina Color with channels clamped and scaled 0.0 to 1.0."""
    alpha = (a / 255.0) if a > 1.0 else a
    return color.Color(r / 255.0, g / 255.0, b / 255.0, alpha)

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
SOUNDS_DIR = ASSETS_DIR / "sounds"
FONTS_DIR = ASSETS_DIR / "fonts"
TEXTURES_DIR = ASSETS_DIR / "textures"

LEVELS_FILE = DATA_DIR / "levels.json"
SAVE_FILE = DATA_DIR / "save.json"
SETTINGS_FILE = DATA_DIR / "settings.json"

SOUND_MOVE = SOUNDS_DIR / "move.wav"
SOUND_INVALID = SOUNDS_DIR / "invalid.wav"
SOUND_WIN = SOUNDS_DIR / "win.wav"
SOUND_CLICK = SOUNDS_DIR / "click.wav"

# Window settings
WINDOW_TITLE = "Neon Clockwork 8 Puzzle"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
ASPECT_RATIO = WINDOW_WIDTH / WINDOW_HEIGHT

# Game grid constants
GRID_SIZE = 3
TILE_COUNT = 9
TOTAL_LEVELS = 60

# Strict Goal State:
# 1 2 3
# 8 0 4
# 7 6 5
GOAL_STATE = (1, 2, 3, 8, 0, 4, 7, 6, 5)

# Animation settings
MOVE_ANIMATION_DURATION = 0.14
HOVER_SCALE = 1.03
PANEL_ANIMATION_DURATION = 0.20
WIN_STEP_DELAY = 0.08

# Visual Colors (Liquid Glass Purple Theme)
# Deep obsidian violet background
BACKGROUND_COLOR = color.hex("#100B1C")
BACKGROUND_SECONDARY = color.hex("#1A1230")

# Liquid glass panel colors
PANEL_ALPHA = 0.28
BORDER_ALPHA = 0.45
GLASS_BASE_COLOR = rgba(36, 22, 60, int(255 * PANEL_ALPHA))
GLASS_CARD_COLOR = rgba(50, 32, 85, int(255 * (PANEL_ALPHA + 0.12)))
GLASS_BORDER_COLOR = rgba(231, 222, 255, int(255 * BORDER_ALPHA))
GLASS_HIGHLIGHT_COLOR = rgba(255, 255, 255, 35)

# Accent colors
ACCENT_LAVENDER = color.hex("#BCA7FF")
ACCENT_PURPLE = color.hex("#9672F5")
ACCENT_CYAN = color.hex("#8DEBFF")
PURPLE_GLOW_COLOR = color.hex("#9672F5")
SUCCESS_COLOR = color.hex("#6EE7B7")
ERROR_COLOR = color.hex("#F87171")

# Tile specific colors
TILE_COLOR = rgba(55, 34, 92, 230)
TILE_HOVER_COLOR = rgba(85, 55, 145, 245)
TILE_VALID_COLOR = rgba(70, 45, 120, 235)
TILE_EMPTY_COLOR = color.hex("#171024")
TILE_BORDER_COLOR = rgba(200, 185, 245, 150)
TILE_BORDER_HOVER_COLOR = rgba(231, 222, 255, 230)
TILE_BORDER_VALID_COLOR = rgba(141, 235, 255, 190)

# Typography colors
TEXT_PRIMARY_COLOR = color.hex("#F8F5FF")
TEXT_SECONDARY_COLOR = color.hex("#C4BBD9")
TEXT_MUTED_COLOR = color.hex("#8C82A6")
