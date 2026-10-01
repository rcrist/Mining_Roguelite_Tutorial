import arcade

VIEW_WIDTH = 320
VIEW_HEIGHT = 180


class GameCamera(arcade.Camera2D):
    def __init__(self):
        super().__init__(
            projection=arcade.LRBT(
                -VIEW_WIDTH / 2, VIEW_WIDTH / 2,
                -VIEW_HEIGHT / 2, VIEW_HEIGHT / 2,
            ),
            position=(VIEW_WIDTH / 2, VIEW_HEIGHT / 2),
        )

    def resize(self):
        self.match_window(projection=False)

    def follow(self, player, level):
        # Stop scrolling when the edge of the view reaches the map boundary.
        half_width = VIEW_WIDTH / 2
        half_height = VIEW_HEIGHT / 2
        x = max(half_width, min(player.center_x, level.width - half_width))
        y = max(half_height, min(player.center_y, level.height - half_height))
        if level.width < VIEW_WIDTH:
            x = level.width / 2
        if level.height < VIEW_HEIGHT:
            y = level.height / 2
        self.position = (x, y)
