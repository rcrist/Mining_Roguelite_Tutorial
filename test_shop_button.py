"""Run this file to preview the shop button. Press Escape to close."""
import arcade

from shop_button import ShopButtonUi

class ShopButtonPreview(arcade.Window):
    def __init__(self, visible=True):
        super().__init__(640, 360, "Shop Button Preview", visible=visible)
        self.background_color = (245, 245, 250)
        self.camera = arcade.Camera2D(
            projection=arcade.LRBT(-160, 160, -90, 90),
            position=(160, 90),
        )
        self.slot = ShopButtonUi(text_color=(40, 40, 48))
        self.slot.position = (160, 90)
        self.slot.button_manager.camera = self.camera

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.slot.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.close()

if __name__ == "__main__":
    ShopButtonPreview()
    arcade.run()
