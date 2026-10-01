import arcade
from pathlib import Path

from summary_row_ui import SummaryRow
from button_theme import RoundedButton as UIFlatButton, button_style
from arcade.gui import NinePatchTexture, UIManager

class SummaryUi:
    def __init__(self, x=0, y=0, width=280, height=240, inventory=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.inventory = inventory
        self.rows = []
        self.row_spacing = 2
        self.top_padding = 12
        arcade.load_font(Path(__file__).resolve().parent / "assets/font/m5x7.ttf")
        self.total_label = arcade.Text(
            text="Total: 0", x=0, y=0,
            font_name="m5x7", font_size=12,
            color=(40, 40, 48), anchor_x="right", anchor_y="center",
        )
        self.button_manager = UIManager()
        self.shop_button = self.button_manager.add(UIFlatButton(
            text="Go To\nThe Shop", multiline=True,
            width=100, height=32, style=button_style,
        ))
        self.mines_button = self.button_manager.add(UIFlatButton(
            text="Back To\nThe Mines", multiline=True,
            width=100, height=32, style=button_style,
        ))
        for button in (self.shop_button, self.mines_button):
            button.ui_label._label.align = "center"
            button.ui_label.with_padding(all=5)
            button.ui_label.fit_content()
            button.width = max(button.width, button.ui_label.width)
            button.height = max(button.height, button.ui_label.height)
        # In __init__: borders measured in source-image pixels.
        self.panel = NinePatchTexture(
            left=10, right=10, bottom=10, top=10,
            texture=arcade.load_texture(
                Path(__file__).resolve().parent / "assets/ui/DialogueBoxSimple.png"
            ),
        )

    def update(self):
        slots = [] if self.inventory is None else [
            slot for slot in self.inventory.slots
            if slot is not None and slot.quantity > 0
        ]
        while len(self.rows) < len(slots):
            row = SummaryRow(color=(40, 40, 48))
            row.height = 16
            self.rows.append(row)
        del self.rows[len(slots):]
        for row, slot in zip(self.rows, slots):
            row.set_item(slot)
        # Keep all columns aligned, including totals with more than three digits.
        if self.rows:
            widths = [max(row.labels[i].content_width for row in self.rows)
                      for i in range(3)]
            for row in self.rows:
                row.minimum_widths = [max(a, b) for a, b in zip(row.minimum_widths, widths)]
                row._layout_columns()
        self.total = sum(row.total for row in self.rows)
        text = f"Total: {self.total}"
        if self.total_label.text != text:
            self.total_label.text = text

    def draw(self):
        self.update()
        self.panel.draw_rect(
            rect=arcade.LBWH(self.x, self.y, self.width, self.height),
            pixelated=True,
        )
        next_top = self.y + self.height - self.top_padding
        for row in self.rows:
            row.x = self.x + (self.width - row.width) / 2
            row.y = next_top - row.height
            row.draw()
            next_top = row.y - self.row_spacing
        total_width = self.rows[-1].width if self.rows else self.width - 40
        arcade.draw_rect_filled(
            arcade.LBWH(
                self.x + (self.width - total_width) / 2,
                next_top - 16, total_width, 16,
            ),
            color=(215, 139, 0),  # #D78B00
        )
        self.total_label.x = self.x + (self.width + total_width) / 2 - 8
        self.total_label.y = next_top - 8
        self.total_label.draw()
        button_gap = 12
        buttons_width = self.shop_button.width + button_gap + self.mines_button.width
        self.shop_button.left = self.x + (self.width - buttons_width) / 2
        self.shop_button.bottom = self.y + 12
        self.mines_button.left = self.shop_button.right + button_gap
        self.mines_button.bottom = self.y + 12
        self.button_manager.draw()
