# Tile Strategy Game - Project Structure

I've organized the multiplayer Pygame game into the following files:

```
tile_game/
├── main.py            # Entry point for the game
├── game_options.py    # Configuration options class
├── colors.py          # Color constants
├── tile_type.py       # Enum for different types of tiles
├── tile_bank.py       # Manages player's bank of tiles
├── player.py          # Player class for cursor movement and scoring
├── ball.py            # Ball movement and physics
└── game.py            # Main game class that ties everything together
```

## How to Run

1. Make sure you have Python and Pygame installed:
   ```
   pip install pygame
   ```

2. Download and extract all files to a directory

3. Run the game:
   ```
   python main.py
   ```

## Controls

- **Player 1**:
  - WASD to move cursor
  - 1, 2, 3 keys to place tiles from respective slots

- **Player 2**:
  - Arrow keys to move cursor
  - I, O, P keys to place tiles from respective slots

- Press R to restart when game is over

## Configuration

You can modify game parameters in the `game_options.py` file:
- Grid size
- Cell size
- Goal size
- Tile bank size
- Tile replenish time
- Game duration