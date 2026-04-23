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
        self.tile_limit = 10  # Number of tiles a player can place before delay kicks in
        
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

        # Per-player input source. Switchable from the options menu.
        self.p1_input = "keyboard"  # "keyboard" or "gamepad"
        self.p2_input = "keyboard"

        # Gamepad bindings. Edit in place to calibrate for your cabinet.
        #   ("button", N)         -> button N is pressed
        #   ("hat",    H, (x, y)) -> hat H is in direction (x, y); SDL hat Y is +1 up, -1 down
        #   ("axis",   A, sign)   -> axis A crossed threshold in direction sign (+1/-1)
        self.p1_gamepad = {
            "joystick_index": 0,
            "up":    ("hat", 0, (0, 1)),
            "down":  ("hat", 0, (0, -1)),
            "left":  ("hat", 0, (-1, 0)),
            "right": ("hat", 0, (1, 0)),
            "tile1": ("button", 0),
            "tile2": ("button", 1),
            "tile3": ("button", 2),
        }
        self.p2_gamepad = {
            "joystick_index": 1,
            "up":    ("hat", 0, (0, 1)),
            "down":  ("hat", 0, (0, -1)),
            "left":  ("hat", 0, (-1, 0)),
            "right": ("hat", 0, (1, 0)),
            "tile1": ("button", 0),
            "tile2": ("button", 1),
            "tile3": ("button", 2),
        }
