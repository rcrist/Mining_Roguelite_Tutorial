"""Run this file to preview the summary row. Press Escape to close."""

import arcade

from summary_row_ui import SummaryRow


class SummaryRowPreview(arcade.Window):
    def __init__(self, visible=True):
        super().__init__(640, 360, "Summary Row Preview", visible=visible)
        self.background_color = (245, 245, 248)
        self.camera = arcade.Camera2D(
            projection=arcade.LRBT(-160, 160, -90, 90),
            position=(160, 90),
        )
        self.row = SummaryRow(color=(40, 40, 48))
        self.row.x = (320 - self.row.width) / 2
        self.row.y = (180 - self.row.height) / 2

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.row.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.close()


if __name__ == "__main__":
    SummaryRowPreview()
    arcade.run()
