"""Gamepad calibration UI and persistence.

Walks a player through pressing one input per gameplay action, captures each
binding as a (kind, ...) tuple compatible with ``Game._event_matches_binding``,
and writes the result to ``calibration.json`` at the repo root. ``apply_calibration``
is called once at startup to overlay any saved bindings onto ``GameOptions``.
"""

import json
import os
import sys
import pygame
from colors import *

RETRO_FONT = "couriernew,menlo,consolas,monospace"

CALIBRATION_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "calibration.json",
)

AXIS_THRESHOLD = 0.6
COOLDOWN_MS = 600


def load_calibration():
    try:
        with open(CALIBRATION_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_calibration(player_id, gamepad):
    data = load_calibration()
    data[f"p{player_id}"] = _serialize(gamepad)
    with open(CALIBRATION_PATH, "w") as f:
        json.dump(data, f, indent=2)


def apply_calibration(options):
    data = load_calibration()
    for pid in (1, 2):
        raw = data.get(f"p{pid}")
        if not raw:
            continue
        target = options.p1_gamepad if pid == 1 else options.p2_gamepad
        target.update(_deserialize(raw))


def _serialize(gamepad):
    return {k: list(v) if isinstance(v, tuple) else v for k, v in gamepad.items()}


def _deserialize(raw):
    out = {}
    for k, v in raw.items():
        if k == "joystick_index":
            out[k] = v
        elif isinstance(v, list) and len(v) == 3 and v[0] == "hat":
            out[k] = (v[0], v[1], tuple(v[2]))
        elif isinstance(v, list):
            out[k] = tuple(v)
        else:
            out[k] = v
    return out


def _binding_from_event(event):
    if event.type == pygame.JOYBUTTONDOWN:
        return ("button", event.button)
    if event.type == pygame.JOYHATMOTION:
        dx, dy = event.value
        if (dx, dy) != (0, 0):
            return ("hat", event.hat, (dx, dy))
    if event.type == pygame.JOYAXISMOTION:
        if abs(event.value) > AXIS_THRESHOLD:
            sign = 1 if event.value > 0 else -1
            return ("axis", event.axis, sign)
    return None


def _describe_binding(binding):
    kind = binding[0]
    if kind == "button":
        return f"BUTTON {binding[1]}"
    if kind == "hat":
        dx, dy = binding[2]
        return f"HAT {binding[1]} {_hat_direction(dx, dy)}"
    if kind == "axis":
        sign = "+" if binding[2] > 0 else "-"
        return f"AXIS {binding[1]} {sign}"
    return "?"


def _hat_direction(dx, dy):
    if dy > 0: return "UP"
    if dy < 0: return "DOWN"
    if dx > 0: return "RIGHT"
    if dx < 0: return "LEFT"
    return "-"


class Calibrator:
    ACTIONS = [
        ("up",    "MOVE UP"),
        ("down",  "MOVE DOWN"),
        ("left",  "MOVE LEFT"),
        ("right", "MOVE RIGHT"),
        ("tile1", "TILE SLOT 1"),
        ("tile2", "TILE SLOT 2"),
        ("tile3", "TILE SLOT 3"),
    ]

    def __init__(self, screen, options, player_id):
        self.screen = screen
        self.options = options
        self.player_id = player_id
        self.width, self.height = screen.get_size()
        self.small_font = pygame.font.SysFont(RETRO_FONT, 20, bold=True)
        self.font = pygame.font.SysFont(RETRO_FONT, 28, bold=True)
        self.big_font = pygame.font.SysFont(RETRO_FONT, 48, bold=True)
        self.title_font = pygame.font.SysFont(RETRO_FONT, 52, bold=True)

    def run(self):
        bindings = {}
        joy_id = None
        clock = pygame.time.Clock()

        for step, (action_key, action_label) in enumerate(self.ACTIONS):
            binding, captured_joy = self._capture_step(step, action_label, joy_id, clock)
            if binding is None:
                return False
            if joy_id is None:
                joy_id = captured_joy
            bindings[action_key] = binding
            self._flash_captured(binding)

        gamepad = {"joystick_index": joy_id, **bindings}
        if self.player_id == 1:
            self.options.p1_gamepad = gamepad
        else:
            self.options.p2_gamepad = gamepad
        save_calibration(self.player_id, gamepad)
        self._flash_done()
        return True

    def _capture_step(self, step, action_label, required_joy, clock):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return None, None
                binding = _binding_from_event(event)
                if binding is None:
                    continue
                if required_joy is not None and event.joy != required_joy:
                    continue
                return binding, event.joy
            self._draw_step(step, action_label)
            clock.tick(60)

    def _draw_step(self, step, action_label):
        self.screen.fill(BG_DARK)
        self._draw_title()

        prompt = self.font.render("PRESS INPUT FOR", True, NEON_CYAN)
        action = self.big_font.render(action_label, True, NEON_YELLOW)
        step_text = self.small_font.render(
            f"{step + 1} / {len(self.ACTIONS)}", True, GRAY,
        )
        cancel = self.small_font.render("ESC - CANCEL", True, GRAY)

        self.screen.blit(prompt, prompt.get_rect(center=(self.width // 2, self.height // 2 - 40)))
        self.screen.blit(action, action.get_rect(center=(self.width // 2, self.height // 2 + 20)))
        self.screen.blit(step_text, step_text.get_rect(center=(self.width // 2, self.height // 2 + 90)))
        self.screen.blit(cancel, cancel.get_rect(center=(self.width // 2, self.height - 60)))

        pygame.display.flip()

    def _draw_title(self):
        text = f"CALIBRATE P{self.player_id}"
        main = self.title_font.render(text, True, NEON_MAGENTA)
        shadow = self.title_font.render(text, True, NEON_CYAN)
        rect = main.get_rect(center=(self.width // 2, self.height // 4))
        self.screen.blit(shadow, rect.move(-3, 3))
        self.screen.blit(main, rect)

    def _flash_captured(self, binding):
        self.screen.fill(BG_DARK)
        self._draw_title()
        captured = self.big_font.render("CAPTURED", True, NEON_GREEN)
        desc = self.font.render(_describe_binding(binding), True, WHITE)
        self.screen.blit(captured, captured.get_rect(center=(self.width // 2, self.height // 2 - 20)))
        self.screen.blit(desc, desc.get_rect(center=(self.width // 2, self.height // 2 + 30)))
        pygame.display.flip()

        # Drain events during a short cooldown so a held input doesn't carry
        # into the next step.
        start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start < COOLDOWN_MS:
            pygame.event.get()
            pygame.time.wait(15)

    def _flash_done(self):
        self.screen.fill(BG_DARK)
        self._draw_title()
        done = self.big_font.render("CALIBRATION SAVED", True, NEON_GREEN)
        self.screen.blit(done, done.get_rect(center=(self.width // 2, self.height // 2)))
        pygame.display.flip()
        pygame.time.wait(1000)
