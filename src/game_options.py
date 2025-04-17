# game_options.py
class GameOptions:
    def __init__(self):
        self.grid_size = (20, 15)  # Width, Height in cells
        self.cell_size = 40  # Size of each cell in pixels
        self.goal_size = 3  # Number of cells that make up the goal
        self.tile_bank_size = 3  # Number of slots in the tile bank
        self.tile_replenish_time = 3  # Seconds to replenish a tile
        self.game_duration = 300  # Game duration in seconds (5 minutes)
        self.cursor_sensitivity = 0.2  # Lower values make cursor movement less sensitive
        self.initial_ball_speed = 0.2  # Initial speed of the ball in cells per tick
