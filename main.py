# main.py
import pygame
import sys

sys.path.insert(1, "src")
from game_options import GameOptions
from game import Game


def main():
    # Initialize pygame
    pygame.init()
    pygame.font.init()

    options = GameOptions()
    game = Game(options)
    game.run()


if __name__ == "__main__":
    main()
