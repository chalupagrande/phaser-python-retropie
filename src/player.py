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
        # Accumulate movement with sensitivity applied
        self.movement_accumulator[0] += dx * sensitivity
        self.movement_accumulator[1] += dy * sensitivity
        
        # Extract whole cell movements
        move_x = int(self.movement_accumulator[0])
        move_y = int(self.movement_accumulator[1])
        
        # Keep the fractional part
        self.movement_accumulator[0] -= move_x
        self.movement_accumulator[1] -= move_y
        
        # Apply whole cell movements with bounds checking
        new_x = max(0, min(grid_size[0] - 1, self.cursor_pos[0] + move_x))
        new_y = max(0, min(grid_size[1] - 1, self.cursor_pos[1] + move_y))
        self.cursor_pos = [new_x, new_y]
