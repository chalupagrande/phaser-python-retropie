# player.py
class Player:
    def __init__(self, id, cursor_color, goal_side):
        self.id = id
        self.cursor_color = cursor_color
        self.goal_side = goal_side  # "left" or "right"
        self.score = 0
        self.cursor_pos = [0, 0]  # Grid coordinates
        self.tile_bank = None  # Will be initialized in the Game class
        self.movement_accumulator = [0, 0]  # For fractional cursor movement

    def move_cursor(self, dx, dy, grid_size, sensitivity=1.0):
        # For discrete movement, we'll move exactly one cell in the specified direction
        if dx != 0 or dy != 0:
            # Normalize direction to exactly one cell
            dx = 1 if dx > 0 else (-1 if dx < 0 else 0)
            dy = 1 if dy > 0 else (-1 if dy < 0 else 0)
            
            # Apply bounds checking
            new_x = max(0, min(grid_size[0] - 1, self.cursor_pos[0] + dx))
            new_y = max(0, min(grid_size[1] - 1, self.cursor_pos[1] + dy))
            self.cursor_pos = [new_x, new_y]
