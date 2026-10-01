"""Shop screen opened from the mining summary."""
import arcade

from shop import ShopUi

class ShopView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.background_color = arcade.color.BLACK
        self.camera = arcade.Camera2D()
        self.shop_ui = ShopUi()
        self.shop_ui.push_handlers(
            on_upgrade_purchased=self.game_view.on_upgrade_purchased,
        )
        self.shop_ui.button_manager.camera = self.camera
        self.shop_ui.mines_button.push_handlers(on_click=self._return_to_mines)
        self._resize_shop()

    def _resize_shop(self):
        height = 300
        width = height * self.window.width / max(1, self.window.height)
        self.camera.match_window()
        self.camera.projection = arcade.LRBT(-width / 2, width / 2, -height / 2, height / 2)
        self.camera.position = (width / 2, height / 2)
        self.shop_ui.position = (width / 2, height / 2)

    def on_show_view(self):
        self.game_view.oxygen_system.stop()
        self.shop_ui.set_gold(self.game_view.gold)
        self.shop_ui.button_manager.enable()
        self._resize_shop()

    def on_hide_view(self):
        self.shop_ui.button_manager.disable()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self._resize_shop()

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.shop_ui.draw()

    def _return_to_mines(self, event=None):
        self.window.show_view(self.game_view)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self._return_to_mines()
