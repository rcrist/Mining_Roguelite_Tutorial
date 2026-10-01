import arcade
from arcade.easing import ease_update
from resources import OreData

class Ore(arcade.Sprite):
    def __init__(self, position, data: OreData):
        super().__init__(data.texture)
        self.position = position
        self.ore_data = data
        self.move_tween = None
        self.next_move_tween = None
        self.horizontal_tween = None

    def update(self, delta_time=1 / 60, *args, **kwargs):
        if self.horizontal_tween is not None:
            done, self.center_x = ease_update(self.horizontal_tween, delta_time)
            if done:
                self.horizontal_tween = None
        if self.move_tween is not None:
            done, self.center_y = ease_update(self.move_tween, delta_time)
            if done:
                self.move_tween = self.next_move_tween
                self.next_move_tween = None
