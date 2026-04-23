# game.py
import math
import pygame
import sys
import time
from colors import *
from player import Player
from ball import Ball
from tile_bank import TileBank
from tile_type import TileType

RETRO_FONT = "couriernew,menlo,consolas,monospace"


class Game:
    def __init__(self, options, screen):
        self.options = options

        self.width = options.grid_size[0] * options.cell_size
        self.height = options.grid_size[1] * options.cell_size + 100

        self.screen = screen
        self.game_surface = pygame.Surface((self.width, self.height)).convert_alpha()
        self.offset_x = (screen.get_width() - self.width) // 2
        self.offset_y = (screen.get_height() - self.height) // 2

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
        self.small_font = pygame.font.SysFont(RETRO_FONT, 18, bold=True)
        self.font = pygame.font.SysFont(RETRO_FONT, 26, bold=True)
        self.big_font = pygame.font.SysFont(RETRO_FONT, 40, bold=True)
        self.title_font = pygame.font.SysFont(RETRO_FONT, 64, bold=True)

        self.scanlines = self._build_scanlines()

        self.p1_actions = self._build_player_actions(self.player1)
        self.p2_actions = self._build_player_actions(self.player2)
        self._axis_state = {}
        self.key_handlers = self._build_key_handlers()

    def _build_scanlines(self):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for y in range(0, self.height, 3):
            pygame.draw.line(surf, (0, 0, 0, 70), (0, y), (self.width, y))
        return surf

    def _build_player_actions(self, player):
        return {
            "up":    lambda: player.move_cursor(0, -1, self.options.grid_size),
            "down":  lambda: player.move_cursor(0, 1, self.options.grid_size),
            "left":  lambda: player.move_cursor(-1, 0, self.options.grid_size),
            "right": lambda: player.move_cursor(1, 0, self.options.grid_size),
            "tile1": lambda: self.place_tile(player, 0),
            "tile2": lambda: self.place_tile(player, 1),
            "tile3": lambda: self.place_tile(player, 2),
        }

    def _build_key_handlers(self):
        handlers = {}
        for mode, controls, actions in (
            (self.options.p1_input, self.options.p1_controls, self.p1_actions),
            (self.options.p2_input, self.options.p2_controls, self.p2_actions),
        ):
            if mode == "keyboard":
                for name, action in actions.items():
                    handlers[controls[name]] = action
        return handlers

    def _process_gamepad_event(self, event):
        for mode, cfg, actions in (
            (self.options.p1_input, self.options.p1_gamepad, self.p1_actions),
            (self.options.p2_input, self.options.p2_gamepad, self.p2_actions),
        ):
            if mode != "gamepad":
                continue
            if event.joy != cfg["joystick_index"]:
                continue
            for name, action in actions.items():
                binding = cfg.get(name)
                if binding and self._event_matches_binding(event, binding):
                    action()

    def _event_matches_binding(self, event, binding):
        kind = binding[0]
        if event.type == pygame.JOYBUTTONDOWN and kind == "button":
            return event.button == binding[1]
        if event.type == pygame.JOYHATMOTION and kind == "hat":
            return event.hat == binding[1] and tuple(event.value) == tuple(binding[2])
        if event.type == pygame.JOYAXISMOTION and kind == "axis":
            return self._axis_crossed(event, binding)
        return False

    def _axis_crossed(self, event, binding):
        axis_idx, sign = binding[1], binding[2]
        if event.axis != axis_idx:
            return False
        threshold = 0.5
        key = (event.joy, axis_idx, sign)
        active = (sign > 0 and event.value > threshold) or \
                 (sign < 0 and event.value < -threshold)
        was_active = self._axis_state.get(key, False)
        self._axis_state[key] = active
        return active and not was_active

    def _input_label(self, player):
        if player.id == 1:
            mode = self.options.p1_input
            kb   = self.options.p1_controls
            gp   = self.options.p1_gamepad
        else:
            mode = self.options.p2_input
            kb   = self.options.p2_controls
            gp   = self.options.p2_gamepad
        if mode == "gamepad":
            parts = []
            for i in range(3):
                b = gp.get(f'tile{i + 1}')
                parts.append(f"B{b[1]}" if b and b[0] == "button" else "??")
            return f"P{player.id} GP  {'  '.join(parts)}"
        keys = "  ".join(pygame.key.name(kb[f'tile{i + 1}']).upper() for i in range(3))
        return f"P{player.id}  {keys}"

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

            elif event.type == pygame.JOYBUTTONDOWN:
                if self.game_over:
                    self.reset_game()
                else:
                    self._process_gamepad_event(event)

            elif event.type in (pygame.JOYHATMOTION, pygame.JOYAXISMOTION):
                if not self.game_over:
                    self._process_gamepad_event(event)

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

        goal_height_cells = self.options.goal_size
        goal_center_y = self.options.grid_size[1] / 2
        goal_top_cell = goal_center_y - (goal_height_cells / 2)
        goal_bottom_cell = goal_top_cell + goal_height_cells

        field_left = 1
        field_right = self.options.grid_size[0] - 1

        if goal_top_cell <= self.ball.pos[1] <= goal_bottom_cell:
            if self.ball.pos[0] < field_left:
                self.player2.score += 1
                print(f"GOAL! Player 2 scores! New score: P1 {self.player1.score} - {self.player2.score} P2")
                self.ball.reset(self.options.grid_size)
            elif self.ball.pos[0] >= field_right:
                self.player1.score += 1
                print(f"GOAL! Player 1 scores! New score: P1 {self.player1.score} - {self.player2.score} P2")
                self.ball.reset(self.options.grid_size)
        elif self.ball.pos[0] < field_left or self.ball.pos[0] >= field_right:
            self.ball.velocity[0] *= -1

        # Check if game time is up
        current_time = time.time()
        if current_time - self.start_time >= self.options.game_duration:
            self.game_over = True

    def draw_tile(self, x, y, tile_type, cell_size, owner_id=None):
        rect = pygame.Rect(x, y, cell_size, cell_size)

        if owner_id == 1:
            glyph_color = RED
        elif owner_id == 2:
            glyph_color = BLUE
        elif tile_type == TileType.SPEED_UP:
            glyph_color = NEON_YELLOW
        else:
            glyph_color = NEON_CYAN

        pygame.draw.rect(self.game_surface, BG_TILE, rect)
        pygame.draw.rect(self.game_surface, glyph_color, rect, 2)

        if tile_type == TileType.UP:
            pygame.draw.polygon(self.game_surface, glyph_color, [
                (x + cell_size // 2, y + cell_size // 4),
                (x + cell_size * 3 // 4, y + cell_size * 3 // 4),
                (x + cell_size // 4, y + cell_size * 3 // 4),
            ])
        elif tile_type == TileType.DOWN:
            pygame.draw.polygon(self.game_surface, glyph_color, [
                (x + cell_size // 2, y + cell_size * 3 // 4),
                (x + cell_size * 3 // 4, y + cell_size // 4),
                (x + cell_size // 4, y + cell_size // 4),
            ])
        elif tile_type == TileType.LEFT:
            pygame.draw.polygon(self.game_surface, glyph_color, [
                (x + cell_size // 4, y + cell_size // 2),
                (x + cell_size * 3 // 4, y + cell_size // 4),
                (x + cell_size * 3 // 4, y + cell_size * 3 // 4),
            ])
        elif tile_type == TileType.RIGHT:
            pygame.draw.polygon(self.game_surface, glyph_color, [
                (x + cell_size * 3 // 4, y + cell_size // 2),
                (x + cell_size // 4, y + cell_size // 4),
                (x + cell_size // 4, y + cell_size * 3 // 4),
            ])
        elif tile_type == TileType.SPEED_UP:
            pygame.draw.polygon(self.game_surface, glyph_color, [
                (x + cell_size // 5, y + cell_size // 4),
                (x + cell_size * 2 // 5, y + cell_size // 2),
                (x + cell_size // 5, y + cell_size * 3 // 4),
            ])
            pygame.draw.polygon(self.game_surface, glyph_color, [
                (x + cell_size * 3 // 5, y + cell_size // 4),
                (x + cell_size * 4 // 5, y + cell_size // 2),
                (x + cell_size * 3 // 5, y + cell_size * 3 // 4),
            ])

    def _draw_cursor_brackets(self, cursor_pos, color):
        cell = self.options.cell_size
        x = cursor_pos[0] * cell
        y = cursor_pos[1] * cell + 100
        length = max(6, cell // 3)
        t = 3
        corners = [
            ((x, y),                (x + length, y),          (x, y + length)),
            ((x + cell, y),         (x + cell - length, y),   (x + cell, y + length)),
            ((x, y + cell),         (x + length, y + cell),   (x, y + cell - length)),
            ((x + cell, y + cell),  (x + cell - length, y + cell), (x + cell, y + cell - length)),
        ]
        for origin, h_end, v_end in corners:
            pygame.draw.line(self.game_surface, color, origin, h_end, t)
            pygame.draw.line(self.game_surface, color, origin, v_end, t)

    def _draw_goal(self, x, y, w, h, color):
        glow_pad = 18
        glow = pygame.Surface((w + glow_pad * 2, h + glow_pad * 2), pygame.SRCALPHA)
        for i, alpha in enumerate((30, 55, 95)):
            inset = i * 5
            pygame.draw.rect(
                glow,
                (*color, alpha),
                (inset, inset, glow.get_width() - inset * 2, glow.get_height() - inset * 2),
            )
        self.game_surface.blit(glow, (x - glow_pad, y - glow_pad))
        pygame.draw.rect(self.game_surface, color, (x, y, w, h))

    def _draw_ball(self):
        cell = self.options.cell_size
        radius = cell // 3
        x = int(self.ball.pos[0] * cell)
        y = int(self.ball.pos[1] * cell + 100)

        pulse = 0.5 + 0.5 * math.sin(time.time() * 7)
        glow_half = radius * 4
        glow = pygame.Surface((glow_half * 2, glow_half * 2), pygame.SRCALPHA)
        for r_scale, base_alpha in ((3.0, 20), (2.1, 45), (1.4, 95)):
            alpha = min(255, int(base_alpha + 35 * pulse))
            pygame.draw.circle(glow, (*NEON_YELLOW, alpha), (glow_half, glow_half), int(radius * r_scale))
        self.game_surface.blit(glow, (x - glow_half, y - glow_half))

        pygame.draw.circle(self.game_surface, NEON_YELLOW, (x, y), radius)
        pygame.draw.circle(self.game_surface, WHITE, (x, y), max(1, radius - 3))

    def _draw_bank(self, player, side):
        label = self.small_font.render(self._input_label(player), True, player.cursor_color)
        count = self.small_font.render(
            f"TILES {player.tile_bank.tiles_on_board:02d}/{player.tile_bank.tile_limit:02d}",
            True, player.cursor_color,
        )

        if side == "left":
            self.game_surface.blit(label, (20, 12))
            self.game_surface.blit(count, (20, 34))
            slot_base_x = 20
        else:
            self.game_surface.blit(label, (self.width - 20 - label.get_width(), 12))
            self.game_surface.blit(count, (self.width - 20 - count.get_width(), 34))
            slot_base_x = self.width - 20 - self.options.tile_bank_size * 50 + 10

        for i in range(self.options.tile_bank_size):
            sx = slot_base_x + i * 50
            sy = 55
            slot_rect = pygame.Rect(sx, sy, 40, 40)
            pygame.draw.rect(self.game_surface, BG_TILE, slot_rect)
            pygame.draw.rect(self.game_surface, player.cursor_color, slot_rect, 2)
            tile = player.tile_bank.slots[i]
            if tile is not None:
                self.draw_tile(sx, sy, tile, 40, owner_id=player.id)

    def _draw_game_over(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.game_surface.blit(overlay, (0, 0))

        if self.player1.score > self.player2.score:
            msg, color = "P1 WINS", RED
        elif self.player2.score > self.player1.score:
            msg, color = "P2 WINS", BLUE
        else:
            msg, color = "DRAW", NEON_YELLOW

        text = self.title_font.render(msg, True, color)
        shadow = self.title_font.render(msg, True, UI_ACCENT)
        rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.game_surface.blit(shadow, rect.move(4, 4))
        self.game_surface.blit(text, rect)

        sub = self.small_font.render("R - RESTART    ESC - MENU", True, WHITE)
        sub_rect = sub.get_rect(center=(self.width // 2, self.height // 2 + 55))
        self.game_surface.blit(sub, sub_rect)

    def draw(self):
        self.game_surface.fill(BG_DARK)

        # UI strip
        pygame.draw.rect(self.game_surface, BG_UI, (0, 0, self.width, 100))
        pygame.draw.line(self.game_surface, NEON_MAGENTA, (0, 99), (self.width, 99), 2)

        # Score block
        score_msg = f"{self.player1.score:02d}  ::  {self.player2.score:02d}"
        score_text = self.big_font.render(score_msg, True, WHITE)
        score_shadow = self.big_font.render(score_msg, True, UI_ACCENT)
        score_rect = score_text.get_rect(center=(self.width // 2, 28))
        self.game_surface.blit(score_shadow, score_rect.move(2, 2))
        self.game_surface.blit(score_text, score_rect)

        # Clock
        time_left = max(0, self.options.game_duration - (time.time() - self.start_time))
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)
        clock_color = NEON_ORANGE if time_left < 15 else NEON_YELLOW
        time_text = self.small_font.render(f"TIME  {minutes:02d}:{seconds:02d}", True, clock_color)
        time_rect = time_text.get_rect(center=(self.width // 2, 66))
        self.game_surface.blit(time_text, time_rect)

        # Tile banks
        self._draw_bank(self.player1, side="left")
        self._draw_bank(self.player2, side="right")

        # Playfield grid (skip cells under tiles and the goal-column chambers).
        cell = self.options.cell_size
        last_col = self.options.grid_size[0] - 1
        for y in range(self.options.grid_size[1]):
            for x in range(self.options.grid_size[0]):
                if x == 0 or x == last_col:
                    continue
                if self.grid[y][x] is None:
                    rect = pygame.Rect(x * cell, y * cell + 100, cell, cell)
                    pygame.draw.rect(self.game_surface, GRID_LINE, rect, 1)

        # Goals (glow first so tiles/cursors draw over the halo)
        goal_height = self.options.goal_size * cell
        goal_top_cell = self.options.grid_size[1] / 2 - self.options.goal_size / 2
        goal_y = int(goal_top_cell * cell) + 100
        self._draw_goal(0, goal_y, cell, goal_height, RED)
        self._draw_goal(
            (self.options.grid_size[0] - 1) * cell, goal_y, cell, goal_height, BLUE
        )

        # Tiles on the board
        for y in range(self.options.grid_size[1]):
            for x in range(self.options.grid_size[0]):
                if self.grid[y][x] is not None:
                    self.draw_tile(
                        x * cell, y * cell + 100,
                        self.grid[y][x], cell,
                        owner_id=self.tile_owners[y][x],
                    )

        # Cursor reticles
        self._draw_cursor_brackets(self.player1.cursor_pos, self.player1.cursor_color)
        self._draw_cursor_brackets(self.player2.cursor_pos, self.player2.cursor_color)

        # Ball
        self._draw_ball()

        if self.game_over:
            self._draw_game_over()

        # CRT scanlines on top of everything
        self.game_surface.blit(self.scanlines, (0, 0))

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.game_surface, (self.offset_x, self.offset_y))

        pygame.display.flip()

    def place_tile(self, player, slot_index):
        x = player.cursor_pos[0]
        y = player.cursor_pos[1]
        # Goal columns (leftmost + rightmost) are non-placeable so the ball
        # can only enter the goal through its front face.
        if not (1 <= x < self.options.grid_size[0] - 1):
            return
        if not (0 <= y < self.options.grid_size[1]):
            return
        if self.grid[y][x] is not None:
            return
        tile = player.tile_bank.use_tile(slot_index)
        if tile:
            self.grid[y][x] = tile
            self.tile_owners[y][x] = player.id
                    
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
