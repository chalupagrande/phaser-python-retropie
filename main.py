# main.py
import pygame
import sys

sys.path.insert(1, "src")
from game_options import GameOptions
from game import Game
from menu import Menu


def main():
    # Initialize pygame
    pygame.init()
    pygame.font.init()

    # Create game options with default values
    options = GameOptions()
    
    # Create a temporary screen for the menu
    # We'll recreate the screen with proper dimensions after menu configuration
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Game Configuration")
    
    # Run the menu
    menu = Menu(screen, options)
    start_game = menu.run()
    
    # If the user chose to start the game
    if start_game:
        # Create and run the game with configured options
        game = Game(options)
        game.run()


if __name__ == "__main__":
    main()
