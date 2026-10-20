"""
Main entry point for Neon Clockwork 8 Puzzle.
Initializes Ursina application, window configuration, camera, ambient effects,
and launches GameManager.
"""
import random
from ursina import Ursina, window, camera, color, Entity, time, Vec3
import config
from config import rgba
from core.game_manager import GameManager

def create_ambient_particles(count: int = 18):
    """Creates slow floating cosmic dust particles in the background."""
    particles = []
    for _ in range(count):
        p = Entity(
            parent=camera.ui,
            model="quad",
            scale=(random.uniform(0.004, 0.007), random.uniform(0.004, 0.007)),
            position=(
                random.uniform(-0.85, 0.85),
                random.uniform(-0.48, 0.48),
                0.08  # Placed behind UI panels
            ),
            color=rgba(180, 160, 245, random.randint(20, 45))
        )
        p.speed_y = random.uniform(0.015, 0.035)
        p.speed_x = random.uniform(-0.01, 0.01)
        particles.append(p)
    return particles

def main():
    # Initialize Ursina
    app = Ursina(
        title=config.WINDOW_TITLE,
        borderless=False,
        size=(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
    )

    # Configure window
    window.title = config.WINDOW_TITLE
    window.size = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
    window.borderless = False
    window.fullscreen = False
    window.color = config.BACKGROUND_COLOR
    if hasattr(window, "fps_counter") and window.fps_counter:
        window.fps_counter.enabled = False
    if hasattr(window, "exit_button") and window.exit_button:
        window.exit_button.enabled = False

    # Ambient Background glow disc
    bg_glow = Entity(
        parent=camera.ui,
        model="quad",
        scale=(1.8, 1.1),
        position=(0, 0, 0.09),
        color=config.BACKGROUND_SECONDARY
    )

    particles = create_ambient_particles()

    # Create Game Manager
    game_manager = GameManager()
    game_manager.show_main_menu()

    # Frame update hook
    def update():
        dt = time.dt
        game_manager.update_timer(dt)

        # Ambient floating particle physics
        settings = game_manager.save_manager.load_settings()
        if settings.get("background_particles_enabled", True):
            for p in particles:
                p.y += p.speed_y * dt
                p.x += p.speed_x * dt
                if p.y > 0.52:
                    p.y = -0.52
                    p.x = random.uniform(-0.85, 0.85)

    # Key input hook
    def input(key):
        game_manager.input_controller.handle_key(key)

    # Register handlers with Ursina
    import __main__
    __main__.update = update
    __main__.input = input

    # Run game loop
    app.run()

if __name__ == "__main__":
    main()
