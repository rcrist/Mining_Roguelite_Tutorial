"""Inventory summary shown when leaving the mine."""

import arcade

from summary_ui import SummaryUi
from shop_view import ShopView

class SummaryView(arcade.View):
    def __init__(self, game_view, inventory=None):
        super().__init__()
        self.game_view = game_view
        self.background_color = arcade.color.BLACK
        self.camera = arcade.Camera2D()
        self.summary_ui = SummaryUi(
            inventory=game_view.player.inventory if inventory is None else inventory
        )
        self.summary_ui.button_manager.camera = self.camera
        self.summary_ui.mines_button.push_handlers(on_click=self._return_to_mines)
        self.summary_ui.shop_button.push_handlers(on_click=self._open_shop)
        self._resize_summary()

    def _resize_summary(self):
        height = 300
        width = height * self.window.width / max(1, self.window.height)
        self.camera.match_window()
        self.camera.projection = arcade.LRBT(-width / 2, width / 2, -height / 2, height / 2)
        self.camera.position = (width / 2, height / 2)
        self.summary_ui.x = (width - self.summary_ui.width) / 2
        self.summary_ui.y = (height - self.summary_ui.height) / 2

    def on_show_view(self):
        self.summary_ui.button_manager.enable()
        self._resize_summary()

    def on_hide_view(self):
        self.summary_ui.button_manager.disable()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self._resize_summary()

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.summary_ui.draw()

    def _return_to_mines(self, event=None):
        self.window.show_view(self.game_view)

    def _open_shop(self, event=None):
        if self.game_view.shop_view is None:
            self.game_view.shop_view = ShopView(self.game_view)
        self.window.show_view(self.game_view.shop_view)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self._return_to_mines()
