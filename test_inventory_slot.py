"""Run this file to preview the inventory slot. Press Escape to close."""
import arcade

from inventory_slot_ui import InventorySlotUi

class InventorySlotPreview(arcade.Window):
    def __init__(self, visible=True):
        super().__init__(640, 360, "Inventory Slot Preview", visible=visible)
        self.background_color = (40, 40, 48)
        self.camera = arcade.Camera2D(
            projection=arcade.LRBT(-160, 160, -90, 90),
            position=(160, 90),
        )
        self.slot = InventorySlotUi()
        self.slot.position = (160, 90)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.slot.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.close()

if __name__ == "__main__":
    InventorySlotPreview()
    arcade.run()
