import math
import time
import pygame
from colors import *

RETRO_FONT = "couriernew,menlo,consolas,monospace"


class WelcomeScreen:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.small_font = pygame.font.SysFont(RETRO_FONT, 20, bold=True)
        self.font = pygame.font.SysFont(RETRO_FONT, 32, bold=True)
        self.title_font = pygame.font.SysFont(RETRO_FONT, 96, bold=True)
        self.subtitle_font = pygame.font.SysFont(RETRO_FONT, 22, bold=True)
        self.running = True
        self.selected_option = 0
        self.result = None
        self.scanlines = self._build_scanlines()

    def _build_scanlines(self):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for y in range(0, self.height, 3):
            pygame.draw.line(surf, (0, 0, 0, 70), (0, y), (self.width, y))
        return surf

    def _confirm(self):
        self.result = 'start' if self.selected_option == 0 else 'options'
        self.running = False

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    self.selected_option = 1 - self.selected_option
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._confirm()

            elif event.type == pygame.JOYHATMOTION:
                _, dy = event.value
                if dy != 0:
                    self.selected_option = 1 - self.selected_option

            elif event.type == pygame.JOYBUTTONDOWN:
                self._confirm()

    def _draw_title(self):
        title_y = self.height // 3
        # Flicker between near-full and slightly dimmed.
        flicker = 0.88 + 0.12 * math.sin(time.time() * 9)
        main = tuple(min(255, int(c * flicker)) for c in NEON_MAGENTA)

        shadow_cyan = self.title_font.render("PHASER", True, NEON_CYAN)
        shadow_pink = self.title_font.render("PHASER", True, UI_ACCENT)
        main_text   = self.title_font.render("PHASER", True, main)
        rect = main_text.get_rect(center=(self.width // 2, title_y))

        # Layered offsets create a chromatic-aberration look.
        self.screen.blit(shadow_cyan, rect.move(-4, 0))
        self.screen.blit(shadow_pink, rect.move(4, 4))
        self.screen.blit(main_text, rect)

        subtitle = self.subtitle_font.render("~ TILE STRATEGY ~", True, NEON_CYAN)
        sub_rect = subtitle.get_rect(center=(self.width // 2, title_y + 70))
        self.screen.blit(subtitle, sub_rect)

    def _draw_option(self, text, y, selected):
        if selected:
            pulse = 0.7 + 0.3 * math.sin(time.time() * 6)
            color = tuple(min(255, int(c * pulse + (1 - pulse) * 80)) for c in NEON_YELLOW)
            label = f">  {text}  <"
        else:
            color = NEON_CYAN
            label = text
        surface = self.font.render(label, True, color)
        rect = surface.get_rect(center=(self.width // 2, y))
        self.screen.blit(surface, rect)

    def draw(self):
        self.screen.fill(BG_DARK)

        self._draw_title()

        self._draw_option("START GAME", self.height // 2 + 30, self.selected_option == 0)
        self._draw_option("OPTIONS",    self.height // 2 + 80, self.selected_option == 1)

        instructions = self.small_font.render(
            "UP / DOWN - NAVIGATE     ENTER - SELECT     ESC - QUIT",
            True, GRAY,
        )
        instructions_rect = instructions.get_rect(center=(self.width // 2, self.height - 60))
        self.screen.blit(instructions, instructions_rect)

        self.screen.blit(self.scanlines, (0, 0))
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_input()
            self.draw()
            pygame.time.delay(30)

        return self.result
