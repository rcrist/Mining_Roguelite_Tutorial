import arcade
from pathlib import Path
from PIL import Image

from resources import ROCK_TYPES

class SummaryRow:
    def __init__(self, x=0, y=0, color=arcade.color.WHITE):
        self.x = x
        self.y = y
        self.separator_color = color
        self.height = 32
        self.ore_sprite = arcade.Sprite()

        # Create the ore image
        iron = ROCK_TYPES["Iron"]
        iron_sheet = arcade.load_spritesheet(
            Path(__file__).resolve().parent
            / "assets/mine_tiles/Ore n Gems"
            / iron.filename
        )
        iron_frames = iron_sheet.get_texture_grid(size=(16, 16), columns=3, count=12)
        self.ore_sprite.texture = iron_frames[iron.rock_frame]


        arcade.load_font(Path(__file__).resolve().parent / "assets/font/m5x7.ttf")
        self.quantity_label = arcade.Text(
            text="QTY: 5", x=0, y=0, font_name="m5x7", font_size=12,
            color=color, anchor_y="center",
        )
        self.value_label = arcade.Text(
            text="Value: 10", x=0, y=0, font_name="m5x7", font_size=12,
            color=color, anchor_y="center",
        )
        self.total_label = arcade.Text(
            text="Total: 50", x=0, y=0, font_name="m5x7", font_size=12,
            color=color, anchor_y="center",
        )
        self.labels = (self.quantity_label, self.value_label, self.total_label)
        self.minimum_widths = []
        for label, sample in zip(self.labels, ("QTY: 99", "Value: 999", "Total: 999")):
            original_text = label.text
            label.text = sample
            self.minimum_widths.append(label.content_width)
            label.text = original_text
        self._layout_columns()

    def set_item(self, slot):
        self.ore_sprite.texture = slot.ore_data.texture
        self.total = slot.quantity * slot.ore_data.value
        for label, text in zip(self.labels, (
            f"QTY: {slot.quantity}",
            f"Value: {slot.ore_data.value}",
            f"Total: {self.total}",
        )):
            if label.text != text:
                label.text = text
        self._layout_columns()

    def _layout_columns(self):
        self.separator_offsets = []
        self.label_offsets = []
        next_separator = 32
        for label, minimum_width in zip(self.labels, self.minimum_widths):
            self.separator_offsets.append(next_separator)
            self.label_offsets.append(next_separator + 8)
            next_separator += 16 + max(minimum_width, label.content_width)
        self.width = next_separator

    def draw(self):
        """Draw the row with x and y as its bottom-left corner."""
        self._layout_columns()
        center_y = self.y + self.height / 2
        self.ore_sprite.position = (self.x + 16, center_y)
        arcade.draw_sprite(self.ore_sprite, pixelated=True)
        for offset in self.separator_offsets:
            arcade.draw_line(
                self.x + offset, center_y + 4,
                self.x + offset, center_y - 4,
                self.separator_color, 1,
            )
        for label, offset in zip(self.labels, self.label_offsets):
            label.x = self.x + offset
            label.y = center_y
            label.draw()

