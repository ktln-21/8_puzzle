"""
Sound manager for playing game audio effects with volume control and muting.
"""
import logging
from ursina import Audio

logger = logging.getLogger(__name__)

class SoundManager:
    """
    Manages sound effects and background audio.
    """

    def __init__(self, settings_manager=None):
        self.settings_manager = settings_manager
        self.sounds = {}
        self._init_sounds()

    def _init_sounds(self):
        """Pre-loads sound instances using relative paths to avoid non-ASCII directory issues."""
        sound_files = {
            "click": "assets/sounds/click.wav",
            "move": "assets/sounds/move.wav",
            "invalid": "assets/sounds/invalid.wav",
            "win": "assets/sounds/win.wav",
        }
        for name, rel_path in sound_files.items():
            try:
                snd = Audio(rel_path, autoplay=False, loop=False)
                self.sounds[name] = snd
            except Exception as e:
                logger.warning(f"Could not load sound {name}: {e}")

    def play(self, sound_name: str):
        """Plays the requested sound if enabled in settings."""
        if not self.settings_manager:
            return
        settings = self.settings_manager.load_settings()
        if not settings.get("sound_enabled", True):
            return

        vol = settings.get("sound_volume", 0.7)
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.volume = vol
                snd.play()
            except Exception as e:
                logger.debug(f"Audio playback error: {e}")
