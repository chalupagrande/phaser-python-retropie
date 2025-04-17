# tile_bank.py
import time
import random
from tile_type import TileType


class TileBank:
    def __init__(self, size, replenish_time):
        self.size = size
        self.replenish_time = replenish_time
        self.slots = [None] * size
        self.replenish_timers = [0] * size

        # Fill bank initially
        for i in range(size):
            self.slots[i] = random.choice(list(TileType))

    def use_tile(self, slot_index):
        if slot_index < 0 or slot_index >= self.size:
            return None

        if self.slots[slot_index] is not None:
            tile = self.slots[slot_index]
            self.slots[slot_index] = None
            self.replenish_timers[slot_index] = time.time() + self.replenish_time
            return tile
        return None

    def update(self):
        current_time = time.time()
        for i in range(self.size):
            if self.slots[i] is None and current_time >= self.replenish_timers[i]:
                self.slots[i] = random.choice(list(TileType))
