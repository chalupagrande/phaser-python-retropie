# player.py
class Player:
    def __init__(self, id, cursor_color, goal_side):
        self.id = id
        self.cursor_color = cursor_color
        self.goal_side = goal_side  # "left" or "right"
        self.score = 0
        self.cursor_pos = [0, 0]  # Grid coordinates
        self.tile_bank = None  # Will be initialized in the Game class

    def move_cursor(self, dx, dy, grid_size):
        new_x = max(0, min(grid_size[0] - 1, self.cursor_pos[0] + dx))
        new_y = max(0, min(grid_size[1] - 1, self.cursor_pos[1] + dy))
        self.cursor_pos = [new_x, new_y]
