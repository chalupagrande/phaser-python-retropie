# ball.py
import random
from tile_type import TileType


class Ball:
    def __init__(self, grid_size):
        self.pos = [grid_size[0] // 2, grid_size[1] // 2]  # Center of grid
        self.velocity = [0, random.choice([-1, 1])]  # Start moving vertically
        self.speed_multiplier = 1.0
        self.base_speed = 0.2  # Cells per tick
        self.accumulated_movement = [0, 0]

    def update(self, grid, grid_size):
        # Apply velocity to position with accumulated fractional movement
        self.accumulated_movement[0] += (
            self.velocity[0] * self.speed_multiplier * self.base_speed
        )
        self.accumulated_movement[1] += (
            self.velocity[1] * self.speed_multiplier * self.base_speed
        )

        # Extract whole cell movements
        dx = int(self.accumulated_movement[0])
        dy = int(self.accumulated_movement[1])

        # Keep the fractional part
        self.accumulated_movement[0] -= dx
        self.accumulated_movement[1] -= dy

        # Apply whole cell movements
        if dx != 0 or dy != 0:
            for _ in range(abs(dx) + abs(dy)):
                # Move one step at a time
                step_x = 1 if dx > 0 else (-1 if dx < 0 else 0)
                step_y = 1 if dy > 0 else (-1 if dy < 0 else 0)

                if abs(step_x) > 0 and abs(step_y) > 0:
                    # Prioritize x movement if both
                    if abs(dx) > abs(dy):
                        next_x = self.pos[0] + step_x
                        next_y = self.pos[1]
                        dx -= step_x
                    else:
                        next_x = self.pos[0]
                        next_y = self.pos[1] + step_y
                        dy -= step_y
                elif abs(step_x) > 0:
                    next_x = self.pos[0] + step_x
                    next_y = self.pos[1]
                    dx -= step_x
                else:
                    next_x = self.pos[0]
                    next_y = self.pos[1] + step_y
                    dy -= step_y

                # Check if the next position is within bounds
                if next_x < 0 or next_x >= grid_size[0]:
                    self.velocity[0] *= -1  # Bounce horizontally
                    next_x = self.pos[0]  # Stay at current position

                if next_y < 0 or next_y >= grid_size[1]:
                    self.velocity[1] *= -1  # Bounce vertically
                    next_y = self.pos[1]  # Stay at current position

                self.pos = [next_x, next_y]

                # Check if ball is on a tile and apply effect
                if 0 <= self.pos[0] < grid_size[0] and 0 <= self.pos[1] < grid_size[1]:
                    tile = grid[self.pos[1]][self.pos[0]]
                    if tile is not None:
                        self.apply_tile_effect(tile)
                        grid[self.pos[1]][self.pos[0]] = None  # Remove the tile

    def apply_tile_effect(self, tile_type):
        if tile_type == TileType.UP:
            self.velocity = [0, -1]
        elif tile_type == TileType.DOWN:
            self.velocity = [0, 1]
        elif tile_type == TileType.LEFT:
            self.velocity = [-1, 0]
        elif tile_type == TileType.RIGHT:
            self.velocity = [1, 0]
        elif tile_type == TileType.SPEED_UP:
            self.speed_multiplier += 0.5

    def reset(self, grid_size):
        self.pos = [grid_size[0] // 2, grid_size[1] // 2]
        self.velocity = [0, random.choice([-1, 1])]
        self.speed_multiplier = 1.0
        self.accumulated_movement = [0, 0]
