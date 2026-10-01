"""Game-over screen with a fresh-game restart."""

from pathlib import Path

import arcade
from arcade.gui import UIManager

from button_theme import RoundedButton as UIFlatButton, button_style


class DeathView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK
        arcade.load_font(Path(__file__).resolve().parent / "assets/font/m5x7.ttf")
        self.camera = arcade.Camera2D()
        self.manager = UIManager()
        self.manager.camera = self.camera
        self.message = arcade.Text(
            "You Died!", 0, 0, arcade.color.WHITE,
            font_size=32, font_name="m5x7",
            anchor_x="center", anchor_y="center",
        )
        self.restart_button = self.manager.add(UIFlatButton(
            text="Restart", width=100, height=32, style=button_style,
        ))
        self.restart_button.push_handlers(on_click=self._restart)
        self._resize()

    def _resize(self):
        height = 300
        width = height * self.window.width / max(1, self.window.height)
        self.camera.match_window()
        self.camera.projection = arcade.LRBT(-width / 2, width / 2, -height / 2, height / 2)
        self.camera.position = (width / 2, height / 2)
        self.message.x = width / 2
        self.message.y = height / 2 + 30
        self.restart_button.left = (width - self.restart_button.width) / 2
        self.restart_button.bottom = height / 2 - 40

    def on_show_view(self):
        self.manager.enable()
        self._resize()

    def on_hide_view(self):
        self.manager.disable()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self._resize()

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.message.draw()
        self.manager.draw()

    def _restart(self, event=None):
        from game import GameView

        self.window.show_view(GameView())
