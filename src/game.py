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

        self.width = options.grid_size[0] * options.cell_size
        self.height = options.grid_size[1] * options.cell_size + 100

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Tile Strategy Game")

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

        self.ball = Ball(options.grid_size, options.initial_ball_speed, options.goal_size)

        self.start_time = time.time()
        self.game_over = False
        self.exit_to_menu = False
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)

        self.key_handlers = self._build_key_handlers()

    def _build_key_handlers(self):
        p1c = self.options.p1_controls
        p2c = self.options.p2_controls
        return {
            p1c['up']:    lambda: self.player1.move_cursor(0, -1, self.options.grid_size),
            p1c['down']:  lambda: self.player1.move_cursor(0, 1, self.options.grid_size),
            p1c['left']:  lambda: self.player1.move_cursor(-1, 0, self.options.grid_size),
            p1c['right']: lambda: self.player1.move_cursor(1, 0, self.options.grid_size),
            p1c['tile1']: lambda: self.place_tile(self.player1, 0),
            p1c['tile2']: lambda: self.place_tile(self.player1, 1),
            p1c['tile3']: lambda: self.place_tile(self.player1, 2),
            p2c['up']:    lambda: self.player2.move_cursor(0, -1, self.options.grid_size),
            p2c['down']:  lambda: self.player2.move_cursor(0, 1, self.options.grid_size),
            p2c['left']:  lambda: self.player2.move_cursor(-1, 0, self.options.grid_size),
            p2c['right']: lambda: self.player2.move_cursor(1, 0, self.options.grid_size),
            p2c['tile1']: lambda: self.place_tile(self.player2, 0),
            p2c['tile2']: lambda: self.place_tile(self.player2, 1),
            p2c['tile3']: lambda: self.place_tile(self.player2, 2),
        }

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_to_menu = True
                elif self.game_over and event.key == pygame.K_r:
                    self.reset_game()
                elif not self.game_over:
                    handler = self.key_handlers.get(event.key)
                    if handler:
                        handler()

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

        goal1_rect = pygame.Rect(0, goal_y, self.options.cell_size, goal_height)
        pygame.draw.rect(self.screen, RED, goal1_rect)

        goal2_rect = pygame.Rect(
            (self.options.grid_size[0] - 1) * self.options.cell_size,
            goal_y,
            self.options.cell_size,
            goal_height,
        )
        pygame.draw.rect(self.screen, BLUE, goal2_rect)

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

        self.player1.tile_bank.reset()
        self.player2.tile_bank.reset()

        # Reset ball
        self.ball.reset(self.options.grid_size, self.options.initial_ball_speed)

        # Reset game state
        self.start_time = time.time()
        self.game_over = False

    def run(self):
        clock = pygame.time.Clock()
        while not self.exit_to_menu:
            self.handle_input()
            if self.exit_to_menu:
                break
            if not self.game_over:
                self.update()
            self.draw()
            clock.tick(60)
