import arcade
from dataclasses import dataclass
from pathlib import Path
from arcade.gui import UIManager

from button_theme import RoundedButton as UIFlatButton, button_style

@dataclass
class ShopData:
    button: str = ""
    level_label: str = ""
    cost_label: str = ""

class ShopButtonUi(arcade.Sprite):
    MIN_LABEL_WIDTH = 64

    def __init__(self, button_name="Inventory Size", level="Level 0/2", gold="500 gold", text_color=arcade.color.WHITE):
        super().__init__()

        self.shop_button = ShopData()

        self.separator_color = text_color
        arcade.load_font(Path(__file__).resolve().parent / "assets/font/m5x7.ttf")

        # Create the button for the shop item
        self.button_manager = UIManager()
        minimum_button_text = arcade.Text(
            text="Inventory Size", x=0, y=0, font_name="m5x7", font_size=12,
        )
        button_width = max(120, minimum_button_text.content_width + 16)

        self.option_button = self.button_manager.add(UIFlatButton(
            text=self.shop_button.button, multiline=False,
            width=button_width, height=24, style=button_style,
        ))

        self.level_label = arcade.Text(
            text=self.shop_button.level_label,
            x=self.right,
            y=self.bottom,
            font_name="m5x7",
            font_size=12,
            color=text_color,
            anchor_x="left",
            anchor_y="center",
        )

        self.cost_label = arcade.Text(
            text=self.shop_button.cost_label,
            x=self.right,
            y=self.bottom,
            font_name="m5x7",
            font_size=12,
            color=text_color,
            anchor_x="left",
            anchor_y="center",
        )

        self.setup(button_name, level, gold)

    def setup(self, display_name: str, level: str, cost: str) -> None:
        """Set the row data and refresh its button and labels."""
        self.shop_button.button = display_name
        self.shop_button.level_label = level
        self.shop_button.cost_label = cost

        self.option_button.text = display_name
        self.level_label.text = level
        self.cost_label.text = cost

    @property
    def label_width(self):
        """Reserve equal space for level and gold, including the MAX labels."""
        return max(
            self.MIN_LABEL_WIDTH,
            self.level_label.content_width,
            self.cost_label.content_width,
        )

    @property
    def row_width(self):
        return (
            self.option_button.width
            + 2 * self.label_width
            + 16  # Two 8-pixel gaps between fields.
        )

    def draw(self):
        self.option_button.left = self.center_x - self.row_width / 2
        self.option_button.bottom = self.center_y - self.option_button.height / 2
        self.button_manager.draw()

        self.level_label.x = self.option_button.right + 8
        self.level_label.y = self.center_y
        self.level_label.draw()

        level_right = self.level_label.x + self.label_width
        self.cost_label.x = level_right + 8
        self.cost_label.y = self.center_y
        self.cost_label.draw()

        for separator_x in (self.option_button.right + 4, level_right + 4):
            arcade.draw_line(
                separator_x, self.center_y - 4,
                separator_x, self.center_y + 4,
                self.separator_color, 1,
            )
