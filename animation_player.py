import arcade

UPDATES_PER_FRAME = 5

class AnimationPlayer:
    def __init__(self):
        self.cur_texture = 0
        self.finished = False

    def reset(self):
        self.cur_texture = 0
        self.finished = False

    def update_animation(self, texture_list, one_shot=False) -> arcade.Texture:
        # Assume this function is called in the on_update() method and updates every frame
        if one_shot:
            frame = min(self.cur_texture // UPDATES_PER_FRAME, len(texture_list) - 1)
            self.cur_texture = min(self.cur_texture + 1, len(texture_list) * UPDATES_PER_FRAME)
            self.finished = self.cur_texture >= len(texture_list) * UPDATES_PER_FRAME
            return texture_list[frame]

        self.finished = False
        self.cur_texture += 1
        frame = (self.cur_texture // UPDATES_PER_FRAME) % len(texture_list)
        texture = texture_list[frame]

        return texture
