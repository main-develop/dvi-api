import time
import random
import hashlib


class UniqueIDGenerator:
    def __init__(self):
        self.seed_max = (1 << 14) - 1
        self.seed = random.getrandbits(14)
        
    def get_unique_id(self):
        current_time = time.time_ns() // 1000
        raw_data = f"{current_time}{self.seed}".encode()

        unique_id = hashlib.sha256(raw_data).hexdigest()[:16]

        self.seed = (self.seed + 1) % self.seed_max

        return unique_id
