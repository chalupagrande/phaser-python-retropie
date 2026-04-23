# main.py
import os
import pygame
import sys

sys.path.insert(1, "src")
from game_options import GameOptions
from game import Game
from menu import Menu
from welcome_screen import WelcomeScreen
from calibration import apply_calibration

MENU_SIZE = (1000, 800)


def _create_display():
    # Dev opt-out for Mac: PHASER_WINDOWED=1 keeps a normal window.
    # Default path is fullscreen at the Pi's native resolution.
    if os.environ.get("PHASER_WINDOWED"):
        return pygame.display.set_mode(MENU_SIZE)
    info = pygame.display.Info()
    return pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)


def main():
    pygame.init()
    pygame.font.init()
    pygame.joystick.init()

    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    for j in joysticks:
        j.init()

    options = GameOptions()
    apply_calibration(options)
    pygame.display.set_caption("PHASER")
    screen = _create_display()

    while True:
        choice = WelcomeScreen(screen).run()

        if choice == 'start':
            Game(options, screen).run()
        elif choice == 'options':
            Menu(screen, options).run()


if __name__ == "__main__":
    main()
