"""Run this file to preview the summary UI. Press Escape to close."""

import arcade
from pathlib import Path

from summary_ui import SummaryUi
from inventory import Inventory
from inventory_slot import InventorySlot
from resources import OreData, ROCK_TYPES

PREVIEW_WIDTH = 400
PREVIEW_HEIGHT = 300

class SummaryUiPreview(arcade.Window):
    def __init__(self, visible=True, inventory=None):
        super().__init__(800, 600, "Summary UI Preview", visible=visible)
        self.background_color = (0, 0, 0)
        self.camera = arcade.Camera2D(
            projection=arcade.LRBT(
                -PREVIEW_WIDTH / 2, PREVIEW_WIDTH / 2,
                -PREVIEW_HEIGHT / 2, PREVIEW_HEIGHT / 2,
            ),
            position=(PREVIEW_WIDTH / 2, PREVIEW_HEIGHT / 2),
        )
        # A standalone preview uses sample inventory; callers can pass a live one.
        self.inventory = inventory if inventory is not None else Inventory(4)
        if inventory is None:
            for index, (name, quantity) in enumerate((
                ("Iron", 5), ("Gold", 3), ("Silver", 2), ("Diamond", 5),
            )):
                definition = ROCK_TYPES[name]
                sheet = arcade.load_spritesheet(
                    Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems"
                    / definition.filename
                )
                texture = sheet.get_texture_grid(size=(16, 16), columns=3, count=12)[0]
                self.inventory.slots[index] = InventorySlot(
                    OreData(texture=texture, name=f"{name.lower()}_ore",
                            value=definition.ore_value), quantity,
                )
        self.summary_ui = SummaryUi(inventory=self.inventory)
        self.summary_ui.x = (PREVIEW_WIDTH - self.summary_ui.width) / 2
        self.summary_ui.y = (PREVIEW_HEIGHT - self.summary_ui.height) / 2
        self.summary_ui.button_manager.camera = self.camera
        self.summary_ui.button_manager.enable()

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.summary_ui.draw()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        if hasattr(self, "camera"):
            # UIManager resizes the shared camera to window pixels first.
            # Restore the preview's logical canvas and scale.
            self.camera.match_window()
            self.camera.projection = arcade.LRBT(
                -PREVIEW_WIDTH / 2, PREVIEW_WIDTH / 2,
                -PREVIEW_HEIGHT / 2, PREVIEW_HEIGHT / 2,
            )
            self.camera.position = (PREVIEW_WIDTH / 2, PREVIEW_HEIGHT / 2)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.close()

    def close(self):
        self.summary_ui.button_manager.disable()
        super().close()

if __name__ == "__main__":
    SummaryUiPreview()
    arcade.run()
