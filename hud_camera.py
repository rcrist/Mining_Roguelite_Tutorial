import arcade
from pathlib import Path

from inventory_ui import InventoryUi

DEFAULT_FONT = "m5x7"
VIEW_WIDTH = 320
VIEW_HEIGHT = 180
PANEL_WIDTH = 80
PANEL_HEIGHT = 14
PANEL_COLOR = (146, 99, 42)

class HudCamera(arcade.Camera2D):
    def __init__(self, oxygen_system):
        super().__init__(
            projection=arcade.LRBT(
                -VIEW_WIDTH / 2, VIEW_WIDTH / 2,
                -VIEW_HEIGHT / 2, VIEW_HEIGHT / 2,
            ),
            position=(VIEW_WIDTH / 2, VIEW_HEIGHT / 2),
        )
        arcade.load_font(Path(__file__).resolve().parent / "assets" / "font" / "m5x7.ttf")
        self.oxygen_system = oxygen_system
        self.OxygenText = arcade.Text(
            text=f"Oxygen: {self.oxygen_system.oxygen}",
            x=PANEL_WIDTH / 2,
            y=VIEW_HEIGHT - PANEL_HEIGHT / 2,
            color=arcade.color.BLACK,
            font_name=DEFAULT_FONT,
            font_size=12,
            anchor_x="center",
            anchor_y="center",
        )
        self.DepthText = arcade.Text(
            text="Depth: 1",
            x=VIEW_WIDTH / 2,
            color = arcade.color.BLACK,
            y=PANEL_HEIGHT / 2,
            font_name=DEFAULT_FONT,
            font_size=12,
            anchor_x="center",
            anchor_y="center",
        )
        self.inventory_ui = InventoryUi(center_x=VIEW_WIDTH / 2, top=VIEW_HEIGHT)
        self.inventory_visible = False
        self.resize()

    def resize(self):
        self.match_window(projection=False)

    def toggle_inventory(self):
        self.inventory_visible = not self.inventory_visible

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.TAB:
            self.toggle_inventory()
            return True
        return False

    def draw(self):
        self.use()
        self.OxygenText.text = f"Oxygen: {self.oxygen_system.oxygen}"
        if self.oxygen_system.oxygen <= 25:
            oxygen_color = arcade.color.RED
        elif self.oxygen_system.oxygen <= 50:
            oxygen_color = arcade.color.DARK_ORANGE
        else:
            oxygen_color = arcade.color.TEAL
        arcade.draw_rect_filled(
            arcade.XYWH(self.OxygenText.x, self.OxygenText.y, PANEL_WIDTH, PANEL_HEIGHT),
            oxygen_color,
        )
        self.OxygenText.draw()
        arcade.draw_rect_filled(
            arcade.XYWH(self.DepthText.x, PANEL_HEIGHT / 2, PANEL_WIDTH, PANEL_HEIGHT),
            PANEL_COLOR,
        )
        self.DepthText.draw()
        if self.inventory_visible:
            self.inventory_ui.draw()
