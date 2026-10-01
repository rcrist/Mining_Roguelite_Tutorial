"""Preview inventory slots. Press Space to add Iron; Escape to close."""

import arcade

from inventory_ui import InventoryUi
from inventory import Inventory
from inventory_slot_ui import InventorySlotUi
from resources import OreData


class InventoryUiPreview(arcade.Window):
    def __init__(self, visible=True):
        super().__init__(640, 360, "Inventory UI Preview", visible=visible)
        self.background_color = (40, 40, 48)
        self.camera = arcade.Camera2D(
            projection=arcade.LRBT(-160, 160, -90, 90),
            position=(160, 90),
        )
        self.inventory = Inventory(4)
        self.iron = OreData(texture=InventorySlotUi().item_icon, name="iron_ore")
        self.inventory_ui = InventoryUi(self.inventory, center_x=160, y=82)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.inventory_ui.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.SPACE:
            self.inventory.add_item(self.iron)
        if symbol == arcade.key.ESCAPE:
            self.close()


if __name__ == "__main__":
    InventoryUiPreview()
    arcade.run()
