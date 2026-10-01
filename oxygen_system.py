# Player oxygen limits the time spent in the mines
class OxygenSystem:
    def __init__(self):
        self.max_oxygen = 100
        self.oxygen: int
        self.oxygen_use = 5
        self.oxygen_time = 1.0
        self.running = True

        self._reset_oxygen()

    def _reset_oxygen(self):
        self.oxygen = self.max_oxygen
        self.oxygen_timer = 0.0

    def start(self):
        self._reset_oxygen()
        self.running = True

    def stop(self):
        self.running = False
        self.oxygen_timer = 0.0

    def on_update(self, delta_time):
        if not self.running:
            return
        self.oxygen_timer += delta_time
        while self.oxygen_timer >= self.oxygen_time:
            self.oxygen_timer -= self.oxygen_time
            self.oxygen = max(0, self.oxygen - self.oxygen_use)
