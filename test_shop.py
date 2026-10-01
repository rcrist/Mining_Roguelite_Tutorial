"""Run this file to preview the current ShopUi. Press Escape to close."""
import arcade

from shop import ShopUi

class ShopPreview(arcade.Window):
    def __init__(self, visible=True):
        super().__init__(800, 600, "Shop Preview", visible=visible, resizable=True)
        self.background_color = (0, 0, 0)
        self.camera = arcade.Camera2D()
        self.shop = ShopUi(text_color=(40, 40, 48))
        self.shop.button_manager.camera = self.camera
        self.shop.button_manager.enable()
        self.shop.set_gold(10000)  # Set initial gold for testing
        self._fit_shop()

    def _fit_shop(self):
        aspect = self.width / max(1, self.height)
        minimum_width = max(
            button.row_width for button in self.shop.upgrade_buttons.values()
        ) + 24
        view_height = max(240, minimum_width / aspect)
        view_width = view_height * aspect
        self.camera.match_window()
        self.camera.projection = arcade.LRBT(
            -view_width / 2, view_width / 2, -view_height / 2, view_height / 2,
        )
        self.camera.position = (view_width / 2, view_height / 2)
        self.shop.position = self.camera.position
        self.shop.width = view_width
        self.shop.height = view_height

    def on_draw(self):
        # UIManager resets its camera on resize; restore the shop scale afterward.
        self._fit_shop()
        self.clear()
        self.camera.use()
        self.shop.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.close()

if __name__ == "__main__":
    ShopPreview()
    arcade.run()
