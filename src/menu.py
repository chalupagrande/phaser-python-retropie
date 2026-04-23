import pygame
from colors import *

RETRO_FONT = "couriernew,menlo,consolas,monospace"


class MenuItem:
    def __init__(self, text, value=None, min_value=None, max_value=None, options=None, callback=None, action=None):
        self.text = text
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.options = options
        self.callback = callback
        self.action = action
        self.selected = False
        self.editing = False

    def select(self):
        if self.action:
            self.action()

    def increase(self):
        if self.options:
            current_index = self.options.index(self.value)
            next_index = (current_index + 1) % len(self.options)
            self.value = self.options[next_index]
        elif self.max_value is not None:
            self.value = min(self.value + 1, self.max_value)

        if self.callback:
            self.callback(self.value)

    def decrease(self):
        if self.options:
            current_index = self.options.index(self.value)
            prev_index = (current_index - 1) % len(self.options)
            self.value = self.options[prev_index]
        elif self.min_value is not None:
            self.value = max(self.value - 1, self.min_value)

        if self.callback:
            self.callback(self.value)

    def draw(self, screen, label_x, value_x, y, font):
        label_color = NEON_YELLOW if self.selected else NEON_CYAN
        label_surf = font.render(self.text.upper(), True, label_color)
        label_rect = label_surf.get_rect(midleft=(label_x, y))
        screen.blit(label_surf, label_rect)

        if self.value is None:
            return y + 42

        if self.selected:
            value_text = f"<  {self.value}  >"
            value_color = NEON_PINK
        else:
            value_text = str(self.value)
            value_color = WHITE

        value_surf = font.render(value_text, True, value_color)
        value_rect = value_surf.get_rect(midright=(value_x, y))
        screen.blit(value_surf, value_rect)
        return y + 42


class Menu:
    def __init__(self, screen, options):
        self.screen = screen
        self.options = options
        self.width, self.height = screen.get_size()
        self.small_font = pygame.font.SysFont(RETRO_FONT, 18, bold=True)
        self.font = pygame.font.SysFont(RETRO_FONT, 22, bold=True)
        self.title_font = pygame.font.SysFont(RETRO_FONT, 52, bold=True)
        self.items = []
        self.selected_index = 0
        self.running = True
        self.result = None
        self.scanlines = self._build_scanlines()

        self.create_menu_items()

    def _build_scanlines(self):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for y in range(0, self.height, 3):
            pygame.draw.line(surf, (0, 0, 0, 70), (0, y), (self.width, y))
        return surf

    def create_menu_items(self):
        def update_grid_width(value):
            self.options.grid_size = (value, self.options.grid_size[1])

        def update_grid_height(value):
            self.options.grid_size = (self.options.grid_size[0], value)

        self.items.append(MenuItem("Grid Width", self.options.grid_size[0], 10, 30, callback=update_grid_width))
        self.items.append(MenuItem("Grid Height", self.options.grid_size[1], 8, 20, callback=update_grid_height))

        def update_cell_size(value):
            self.options.cell_size = value

        self.items.append(MenuItem("Cell Size", self.options.cell_size, 20, 60, options=[20, 30, 40, 50, 60], callback=update_cell_size))

        def update_goal_size(value):
            self.options.goal_size = value

        self.items.append(MenuItem("Goal Size", self.options.goal_size, 2, 5, callback=update_goal_size))

        def update_tile_bank_size(value):
            self.options.tile_bank_size = value

        self.items.append(MenuItem("Tile Bank Size", self.options.tile_bank_size, 1, 5, callback=update_tile_bank_size))

        def update_replenish_time(value):
            self.options.tile_replenish_time = value

        self.items.append(MenuItem("Tile Replenish Time (s)", self.options.tile_replenish_time, 1, 10, callback=update_replenish_time))

        def update_tile_limit(value):
            self.options.tile_limit = value

        self.items.append(MenuItem("Tile Limit Before Delay", self.options.tile_limit, 5, 30, callback=update_tile_limit))

        def update_game_duration(value):
            self.options.game_duration = value

        self.items.append(MenuItem("Game Duration (s)", self.options.game_duration, 60, 600, options=[60, 120, 180, 300, 600], callback=update_game_duration))

        def update_ball_speed(value):
            self.options.initial_ball_speed = value

        self.items.append(MenuItem("Ball Speed", self.options.initial_ball_speed, 0.1, 0.5, options=[0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5], callback=update_ball_speed))

        def update_p1_input(value):
            self.options.p1_input = value

        def update_p2_input(value):
            self.options.p2_input = value

        self.items.append(MenuItem("P1 Input", self.options.p1_input, options=["keyboard", "gamepad"], callback=update_p1_input))
        self.items.append(MenuItem("Calibrate P1 Gamepad", action=lambda: self._calibrate(1)))
        self.items.append(MenuItem("P2 Input", self.options.p2_input, options=["keyboard", "gamepad"], callback=update_p2_input))
        self.items.append(MenuItem("Calibrate P2 Gamepad", action=lambda: self._calibrate(2)))

        self.items.append(MenuItem("Back", action=self._go_back))

        self.items[0].selected = True

    def _go_back(self):
        self.result = 'back'
        self.running = False

    def _calibrate(self, player_id):
        from calibration import Calibrator
        Calibrator(self.screen, self.options, player_id).run()

    def _nav(self, delta):
        self.items[self.selected_index].selected = False
        self.selected_index = (self.selected_index + delta) % len(self.items)
        self.items[self.selected_index].selected = True

    def _confirm(self):
        self.items[self.selected_index].select()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.result = 'back'
                    self.running = False
                elif event.key == pygame.K_UP:
                    self._nav(-1)
                elif event.key == pygame.K_DOWN:
                    self._nav(1)
                elif event.key == pygame.K_LEFT:
                    self.items[self.selected_index].decrease()
                elif event.key == pygame.K_RIGHT:
                    self.items[self.selected_index].increase()
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._confirm()

            elif event.type == pygame.JOYHATMOTION:
                dx, dy = event.value
                if dy > 0:
                    self._nav(-1)
                elif dy < 0:
                    self._nav(1)
                elif dx > 0:
                    self.items[self.selected_index].increase()
                elif dx < 0:
                    self.items[self.selected_index].decrease()

            elif event.type == pygame.JOYBUTTONDOWN:
                self._confirm()

    def draw(self):
        self.screen.fill(BG_DARK)

        title_main = self.title_font.render("GAME OPTIONS", True, NEON_MAGENTA)
        title_shadow = self.title_font.render("GAME OPTIONS", True, NEON_CYAN)
        title_rect = title_main.get_rect(center=(self.width // 2, 60))
        self.screen.blit(title_shadow, title_rect.move(-3, 3))
        self.screen.blit(title_main, title_rect)

        pygame.draw.line(
            self.screen, UI_ACCENT,
            (60, 105), (self.width - 60, 105), 2,
        )

        instructions = self.small_font.render(
            "UP/DOWN - NAVIGATE    LEFT/RIGHT - CHANGE    ESC - BACK",
            True, GRAY,
        )
        instructions_rect = instructions.get_rect(center=(self.width // 2, 130))
        self.screen.blit(instructions, instructions_rect)

        label_x = self.width // 2 - 240
        value_x = self.width // 2 + 240
        y = 180
        for item in self.items:
            y = item.draw(self.screen, label_x, value_x, y, self.font)

        self.screen.blit(self.scanlines, (0, 0))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_input()
            self.draw()
            pygame.time.delay(30)

        return self.result
