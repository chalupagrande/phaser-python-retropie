# game.py
import pygame
import sys
import time
from colors import *
from player import Player
from ball import Ball
from tile_bank import TileBank
from tile_type import TileType


class Game:
    def __init__(self, options):
        self.options = options
        self.debug = False  # Set to True to enable debug output

        # Calculate window dimensions based on grid
        self.width = options.grid_size[0] * options.cell_size
        self.height = options.grid_size[1] * options.cell_size + 100  # Extra space for UI at top

        # Initialize display
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Tile Strategy Game")
        
        # Print configured options for debugging
        if self.debug:
            print(f"Game initialized with options:")
            print(f"Grid size: {options.grid_size}")
            print(f"Cell size: {options.cell_size}")
            print(f"Goal size: {options.goal_size}")
            print(f"Tile bank size: {options.tile_bank_size}")
            print(f"Tile replenish time: {options.tile_replenish_time}")
            print(f"Game duration: {options.game_duration}")
            print(f"Ball speed: {options.initial_ball_speed}")

        # Initialize game grid with None values (no tiles)
        self.grid = [
            [None for _ in range(options.grid_size[0])]
            for _ in range(options.grid_size[1])
        ]
        
        # Grid to track which player placed each tile
        self.tile_owners = [
            [None for _ in range(options.grid_size[0])]
            for _ in range(options.grid_size[1])
        ]

        # Initialize players
        self.player1 = Player(1, RED, "left")
        self.player2 = Player(2, BLUE, "right")

        # Set initial cursor positions
        self.player1.cursor_pos = [3, options.grid_size[1] // 2]
        self.player2.cursor_pos = [options.grid_size[0] - 4, options.grid_size[1] // 2]

        # Initialize tile banks
        self.player1.tile_bank = TileBank(
            options.tile_bank_size, options.tile_replenish_time, options.tile_limit
        )
        self.player2.tile_bank = TileBank(
            options.tile_bank_size, options.tile_replenish_time, options.tile_limit
        )

        # Initialize ball
        self.ball = Ball(options.grid_size, options.initial_ball_speed)

        # Game state
        self.start_time = time.time()
        self.game_over = False
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Player 1 movement
                if event.key == self.options.p1_controls['up']:
                    self.player1.move_cursor(0, -1, self.options.grid_size)
                elif event.key == self.options.p1_controls['down']:
                    self.player1.move_cursor(0, 1, self.options.grid_size)
                elif event.key == self.options.p1_controls['left']:
                    self.player1.move_cursor(-1, 0, self.options.grid_size)
                elif event.key == self.options.p1_controls['right']:
                    self.player1.move_cursor(1, 0, self.options.grid_size)
                
                # Player 2 movement
                elif event.key == self.options.p2_controls['up']:
                    self.player2.move_cursor(0, -1, self.options.grid_size)
                elif event.key == self.options.p2_controls['down']:
                    self.player2.move_cursor(0, 1, self.options.grid_size)
                elif event.key == self.options.p2_controls['left']:
                    self.player2.move_cursor(-1, 0, self.options.grid_size)
                elif event.key == self.options.p2_controls['right']:
                    self.player2.move_cursor(1, 0, self.options.grid_size)
                
                # Player 1 tile placement
                elif event.key == self.options.p1_controls['tile1']:
                    self.place_tile(self.player1, 0)
                elif event.key == self.options.p1_controls['tile2']:
                    self.place_tile(self.player1, 1)
                elif event.key == self.options.p1_controls['tile3']:
                    self.place_tile(self.player1, 2)

                # Player 2 tile placement
                elif event.key == self.options.p2_controls['tile1']:
                    self.place_tile(self.player2, 0)
                elif event.key == self.options.p2_controls['tile2']:
                    self.place_tile(self.player2, 1)
                elif event.key == self.options.p2_controls['tile3']:
                    self.place_tile(self.player2, 2)

        # Movement is now handled in the KEYDOWN event, not here

    def update(self):
        # Update tile banks
        self.player1.tile_bank.update()
        self.player2.tile_bank.update()

        # Store the grid before update to detect tile removals
        old_grid = [row[:] for row in self.grid]
        
        # Update ball
        self.ball.update(self.grid, self.options.grid_size)
        
        # Check for removed tiles and update tile counts
        for y in range(self.options.grid_size[1]):
            for x in range(self.options.grid_size[0]):
                if old_grid[y][x] is not None and self.grid[y][x] is None:
                    # A tile was removed at this position
                    owner_id = self.tile_owners[y][x]
                    if owner_id == 1:
                        self.player1.tile_bank.remove_tile_from_board()
                    elif owner_id == 2:
                        self.player2.tile_bank.remove_tile_from_board()
                    # Clear the owner
                    self.tile_owners[y][x] = None

        # Calculate goal dimensions in grid coordinates
        goal_height_cells = self.options.goal_size
        goal_center_y = self.options.grid_size[1] / 2
        goal_top_cell = goal_center_y - (goal_height_cells / 2)
        goal_bottom_cell = goal_top_cell + goal_height_cells
        
        # Debug goal position
        if self.debug:
            print(f"Goal range: {goal_top_cell} to {goal_bottom_cell}, Ball Y: {self.ball.pos[1]}")
        
        # Check if ball is within goal height range
        if goal_top_cell <= self.ball.pos[1] <= goal_bottom_cell:
            # Check for left goal (Player 2 scores)
            if self.ball.pos[0] <= 0.1:  # Use a small threshold to detect goal
                self.player2.score += 1
                print(f"GOAL! Player 2 scores! New score: P1 {self.player1.score} - {self.player2.score} P2")
                self.ball.reset(self.options.grid_size)
            # Check for right goal (Player 1 scores)
            elif self.ball.pos[0] >= self.options.grid_size[0] - 0.1:  # Use a small threshold
                self.player1.score += 1
                print(f"GOAL! Player 1 scores! New score: P1 {self.player1.score} - {self.player2.score} P2")
                self.ball.reset(self.options.grid_size)
        # Ball hit wall but not goal
        elif self.ball.pos[0] < 0 or self.ball.pos[0] >= self.options.grid_size[0]:
            self.ball.velocity[0] *= -1  # Bounce horizontally

        # Check if game time is up
        current_time = time.time()
        if current_time - self.start_time >= self.options.game_duration:
            self.game_over = True

    def draw_tile(self, x, y, tile_type, cell_size):
        rect = pygame.Rect(x, y, cell_size, cell_size)

        # Draw base tile
        pygame.draw.rect(self.screen, LIGHT_GRAY, rect)
        pygame.draw.rect(self.screen, DARK_GRAY, rect, 2)

        # Draw tile icon based on type
        if tile_type == TileType.UP:
            # Draw up arrow
            pygame.draw.polygon(
                self.screen,
                BLACK,
                [
                    (x + cell_size // 2, y + cell_size // 4),
                    (x + cell_size * 3 // 4, y + cell_size * 3 // 4),
                    (x + cell_size // 4, y + cell_size * 3 // 4),
                ],
            )
        elif tile_type == TileType.DOWN:
            # Draw down arrow
            pygame.draw.polygon(
                self.screen,
                BLACK,
                [
                    (x + cell_size // 2, y + cell_size * 3 // 4),
                    (x + cell_size * 3 // 4, y + cell_size // 4),
                    (x + cell_size // 4, y + cell_size // 4),
                ],
            )
        elif tile_type == TileType.LEFT:
            # Draw left arrow
            pygame.draw.polygon(
                self.screen,
                BLACK,
                [
                    (x + cell_size // 4, y + cell_size // 2),
                    (x + cell_size * 3 // 4, y + cell_size // 4),
                    (x + cell_size * 3 // 4, y + cell_size * 3 // 4),
                ],
            )
        elif tile_type == TileType.RIGHT:
            # Draw right arrow
            pygame.draw.polygon(
                self.screen,
                BLACK,
                [
                    (x + cell_size * 3 // 4, y + cell_size // 2),
                    (x + cell_size // 4, y + cell_size // 4),
                    (x + cell_size // 4, y + cell_size * 3 // 4),
                ],
            )
        elif tile_type == TileType.SPEED_UP:
            # Draw speed up symbol (double chevron)
            pygame.draw.polygon(
                self.screen,
                BLACK,
                [
                    (x + cell_size * 1 // 5, y + cell_size * 1 // 4),
                    (x + cell_size * 2 // 5, y + cell_size // 2),
                    (x + cell_size * 1 // 5, y + cell_size * 3 // 4),
                ],
            )
            pygame.draw.polygon(
                self.screen,
                BLACK,
                [
                    (x + cell_size * 3 // 5, y + cell_size * 1 // 4),
                    (x + cell_size * 4 // 5, y + cell_size // 2),
                    (x + cell_size * 3 // 5, y + cell_size * 3 // 4),
                ],
            )

    def draw(self):
        # Fill background
        self.screen.fill(WHITE)
        
        # Draw top UI bar
        pygame.draw.rect(self.screen, LIGHT_GRAY, (0, 0, self.width, 100))
        
        # Draw scores in the center
        score_text = self.font.render(f"Score: P1 {self.player1.score} - {self.player2.score} P2", True, BLACK)
        score_rect = score_text.get_rect(center=(self.width // 2, 25))
        self.screen.blit(score_text, score_rect)
        
        # Draw time remaining in the center
        time_left = max(0, self.options.game_duration - (time.time() - self.start_time))
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)
        time_text = self.font.render(f"Time: {minutes:02}:{seconds:02}", True, BLACK)
        time_rect = time_text.get_rect(center=(self.width // 2, 60))
        self.screen.blit(time_text, time_rect)
        
        # Draw Player 1 tile bank (left side)
        p1_tile_keys = [
            pygame.key.name(self.options.p1_controls['tile1']),
            pygame.key.name(self.options.p1_controls['tile2']),
            pygame.key.name(self.options.p1_controls['tile3'])
        ]
        p1_bank_text = self.small_font.render(f"P1 Tiles ({p1_tile_keys[0]},{p1_tile_keys[1]},{p1_tile_keys[2]})", True, RED)
        self.screen.blit(p1_bank_text, (20, 15))
        
        # Display tiles on board count for Player 1
        tiles_on_board = self.player1.tile_bank.tiles_on_board
        tile_limit = self.player1.tile_bank.tile_limit
        p1_count_text = self.small_font.render(f"Tiles: {tiles_on_board}/{tile_limit}", True, RED)
        self.screen.blit(p1_count_text, (20, 35))
        
        for i in range(self.options.tile_bank_size):
            bank_rect = pygame.Rect(20 + i * 50, 55, 40, 40)
            pygame.draw.rect(self.screen, LIGHT_GRAY, bank_rect)
            pygame.draw.rect(self.screen, RED, bank_rect, 2)
            
            if self.player1.tile_bank.slots[i] is not None:
                self.draw_tile(20 + i * 50, 55, self.player1.tile_bank.slots[i], 40)
        
        # Draw Player 2 tile bank (right side)
        p2_tile_keys = [
            pygame.key.name(self.options.p2_controls['tile1']),
            pygame.key.name(self.options.p2_controls['tile2']),
            pygame.key.name(self.options.p2_controls['tile3'])
        ]
        p2_bank_text = self.small_font.render(f"P2 Tiles ({p2_tile_keys[0]},{p2_tile_keys[1]},{p2_tile_keys[2]})", True, BLUE)
        p2_text_width = p2_bank_text.get_width()
        self.screen.blit(p2_bank_text, (self.width - p2_text_width - 20, 15))
        
        # Display tiles on board count for Player 2
        tiles_on_board = self.player2.tile_bank.tiles_on_board
        tile_limit = self.player2.tile_bank.tile_limit
        p2_count_text = self.small_font.render(f"Tiles: {tiles_on_board}/{tile_limit}", True, BLUE)
        p2_count_width = p2_count_text.get_width()
        self.screen.blit(p2_count_text, (self.width - p2_count_width - 20, 35))
        
        for i in range(self.options.tile_bank_size):
            bank_rect = pygame.Rect(self.width - 20 - (self.options.tile_bank_size - i) * 50, 55, 40, 40)
            pygame.draw.rect(self.screen, LIGHT_GRAY, bank_rect)
            pygame.draw.rect(self.screen, BLUE, bank_rect, 2)
            
            if self.player2.tile_bank.slots[i] is not None:
                self.draw_tile(self.width - 20 - (self.options.tile_bank_size - i) * 50, 55, self.player2.tile_bank.slots[i], 40)
        
        # Draw grid (shifted down to accommodate the top UI)
        for y in range(self.options.grid_size[1]):
            for x in range(self.options.grid_size[0]):
                rect = pygame.Rect(
                    x * self.options.cell_size,
                    y * self.options.cell_size + 100,  # Shift down by 100px
                    self.options.cell_size,
                    self.options.cell_size,
                )
                pygame.draw.rect(self.screen, GRAY, rect, 1)

                # Draw tile if exists
                if self.grid[y][x] is not None:
                    self.draw_tile(
                        x * self.options.cell_size,
                        y * self.options.cell_size + 100,  # Shift down by 100px
                        self.grid[y][x],
                        self.options.cell_size,
                    )

        # Draw goals (shifted down to accommodate the top UI)
        goal_height = self.options.goal_size * self.options.cell_size
        
        # Calculate goal position to match the logical goal position
        goal_center_y = self.options.grid_size[1] / 2
        goal_top_cell = goal_center_y - (self.options.goal_size / 2)
        goal_y = int(goal_top_cell * self.options.cell_size) + 100  # Add UI offset

        # Player 1 goal (left)
        goal1_rect = pygame.Rect(0, goal_y, 10, goal_height)
        pygame.draw.rect(self.screen, RED, goal1_rect)
        
        # Draw goal area indicator with grid lines
        goal_area_rect = pygame.Rect(
            0, goal_y, self.options.cell_size, goal_height
        )
        pygame.draw.rect(self.screen, (255, 200, 200, 128), goal_area_rect)  # Semi-transparent red
        
        # Draw horizontal lines to show goal cell boundaries
        for i in range(self.options.goal_size + 1):
            y_pos = goal_y + i * self.options.cell_size
            pygame.draw.line(self.screen, RED, (0, y_pos), (self.options.cell_size, y_pos), 1)

        # Player 2 goal (right)
        goal2_rect = pygame.Rect(
            self.options.grid_size[0] * self.options.cell_size - 10, goal_y, 10, goal_height
        )
        pygame.draw.rect(self.screen, BLUE, goal2_rect)
        
        # Draw goal area indicator with grid lines
        goal_area_rect = pygame.Rect(
            (self.options.grid_size[0] - 1) * self.options.cell_size, 
            goal_y, 
            self.options.cell_size, 
            goal_height
        )
        pygame.draw.rect(self.screen, (200, 200, 255, 128), goal_area_rect)  # Semi-transparent blue
        
        # Draw horizontal lines to show goal cell boundaries
        for i in range(self.options.goal_size + 1):
            y_pos = goal_y + i * self.options.cell_size
            pygame.draw.line(self.screen, BLUE, 
                            ((self.options.grid_size[0] - 1) * self.options.cell_size, y_pos), 
                            (self.options.grid_size[0] * self.options.cell_size, y_pos), 1)

        # Draw player cursors (shifted down to accommodate the top UI)
        p1_cursor_rect = pygame.Rect(
            self.player1.cursor_pos[0] * self.options.cell_size,
            self.player1.cursor_pos[1] * self.options.cell_size + 100,  # Shift down by 100px
            self.options.cell_size,
            self.options.cell_size,
        )
        pygame.draw.rect(self.screen, self.player1.cursor_color, p1_cursor_rect, 3)

        p2_cursor_rect = pygame.Rect(
            self.player2.cursor_pos[0] * self.options.cell_size,
            self.player2.cursor_pos[1] * self.options.cell_size + 100,  # Shift down by 100px
            self.options.cell_size,
            self.options.cell_size,
        )
        pygame.draw.rect(self.screen, self.player2.cursor_color, p2_cursor_rect, 3)

        # Draw ball (shifted down to accommodate the top UI)
        ball_radius = self.options.cell_size // 3
        ball_x = int(
            self.ball.pos[0] * self.options.cell_size
        )
        ball_y = int(
            self.ball.pos[1] * self.options.cell_size + 100  # Shift down by 100px
        )
        pygame.draw.circle(self.screen, BLACK, (ball_x, ball_y), ball_radius)
        
        # Draw crosshair at ball center for better visibility
        pygame.draw.line(self.screen, RED, (ball_x - 5, ball_y), (ball_x + 5, ball_y), 1)
        pygame.draw.line(self.screen, RED, (ball_x, ball_y - 5), (ball_x, ball_y + 5), 1)
        
        # Draw grid cell boundaries for debugging
        current_cell_x = int(self.ball.pos[0])
        current_cell_y = int(self.ball.pos[1])
        cell_rect = pygame.Rect(
            current_cell_x * self.options.cell_size,
            current_cell_y * self.options.cell_size + 100,
            self.options.cell_size,
            self.options.cell_size
        )
        pygame.draw.rect(self.screen, GREEN, cell_rect, 1)
        
        # Draw a small dot at the center of the ball for visual reference
        pygame.draw.circle(self.screen, RED, (ball_x, ball_y), 2)

        # Draw game over message if needed
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))

            if self.player1.score > self.player2.score:
                result_text = "Player 1 Wins!"
                color = RED
            elif self.player2.score > self.player1.score:
                result_text = "Player 2 Wins!"
                color = BLUE
            else:
                result_text = "Game Tied!"
                color = GREEN

            game_over_font = pygame.font.SysFont(None, 72)
            game_over_text = game_over_font.render(result_text, True, color)
            text_rect = game_over_text.get_rect(
                center=(self.width // 2, self.height // 2)
            )
            self.screen.blit(game_over_text, text_rect)

            restart_text = self.font.render("Press R to Restart", True, WHITE)
            restart_rect = restart_text.get_rect(
                center=(self.width // 2, self.height // 2 + 50)
            )
            self.screen.blit(restart_text, restart_rect)

        # Update display
        pygame.display.flip()

    def place_tile(self, player, slot_index):
        """Helper method to place a tile at the player's cursor position"""
        if (0 <= player.cursor_pos[1] < self.options.grid_size[1] and
            0 <= player.cursor_pos[0] < self.options.grid_size[0]):
            if self.grid[player.cursor_pos[1]][player.cursor_pos[0]] is None:
                tile = player.tile_bank.use_tile(slot_index)
                if tile:
                    self.grid[player.cursor_pos[1]][player.cursor_pos[0]] = tile
                    # Track which player placed this tile
                    self.tile_owners[player.cursor_pos[1]][player.cursor_pos[0]] = player.id
                    
    def reset_game(self):
        # Reset grid
        self.grid = [
            [None for _ in range(self.options.grid_size[0])]
            for _ in range(self.options.grid_size[1])
        ]
        
        # Reset tile owners
        self.tile_owners = [
            [None for _ in range(self.options.grid_size[0])]
            for _ in range(self.options.grid_size[1])
        ]

        # Reset scores
        self.player1.score = 0
        self.player2.score = 0

        # Reset cursors
        self.player1.cursor_pos = [3, self.options.grid_size[1] // 2]
        self.player2.cursor_pos = [
            self.options.grid_size[0] - 4,
            self.options.grid_size[1] // 2,
        ]

        # Reset tile banks
        self.player1.tile_bank = TileBank(
            self.options.tile_bank_size, self.options.tile_replenish_time, self.options.tile_limit
        )
        self.player2.tile_bank = TileBank(
            self.options.tile_bank_size, self.options.tile_replenish_time, self.options.tile_limit
        )

        # Reset ball
        self.ball.reset(self.options.grid_size, self.options.initial_ball_speed)

        # Reset game state
        self.start_time = time.time()
        self.game_over = False

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.handle_input()

            if not self.game_over:
                self.update()
            else:
                # Check for restart
                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:
                    self.reset_game()

            self.draw()
            clock.tick(60)
