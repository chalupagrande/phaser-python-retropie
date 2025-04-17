# main.py
import pygame
import sys

sys.path.insert(1, "src")
from game_options import GameOptions
from game import Game
from menu import Menu
from welcome_screen import WelcomeScreen


def main():
    # Initialize pygame
    pygame.init()
    pygame.font.init()

    # Create game options with default values
    options = GameOptions()
    
    # Create a screen for the welcome screen and menu
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Tile Strategy Game")
    
    while True:
        # Show welcome screen
        welcome = WelcomeScreen(screen)
        choice = welcome.run()
        
        if choice == 'start':
            # Start the game directly
            game = Game(options)
            game.run()
            # After game ends, return to welcome screen
        elif choice == 'options':
            # Show options menu
            menu = Menu(screen, options)
            menu_result = menu.run()
            
            # After options menu, return to welcome screen


if __name__ == "__main__":
    main()
