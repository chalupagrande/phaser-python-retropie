# tile_bank.py
import time
import random
from tile_type import TileType


class TileBank:
    def __init__(self, size, replenish_time, tile_limit=10):
        self.size = size
        self.replenish_time = replenish_time
        self.tile_limit = tile_limit
        self.slots = [None] * size
        self.replenish_timers = [0] * size
        self.tiles_on_board = 0  # Track how many tiles are currently on the board

        # Fill bank initially
        for i in range(size):
            self.slots[i] = random.choice(list(TileType))

    def use_tile(self, slot_index):
        if slot_index < 0 or slot_index >= self.size:
            return None

        if self.slots[slot_index] is not None:
            tile = self.slots[slot_index]
            self.slots[slot_index] = None
            
            # Increment the tiles on board counter
            self.tiles_on_board += 1
            
            # If we're under the tile limit, replenish immediately
            if self.tiles_on_board < self.tile_limit:
                self.replenish_timers[slot_index] = 0
            else:
                # Otherwise use the delay
                self.replenish_timers[slot_index] = time.time() + self.replenish_time
                
            return tile
        return None

    def update(self):
        current_time = time.time()
        for i in range(self.size):
            if self.slots[i] is None and current_time >= self.replenish_timers[i]:
                self.slots[i] = random.choice(list(TileType))
                
    def reset(self):
        """Reset the tile bank for a new game"""
        self.tiles_on_board = 0
        self.replenish_timers = [0] * self.size
        for i in range(self.size):
            self.slots[i] = random.choice(list(TileType))
            
    def remove_tile_from_board(self):
        """Called when a tile is removed from the board (e.g., when ball hits it)"""
        if self.tiles_on_board > 0:
            self.tiles_on_board -= 1
