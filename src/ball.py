# ball.py
import random
import math
from tile_type import TileType


class Ball:
    def __init__(self, grid_size, initial_speed=0.2):
        # Use floating point for precise position
        self.pos = [float(grid_size[0]) / 2, float(grid_size[1]) / 2]  # Center of grid
        self.velocity = [0, random.choice([-1, 1])]  # Start moving vertically
        self.speed_multiplier = 1.0
        self.base_speed = initial_speed  # Cells per tick
        
        # Track the last cell the ball was in to detect cell changes
        self.last_cell = [int(self.pos[0]), int(self.pos[1])]

    def update(self, grid, grid_size):
        # Store old position and cell
        old_pos = self.pos.copy()
        old_cell = [int(old_pos[0]), int(old_pos[1])]
        
        # Calculate new position with smooth movement
        new_x = self.pos[0] + self.velocity[0] * self.speed_multiplier * self.base_speed
        new_y = self.pos[1] + self.velocity[1] * self.speed_multiplier * self.base_speed
        
        # Handle horizontal boundaries
        if new_x < 0 or new_x >= grid_size[0]:
            self.velocity[0] *= -1  # Bounce horizontally
            new_x = max(0, min(grid_size[0] - 0.01, old_pos[0]))
        
        # Handle vertical boundaries
        if new_y < 0 or new_y >= grid_size[1]:
            self.velocity[1] *= -1  # Bounce vertically
            new_y = max(0, min(grid_size[1] - 0.01, old_pos[1]))
        
        # Update position
        self.pos = [new_x, new_y]
        
        # Get current cell
        current_cell = [int(self.pos[0]), int(self.pos[1])]
        
        # Check if we've moved to a new cell
        if current_cell[0] != old_cell[0] or current_cell[1] != old_cell[1]:
            # Check if the new cell has a tile
            if (0 <= current_cell[0] < grid_size[0] and 
                0 <= current_cell[1] < grid_size[1]):
                
                tile = grid[current_cell[1]][current_cell[0]]
                if tile is not None:
                    self.apply_tile_effect(tile)
                    grid[current_cell[1]][current_cell[0]] = None  # Remove the tile

    def apply_tile_effect(self, tile_type):
        # Center the ball in the current cell before changing direction
        current_cell = [int(self.pos[0]), int(self.pos[1])]
        cell_center_x = current_cell[0] + 0.5
        cell_center_y = current_cell[1] + 0.5
        
        # Apply the tile effect
        if tile_type == TileType.UP:
            self.velocity = [0, -1]
            self.pos[0] = cell_center_x  # Center horizontally
        elif tile_type == TileType.DOWN:
            self.velocity = [0, 1]
            self.pos[0] = cell_center_x  # Center horizontally
        elif tile_type == TileType.LEFT:
            self.velocity = [-1, 0]
            self.pos[1] = cell_center_y  # Center vertically
        elif tile_type == TileType.RIGHT:
            self.velocity = [1, 0]
            self.pos[1] = cell_center_y  # Center vertically
        elif tile_type == TileType.SPEED_UP:
            self.speed_multiplier += 0.5

    def reset(self, grid_size, initial_speed=None):
        self.pos = [float(grid_size[0]) / 2, float(grid_size[1]) / 2]
        self.velocity = [0, random.choice([-1, 1])]
        self.speed_multiplier = 1.0
        if initial_speed is not None:
            self.base_speed = initial_speed
        self.last_cell = [int(self.pos[0]), int(self.pos[1])]
