# Multiplayer Pygame Game Specification

## Game Concept
A 2-player competitive game where each player controls a cursor on a grid to place special tiles that influence a ball's movement. The objective is to guide the ball into the opponent's goal.

## Core Mechanics
- **Grid-based gameplay**: Top-down 2D view of a grid where gameplay occurs
- **Real-time action**: Players place tiles as the ball moves across the grid
- **Tile effects**: Different tiles affect the ball in various ways
- **Scoring**: Players score when the ball enters the opponent's goal

## Player Controls
- **Player 1**:
  - Movement: WASD keys to move cursor
  - Place tiles: Keys 1, 2, 3 (corresponding to tile slots)
- **Player 2**:
  - Movement: Arrow keys to move cursor
  - Place tiles: I, O, P keys (corresponding to tile slots)

## Tile System
- **Tile Types**:
  - Direction tiles (UP, DOWN, LEFT, RIGHT) - Force the ball to move in that direction
  - Speed Up tiles - Increase the ball's velocity in its current direction
- **Tile Bank**:
  - Each player has configurable number of slots (default 3)
  - When a tile is used, the slot replenishes after a configurable time (default 3 seconds)
  - Replenished slots receive random tiles
- **Placement Rules**:
  - Tiles can only be placed on empty grid spaces
  - Tiles disappear after the ball crosses over them

## Ball Mechanics
- **Initial Movement**: Starts moving in a random vertical direction (up/down)
- **Physics**: Bounces off grid boundaries (top/bottom)

## Game Structure
- **Goals**: Located on opposite sides (left/right)
- **Match Format**: Timed rounds (default 5 minutes)

## Configurable Options
- Grid size
- Goal size
- Tile bank size
- Tile replenishment time
- Round duration

## Future Features
- Visual and audio effects
- Menu screen for configuration options
- Gamepad support for arcade cabinet implementation

## Implementation Plan
1. Create core game mechanics with Pygame
2. Implement the grid, player cursors, and basic collision detection
3. Add tile functionality and ball physics
4. Implement scoring system and time tracking
5. Add configuration options
6. Later: Add visual/audio effects and menu system