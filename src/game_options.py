# game_options.py
import pygame


class GameOptions:
    def __init__(self):
        # Game board configuration
        self.grid_size = (21, 15)  # Width, Height in cells
        self.cell_size = 40  # Size of each cell in pixels
        self.goal_size = 3  # Number of cells that make up the goal
        
        # Tile configuration
        self.tile_bank_size = 3  # Number of slots in the tile bank
        self.tile_replenish_time = 3  # Seconds to replenish a tile
        
        # Game mechanics
        self.game_duration = 180  # Game duration in seconds (3 minutes)
        self.cursor_sensitivity = 0.2  # Lower values make cursor movement less sensitive
        self.initial_ball_speed = 0.2  # Initial speed of the ball in cells per tick

        # Player 1 controls
        self.p1_controls = {
            "up": pygame.K_w,
            "down": pygame.K_s,
            "left": pygame.K_a,
            "right": pygame.K_d,
            "tile1": pygame.K_1,
            "tile2": pygame.K_2,
            "tile3": pygame.K_3,
        }

        # Player 2 controls
        self.p2_controls = {
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "tile1": pygame.K_i,
            "tile2": pygame.K_o,
            "tile3": pygame.K_p,
        }
