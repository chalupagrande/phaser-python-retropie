# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the game

```
pip install pygame
python main.py
```

There are no tests, linter, or build step. `phaser.sh` is a stale script pointing at a different project and should be ignored. `conda-project.yml` / `environment.yml` are empty scaffolds — pygame is the only real dependency.

## Path layout quirk

`main.py` lives at the repo root and does `sys.path.insert(1, "src")` before importing. All modules inside `src/` therefore import each other with flat names (`from game import Game`, `from tile_type import TileType`), *not* as `src.game`. New modules go in `src/` and follow the same flat-import convention. Run commands from the repo root so that `sys.path` resolves correctly.

## Screen flow

`main.py` runs an outer `while True` loop that alternates between three top-level screens, all sharing the same `pygame.display` surface and the same `GameOptions` instance:

1. `WelcomeScreen` ([src/welcome_screen.py](src/welcome_screen.py)) — returns `'start'` or `'options'`.
2. On `'start'`: a fresh `Game(options)` is constructed and `.run()` blocks until game over + user exits. `Game.__init__` *resizes* the display to `grid_size * cell_size` + a 100px UI strip, so after a game the window size differs from the 800×600 menu size — `WelcomeScreen`/`Menu` re-read `screen.get_size()` each time they're constructed and adapt.
3. On `'options'`: `Menu(screen, options)` mutates the shared `GameOptions` in place via per-item callbacks; changes apply to the *next* game started.

There is no pause / in-game menu — returning to the welcome screen requires the game-over state (time expires).

## Core game model ([src/game.py](src/game.py))

`Game` owns two parallel grids, both indexed `[y][x]` (row-major):

- `self.grid[y][x]` — the `TileType` placed at that cell, or `None`.
- `self.tile_owners[y][x]` — the player id (1 or 2) who placed that tile, or `None`.

The owner grid exists solely to attribute on-board-tile counts back to the right `TileBank` when a tile is consumed. In `Game.update` ([src/game.py:123-140](src/game.py#L123-L140)), the grid is snapshotted before `ball.update()` and diffed after so that tile removals triggered inside `Ball` can be credited back to the correct player.

Scoring/goal detection lives in `Game.update`, not in `Ball`: the ball's horizontal wall-bounce is suppressed (`ball.py`) when within the goal's vertical range, and `Game.update` then reads `ball.pos` to detect that the ball crossed `x<=0.1` or `x>=grid_size[0]-0.1` inside the goal band. Keep these two pieces of boundary logic consistent if you change goal mechanics.

## Ball physics ([src/ball.py](src/ball.py))

Ball position is a pair of floats in grid coordinates (not pixels). Each tick it advances by `velocity * speed_multiplier * base_speed`. Directional tiles snap `velocity` to a unit axis vector and re-center the ball on the *perpendicular* axis of the cell (so the ball doesn't drift off-axis after a turn). `SPEED_UP` adds `0.5` to `speed_multiplier` and leaves velocity alone. A tile is consumed the first tick the ball enters a *new* cell containing one, which is why directional alignment matters — an off-axis ball could skip a cell diagonally.

**Known inconsistency**: `Ball.update` hardcodes `goal_height_cells = 3` ([src/ball.py:39](src/ball.py#L39)) while `GameOptions.goal_size` defaults to 3 but is configurable via the menu (range 2–5). If goal size is changed at runtime, the ball's bounce-suppression range desyncs from the scoring range in `Game.update`. Fix by threading `options.goal_size` into `Ball`.

## TileBank delay mechanic ([src/tile_bank.py](src/tile_bank.py))

The `tile_limit` is a *soft* rate limiter, not a hard cap: the first `tile_limit` tiles a player has on the board replenish the used slot instantly (timer = 0); once `tiles_on_board >= tile_limit`, further placements make the used slot wait `replenish_time` seconds. `tiles_on_board` is decremented by `Game.update` via `remove_tile_from_board()` when the ball consumes a tile. Players can still place beyond the limit — they just can't spam tiles faster than the replenish delay.

## Where controls live

Keybindings are stored in `GameOptions.p1_controls` / `p2_controls` as `pygame.K_*` constants and read in `Game.handle_input`. The options menu does *not* expose rebinding — to change keys, edit `game_options.py`. Defaults: P1 = WASD + 1/2/3, P2 = arrows + I/O/P.

## Supporting docs

`PROJECT_OVERVIEW.md` is the original spec. `README.md` lists controls and configurable options. `AI_CONTEXT.md` and `.aider.chat.history.md` are leftover from an earlier aider session — they're historical, not authoritative.
