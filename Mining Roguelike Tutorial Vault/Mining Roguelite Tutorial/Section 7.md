Shop
-  [x] Shop UI
	-  [x] Wire Summary UI to Shop UI
-  [x] Shop UI Refactor
	-  [x] Rounded Button
	-  [x] Shop Button
	-  [x] Shop UI
-  [x] Dynamic Shop Info
-  [x] Apply Shop Upgrades
	-  [x] Shop Max Values
	-  [x] Upgrade Pickaxe Strength
	-  [x] Upgrade Oxygen Level
	-  [x] Upgrade Inventory Size

### Shop UI
---
Shop reference image:

![[Pasted image 20260930145840.png]]

I think we already know how to create the shop based on the inventory summary.

![[Pasted image 20260930164319.png]]

That's a fairly close facsimile to the reference image.

```python title=shop.py
import arcade
from dataclasses import replace
from pathlib import Path
from arcade.gui import NinePatchTexture, UIFlatButton,UIManager

from button_theme import button_style
from shop_slot import ShopSlot, ShopSlotUi

PICKAXE_PRICE = 200
OXYGEN_PRICE = 250
INVENTORY_PRICE = 500
SHOP_FONT_SIZE = 12  # Rasterizes to 16 pixels at the default 96 DPI.

class Shop:
    def __init__(self):
        self.gold = 0

        self.pickaxe_level = 0
        self.max_pickaxe_level = 3
        self.oxygen_tank_level = 0
        self.max_oxygen_tank_level = 3
        self.inventory_size = 0
        self.max_inventory_size = 3

    def set_gold(self, gold):
        self.gold = gold

    def increment_pickaxe_level(self):
        if self.gold >= PICKAXE_PRICE and self.pickaxe_level < self.max_pickaxe_level:
            self.pickaxe_level += 1

    def increment_oxygen_level(self):
        if self.gold >= OXYGEN_PRICE and self.oxygen_tank_level < self.max_pickaxe_level:
            self.oxygen_tank_level += 1

    def increment_inventory(self):
        if self.gold >= INVENTORY_PRICE and self.inventory_size < self.max_inventory_size:
            self.inventory_size += 1

class ShopUi:
    def __init__(self, x=0, y=0, width=280, height=240, text_color=(40, 40, 48)):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.separator_color = text_color
        self.position = (0, 0)
        arcade.load_font(Path(__file__).resolve().parent / "assets/font/m5x7.ttf")
        self.panel = NinePatchTexture(
            left=10, right=10, bottom=10, top=10,
            texture=arcade.load_texture(
                Path(__file__).resolve().parent / "assets/ui/DialogueBoxSimple.png"
            ),
        )

        # Create the total gold label
        self.gold_label = arcade.Text(
            text="Total Gold: 0", x=0, y=0,
            font_name="m5x7", font_size=SHOP_FONT_SIZE,
            color=(40, 40, 48), anchor_x="center", anchor_y="center",
        )

        # Create the 3 shop slot for pickaxe level, oxygen level, inventory size
        self.pickaxe_slot = ShopSlot("Pickaxe", "Level 0/3", "200 gold")
        self.oxygen_slot = ShopSlot("Oxygen Tank", "Level 0/3", "250 gold")
        self.inventory_slot = ShopSlot("Inventory Size", "Level 0/2", "500 gold")

        self.pickaxe_slot_ui = ShopSlotUi(
            text_color=text_color, button_name=self.pickaxe_slot.button_name,
            level=self.pickaxe_slot.level, gold=self.pickaxe_slot.gold,
        )
        self.oxygen_slot_ui = ShopSlotUi(
            text_color=text_color, button_name=self.oxygen_slot.button_name,
            level=self.oxygen_slot.level, gold=self.oxygen_slot.gold,
        )
        self.inventory_slot_ui = ShopSlotUi(
            text_color=text_color, button_name=self.inventory_slot.button_name,
            level=self.inventory_slot.level, gold=self.inventory_slot.gold,
        )

        # Create the "Back To The Mines" button
        self.button_manager = UIManager()
        self.shop_slot = ShopSlotUi(text_color=text_color)
        mines_button_style = {
            state: replace(style, font_size=SHOP_FONT_SIZE)
            for state, style in button_style.items()
        }

        self.mines_button = self.button_manager.add(UIFlatButton(
            text="Back To\nThe Mines", multiline=True,
            width=self.shop_slot.row_width, height=40, style=mines_button_style,
        ))
        self.mines_button.ui_label._label.align = "center"

    def draw(self):
        center_x, center_y = self.position
        slots = (self.pickaxe_slot_ui, self.oxygen_slot_ui, self.inventory_slot_ui)
        gap = 6
        section_gap = 18
        gold_height = self.gold_label.content_height + 8
        total_height = (
            gold_height + sum(slot.option_button.height for slot in slots)
            + self.mines_button.height + gap * (len(slots) - 1) + section_gap * 2
        )
        top = round(center_y + total_height / 2)
        self.mines_button.width = max(slot.row_width for slot in slots)
        self.mines_button.left = round(center_x - self.mines_button.width / 2)
        self.mines_button.bottom = top - total_height

        panel_width = max(self.width, self.mines_button.width + 24)
        panel_height = max(self.height, total_height + 24)
        self.panel.draw_rect(
            rect=arcade.LBWH(
                center_x - panel_width / 2, center_y - panel_height / 2,
                panel_width, panel_height,
            ),
            pixelated=True,
        )

        # Draw the total gold label
        self.gold_label.x = round(self.mines_button.left + self.mines_button.width / 2)
        self.gold_label.y = top - gold_height / 2
        arcade.draw_rect_filled(
            arcade.LBWH(
                self.mines_button.left,
                self.gold_label.y - self.gold_label.content_height / 2 - 4,
                self.mines_button.width,
                self.gold_label.content_height + 8,
            ),
            arcade.color.ORANGE,
        )
        self.gold_label.draw()

        next_top = top - gold_height - section_gap
        for slot in slots:
            slot.position = (center_x, next_top - slot.option_button.height / 2)
            slot.button_manager.camera = self.button_manager.camera
            slot.draw()
            next_top -= slot.option_button.height + gap

        # Draw the mines button
        self.button_manager.draw()

```

```python title=test_shop.py
"""Run this file to preview the current ShopUi. Press Escape to close."""
import arcade

from shop import ShopUi

class ShopPreview(arcade.Window):
    def __init__(self, visible=True):
        super().__init__(800, 600, "Shop Preview", visible=visible)
        self.background_color = (0, 0, 0)
        view_height = 300
        view_width = view_height * self.width / self.height
        self.camera = arcade.Camera2D(
            projection=arcade.LRBT(-view_width / 2, view_width / 2, -150, 150),
            position=(view_width / 2, view_height / 2),
        )
        self.shop = ShopUi(text_color=(40, 40, 48))
        self.shop.position = (view_width / 2, view_height / 2)
        self.shop.button_manager.camera = self.camera

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.shop.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.close()

if __name__ == "__main__":
    ShopPreview()
    arcade.run()

```

#### Wire Summary UI to Shop UI
---
```python title=shop_view.py
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
        self.shop_ui.gold_label.text = f"Total Gold: {self.game_view.gold}"
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

```

```python title=summary_ui.py
import arcade
from pathlib import Path

from summary_row_ui import SummaryRow
from button_theme import button_style
from arcade.gui import NinePatchTexture, UIFlatButton, UIManager

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

```

```python title=summary_view.py
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
        self.window.show_view(ShopView(self.game_view))

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self._return_to_mines()

```

### Shop UI Refactor
---
After watching more videos from the reference tutorial, I decided to refactor the shop so it matches the functionality better.

#### Rounded Button
---
![[Pasted image 20261001061751.png|1000]]

```python title=button_theme.py
"""Shared styles for UI buttons."""

import arcade
from math import cos, sin, pi
from arcade.gui import UIFlatButton

CORNER_RADIUS = 5

class RoundedButton(UIFlatButton):
    """A themed flat button with 5 px rounded corners."""

    def do_render(self, surface):
        self.prepare_render(surface)
        surface.clear()
        style = self.get_current_style()
        if style is None:
            raise ValueError(f"No style found for state {self.get_current_state()}")
        self._apply_style(style)
        width, height = self.content_width, self.content_height
        radius = min(CORNER_RADIUS, width / 2, height / 2)

        def fill(inset, color):
            if color is None or width <= 2 * inset or height <= 2 * inset:
                return
            r = max(0, radius - inset)
            points = []
            for cx, cy, start in (
                (width - inset - r, height - inset - r, 0),
                (inset + r, height - inset - r, pi / 2),
                (inset + r, inset + r, pi),
                (width - inset - r, inset + r, 3 * pi / 2),
            ):
                for step in range(9):
                    angle = start + step * pi / 16
                    points.append((cx + r * cos(angle), cy + r * sin(angle)))
            arcade.draw_polygon_filled(points, color)

        border_width = style.get("border_width", 0)
        border_color = style.get("border")
        if border_color and border_width:
            fill(0, border_color)
            fill(border_width, style.get("bg"))
        else:
            fill(0, style.get("bg"))

button_style = {
    state: UIFlatButton.UIStyle(
        font_name="m5x7", font_size=12,
        font_color=arcade.color.WHITE, bg=(56, 115, 163, 255),
        border=arcade.color.WHITE,
        border_width=1 if state in ("hover", "press") else 0,
    )
    for state in ("normal", "hover", "press", "disabled")
}

```

```python title=summary_view.py hl=5,50-51
"""Inventory summary shown when leaving the mine."""
import arcade

from summary_ui import SummaryUi
# from shop_view import ShopView

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
        # self.window.show_view(ShopView(self.game_view))
        print("Shop button clicked. Implement shop view transition here.")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self._return_to_mines()

```

#### Shop Button
---
![[Pasted image 20261001063743.png]]

```python title=shop_button.py
import arcade
from dataclasses import dataclass
from pathlib import Path
from arcade.gui import UIManager

from button_theme import RoundedButton as UIFlatButton, button_style

@dataclass
class ShopButton:
    button: str = ""
    level_label: str = ""
    cost_label: str = ""

class ShopButtonUi(arcade.Sprite):
    def __init__(self, button_name="Inventory Size", level="Level 0/2", gold="500 gold", text_color=arcade.color.WHITE):
        super().__init__()

        self.shop_button = ShopButton()

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
    def row_width(self):
        return (
            self.option_button.width
            + self.level_label.content_width
            + self.cost_label.content_width
            + 16  # Two 8-pixel gaps between fields.
        )

    def draw(self):
        self.option_button.left = self.center_x - self.row_width / 2
        self.option_button.bottom = self.center_y - self.option_button.height / 2
        self.button_manager.draw()

        self.level_label.x = self.option_button.right + 8
        self.level_label.y = self.center_y
        self.level_label.draw()

        self.cost_label.x = self.level_label.right + 8
        self.cost_label.y = self.center_y
        self.cost_label.draw()

        for separator_x in (self.option_button.right + 4, self.level_label.right + 4):
            arcade.draw_line(
                separator_x, self.center_y - 4,
                separator_x, self.center_y + 4,
                self.separator_color, 1,
            )

```

```python title=test_shop_button.py
"""Run this file to preview the shop button. Press Escape to close."""
import arcade

from shop_button import ShopButtonUi

class ShopButtonPreview(arcade.Window):
    def __init__(self, visible=True):
        super().__init__(640, 360, "Shop Button Preview", visible=visible)
        self.background_color = (245, 245, 250)
        self.camera = arcade.Camera2D(
            projection=arcade.LRBT(-160, 160, -90, 90),
            position=(160, 90),
        )
        self.slot = ShopButtonUi(text_color=(40, 40, 48))
        self.slot.position = (160, 90)
        self.slot.button_manager.camera = self.camera

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.slot.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.close()

if __name__ == "__main__":
    ShopButtonPreview()
    arcade.run()

```

#### Shop UI
---
We will now connect the shop buttons so that upgrades can be purchased if the player has enough gold.

![[Pasted image 20261001081254.png]]

```python title=shop.py
import arcade
from functools import partial
from pathlib import Path
from arcade.gui import NinePatchTexture, UIManager

from button_theme import RoundedButton, button_style
from shop_button import ShopButtonUi

class ShopUi:
    def __init__(self, x=0, y=0, width=280, height=240, text_color=(40, 40, 48)):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.gold = 0  # Total gold the player has

        self.upgrades = {
            "pickaxe": {"level": 0, "max_level": 3, "costs": [200, 500, 1500]},
            "oxygen_tank": {"level": 0, "max_level": 3, "costs": [250, 600, 2000]},
            "inventory_size": {"level": 0, "max_level": 2, "costs": [500, 2500]},
        }

        self.separator_color = text_color
        self.position = (0, 0)
        arcade.load_font(Path(__file__).resolve().parent / "assets/font/m5x7.ttf")
        self.panel = NinePatchTexture(
            left=10, right=10, bottom=10, top=10,
            texture=arcade.load_texture(
                Path(__file__).resolve().parent / "assets/ui/DialogueBoxSimple.png"
            ),
        )

        # Create the total gold label
        self.gold_label = arcade.Text(
            text="Total Gold: 0", x=0, y=0,
            font_name="m5x7", font_size=12,
            color=(40, 40, 48), anchor_x="center", anchor_y="center",
        )

        # Create the 3 shop buttons for pickaxe level, oxygen level, inventory size
        self.pickaxe_button = ShopButtonUi("Pickaxe", "Level 0/3", "200 gold")
        self.oxygen_button = ShopButtonUi("Oxygen Tank", "Level 0/3", "250 gold")
        self.inventory_button = ShopButtonUi("Inventory Size", "Level 0/2", "500 gold")

        self.pickaxe_button = ShopButtonUi(
            button_name=self.pickaxe_button.shop_button.button,
            level=self.pickaxe_button.shop_button.level_label, 
            gold=self.pickaxe_button.shop_button.cost_label,
            text_color=text_color, 
        )
        self.oxygen_button = ShopButtonUi(
            button_name=self.oxygen_button.shop_button.button,
            level=self.oxygen_button.shop_button.level_label, 
            gold=self.oxygen_button.shop_button.cost_label,
            text_color=text_color, 
        )
        self.inventory_button = ShopButtonUi(
            button_name=self.inventory_button.shop_button.button,
            level=self.inventory_button.shop_button.level_label, 
            gold=self.inventory_button.shop_button.cost_label,
            text_color=text_color,
        )

        # Create the "Back To The Mines" button
        self.button_manager = UIManager()
        self.upgrade_buttons = {
            "pickaxe": self.pickaxe_button,
            "oxygen_tank": self.oxygen_button,
            "inventory_size": self.inventory_button,
        }
        for upgrade_name, button in self.upgrade_buttons.items():
            # Use the shop manager so all buttons share input and camera handling.
            button.button_manager.remove(button.option_button)
            self.button_manager.add(button.option_button)
            button.option_button.push_handlers(
                on_click=partial(self.buy_upgrade, upgrade_name),
            )
        self.shop_slot = ShopButtonUi(text_color=text_color)

        self.mines_button = self.button_manager.add(RoundedButton(
            text="Back To\nThe Mines", multiline=True,
            width=self.shop_slot.row_width, height=40, style=button_style,
        ))
        self.mines_button.ui_label._label.align = "center"

    def buy_upgrade(self, upgrade_name: str, event=None) -> None:
        """Buy one level if affordable and show the next upgrade price."""
        upgrade = self.upgrades[upgrade_name]
        if upgrade["level"] >= upgrade["max_level"]:
            return
        cost = upgrade["costs"][upgrade["level"]]
        if self.gold < cost:
            return

        self.set_gold(self.gold - cost)
        upgrade["level"] += 1
        button = self.upgrade_buttons[upgrade_name]
        maxed = upgrade["level"] >= upgrade["max_level"]
        button.setup(
            display_name=button.shop_button.button,
            level=f"Level {upgrade['level']}/{upgrade['max_level']}",
            cost="Maxed" if maxed else f"{upgrade['costs'][upgrade['level']]} gold",
        )
        button.option_button.disabled = maxed

    def set_gold(self, total_gold: int) -> None:
        """Set the total gold label."""
        self.gold_label.text = f"Total Gold: {total_gold}"
        self.gold = total_gold

    def draw(self):
        center_x, center_y = self.position
        buttons = (self.pickaxe_button, self.oxygen_button, self.inventory_button)
        gap = 6
        section_gap = 18
        gold_height = self.gold_label.content_height + 8
        total_height = (
            gold_height + sum(button.option_button.height for button in buttons)
            + self.mines_button.height + gap * (len(buttons) - 1) + section_gap * 2
        )
        top = round(center_y + total_height / 2)
        self.mines_button.width = max(slot.row_width for slot in buttons)
        self.mines_button.left = round(center_x - self.mines_button.width / 2)
        self.mines_button.bottom = top - total_height

        panel_width = max(self.width, self.mines_button.width + 24)
        panel_height = max(self.height, total_height + 24)
        self.panel.draw_rect(
            rect=arcade.LBWH(
                center_x - panel_width / 2, center_y - panel_height / 2,
                panel_width, panel_height,
            ),
            pixelated=True,
        )

        # Draw the total gold label
        self.gold_label.x = round(self.mines_button.left + self.mines_button.width / 2)
        self.gold_label.y = top - gold_height / 2
        arcade.draw_rect_filled(
            arcade.LBWH(
                self.mines_button.left,
                self.gold_label.y - self.gold_label.content_height / 2 - 4,
                self.mines_button.width,
                self.gold_label.content_height + 8,
            ),
            arcade.color.ORANGE,
        )
        self.gold_label.draw()

        next_top = top - gold_height - section_gap
        for button in buttons:
            button.position = (center_x, next_top - button.option_button.height / 2)
            button.button_manager.camera = self.button_manager.camera
            button.draw()
            next_top -= button.option_button.height + gap

        # Draw the mines button
        self.button_manager.draw()

```

```python title=test_shop.py
"""Run this file to preview the current ShopUi. Press Escape to close."""
import arcade

from shop import ShopUi

class ShopPreview(arcade.Window):
    def __init__(self, visible=True):
        super().__init__(800, 600, "Shop Preview", visible=visible, resizable=True)
        self.background_color = (0, 0, 0)
        self.camera = arcade.Camera2D()
        self.shop = ShopUi(text_color=(40, 40, 48))
        self.shop.button_manager.camera = self.camera
        self.shop.button_manager.enable()
        self.shop.set_gold(1000)  # Set initial gold for testing
        self._fit_shop()

    def _fit_shop(self):
        aspect = self.width / max(1, self.height)
        minimum_width = max(
            button.row_width for button in self.shop.upgrade_buttons.values()
        ) + 24
        view_height = max(240, minimum_width / aspect)
        view_width = view_height * aspect
        self.camera.match_window()
        self.camera.projection = arcade.LRBT(
            -view_width / 2, view_width / 2, -view_height / 2, view_height / 2,
        )
        self.camera.position = (view_width / 2, view_height / 2)
        self.shop.position = self.camera.position
        self.shop.width = view_width
        self.shop.height = view_height

    def on_draw(self):
        # UIManager resets its camera on resize; restore the shop scale afterward.
        self._fit_shop()
        self.clear()
        self.camera.use()
        self.shop.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.close()

if __name__ == "__main__":
    ShopPreview()
    arcade.run()

```

### Dynamic Shop Info
---
We will now integrate the shop user interface with the game. In arcade, pop-up windows such as the Shop and Summary are defined as game views. So when the user clicks on the shop button > shop view > shop ui > shop buttons.

![[Pasted image 20261001082217.png|1000]]

![[Pasted image 20261001082055.png|1000]]

![[Pasted image 20261001082131.png|1000]]

```python title=game.py
import arcade

from level_manager import LevelManager
from game_camera import GameCamera
from hud_camera import HudCamera
from summary_view import SummaryView
from inventory import Inventory
from inventory_slot import InventorySlot
from oxygen_system import OxygenSystem
from death_view import DeathView

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.gold = 0
        self.death_timer = None
        self.oxygen_system = OxygenSystem()

        self.camera = GameCamera()
        self.hud_camera = HudCamera(self.oxygen_system)
        self.level_manager = LevelManager(self)
        self.level_manager.load_first_level()

    def show_summary(self):
        self.oxygen_system.stop()
        self.player.change_x = 0
        self.player.change_y = 0
        self.player.pickaxe_held = False
        inventory = self.player.inventory
        summary_inventory = Inventory(len(inventory.slots))
        summary_inventory.slots = [
            InventorySlot(slot.ore_data, slot.quantity) if slot is not None else None
            for slot in inventory.slots
        ]
        summary = SummaryView(self, inventory=summary_inventory)
        self.gold += sum(
            slot.quantity * slot.ore_data.value
            for slot in summary_inventory.slots if slot is not None
        )
        inventory.slots[:] = [None] * len(inventory.slots)
        self.window.show_view(summary)

    def spend_gold(self, amount: int) -> bool:
        """Pay a whole-number price, returning False if funds are insufficient."""
        if type(amount) is not int or amount < 0:
            raise ValueError("Gold cost must be a non-negative integer")
        if amount > self.gold:
            return False
        self.gold -= amount
        return True

    def on_show_view(self):
        self.oxygen_system.start()
        self.camera.resize()
        self.hud_camera.resize()
        self.camera.follow(self.player, self.level)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw(pixelated=True)
        # self.scene.draw_hit_boxes(
        #     color=arcade.color.YELLOW,
        #     line_thickness=1,
        # )
        if self.player.pickaxe_active:
            arcade.draw_polygon_outline(
                self.player.pickaxe_hitbox.hit_box.get_adjusted_points(),
                arcade.color.RED,
                1,
            )

        self.hud_camera.draw()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.camera.resize()
        self.hud_camera.resize()
        self.camera.follow(self.player, self.level)

    def on_update(self, delta_time):
        if self.death_timer is not None:
            self.player.on_update(delta_time)
            self.death_timer += delta_time
            if self.death_timer >= 5.0:
                self.window.show_view(DeathView())
            return
        self.oxygen_system.on_update(delta_time)
        if self.oxygen_system.oxygen <= 0:
            self.oxygen_system.stop()
            self.player.die()
            self.player.on_update(0.0)
            self.death_timer = 0.0
            return
        self.scene["Rock"].update(delta_time)
        self.scene["Ore"].update(delta_time)
        # Animated drops can overlap the player before physics moves them apart.
        overlapping_ores = arcade.check_for_collision_with_list(
            self.player, self.scene["Ore"]
        )
        for ore in overlapping_ores:
            if self.player.add_ore(ore.ore_data):
                ore.remove_from_sprite_lists()
        # The physics engine resolves movement against walls, rocks, and ore.
        collisions = self.physics_engine.update()
        self.level.constrain_player(self.player)
        for sprite in collisions:
            if sprite in self.scene["Ore"]:
                if self.player.add_ore(sprite.ore_data):
                    sprite.remove_from_sprite_lists()
        self.player.on_update(delta_time)
        self.player.hit_rocks(self.scene["Rock"])
        on_down_ladder = any(
            ladder.type == "Down"
            for ladder in arcade.check_for_collision_with_list(self.player, self.scene["Ladder"])
        )
        self.player_on_ladder = on_down_ladder
        self.camera.follow(self.player, self.level)

    def on_key_press(self, key, key_modifiers):
        if self.death_timer is not None:
            return
        if self.hud_camera.on_key_press(key, key_modifiers):
            return
        self.player.on_key_press(key, key_modifiers)
        for ladder in arcade.check_for_collision_with_list(self.player, self.scene["Ladder"]):
            if ladder.on_key_press(key, key_modifiers):
                if ladder.type == "Up":
                    self.level_manager.previous_level()
                else:
                    self.level_manager.next_level()
                return

    def on_key_release(self, key, key_modifiers):
        if self.death_timer is not None:
            return
        self.player.on_key_release(key, key_modifiers)

def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.center_window()

    game = GameView()
    window.show_view(game)
    arcade.run()  # Runs the Arcade game loop

if __name__ == "__main__":
    main()

```

```python titl=summary_view.py
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
        self.window.show_view(ShopView(self.game_view))

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self._return_to_mines()

```

```python title=shop_view.py
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

```

### Apply Shop Upgrades
---
#### Shop Max Values
---
![[Pasted image 20261001084405.png]]

```python title=shop.py
import arcade
from dataclasses import replace
from functools import partial
from pathlib import Path
from arcade.gui import NinePatchTexture, UIManager

from button_theme import RoundedButton, button_style
from shop_button import ShopButtonUi

class ShopUi:
    def __init__(self, x=0, y=0, width=280, height=240, text_color=(40, 40, 48)):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.gold = 0  # Total gold the player has

        self.upgrades = {
            "pickaxe": {"level": 0, "max_level": 3, "costs": [200, 500, 1500]},
            "oxygen_tank": {"level": 0, "max_level": 3, "costs": [250, 600, 2000]},
            "inventory_size": {"level": 0, "max_level": 2, "costs": [500, 2500]},
        }

        self.separator_color = text_color
        self.position = (0, 0)
        arcade.load_font(Path(__file__).resolve().parent / "assets/font/m5x7.ttf")
        self.panel = NinePatchTexture(
            left=10, right=10, bottom=10, top=10,
            texture=arcade.load_texture(
                Path(__file__).resolve().parent / "assets/ui/DialogueBoxSimple.png"
            ),
        )

        # Create the total gold label
        self.gold_label = arcade.Text(
            text="Total Gold: 0", x=0, y=0,
            font_name="m5x7", font_size=12,
            color=(40, 40, 48), anchor_x="center", anchor_y="center",
        )

        # Create the 3 shop buttons for pickaxe level, oxygen level, inventory size
        self.pickaxe_button = ShopButtonUi("Pickaxe", "Level 0/3", "200 gold")
        self.oxygen_button = ShopButtonUi("Oxygen Tank", "Level 0/3", "250 gold")
        self.inventory_button = ShopButtonUi("Inventory Size", "Level 0/2", "500 gold")

        self.pickaxe_button = ShopButtonUi(
            button_name=self.pickaxe_button.shop_button.button,
            level=self.pickaxe_button.shop_button.level_label, 
            gold=self.pickaxe_button.shop_button.cost_label,
            text_color=text_color, 
        )
        self.oxygen_button = ShopButtonUi(
            button_name=self.oxygen_button.shop_button.button,
            level=self.oxygen_button.shop_button.level_label, 
            gold=self.oxygen_button.shop_button.cost_label,
            text_color=text_color, 
        )
        self.inventory_button = ShopButtonUi(
            button_name=self.inventory_button.shop_button.button,
            level=self.inventory_button.shop_button.level_label, 
            gold=self.inventory_button.shop_button.cost_label,
            text_color=text_color,
        )

        # Create the "Back To The Mines" button
        self.button_manager = UIManager()
        self.upgrade_buttons = {
            "pickaxe": self.pickaxe_button,
            "oxygen_tank": self.oxygen_button,
            "inventory_size": self.inventory_button,
        }
        for upgrade_name, button in self.upgrade_buttons.items():
            button.option_button.style = {
                **button_style,
                "disabled": replace(button_style["disabled"], bg=arcade.color.GRAY),
            }
            # Use the shop manager so all buttons share input and camera handling.
            button.button_manager.remove(button.option_button)
            self.button_manager.add(button.option_button)
            button.option_button.push_handlers(
                on_click=partial(self.buy_upgrade, upgrade_name),
            )
        self.shop_slot = ShopButtonUi(text_color=text_color)

        self.mines_button = self.button_manager.add(RoundedButton(
            text="Back To\nThe Mines", multiline=True,
            width=self.shop_slot.row_width, height=40, style=button_style,
        ))
        self.mines_button.ui_label._label.align = "center"

    def buy_upgrade(self, upgrade_name: str, event=None) -> None:
        """Buy one level if affordable and show the next upgrade price."""
        upgrade = self.upgrades[upgrade_name]
        if upgrade["level"] >= upgrade["max_level"]:
            return
        cost = upgrade["costs"][upgrade["level"]]
        if self.gold < cost:
            return

        self.set_gold(self.gold - cost)
        upgrade["level"] += 1
        button = self.upgrade_buttons[upgrade_name]
        maxed = upgrade["level"] >= upgrade["max_level"]
        button.setup(
            display_name=button.shop_button.button,
            level="MAX" if maxed else f"Level {upgrade['level']}/{upgrade['max_level']}",
            cost="MAX" if maxed else f"{upgrade['costs'][upgrade['level']]} gold",
        )
        button.option_button.disabled = maxed

    def set_gold(self, total_gold: int) -> None:
        """Set the total gold label."""
        self.gold_label.text = f"Total Gold: {total_gold}"
        self.gold = total_gold

    def draw(self):
        center_x, center_y = self.position
        buttons = (self.pickaxe_button, self.oxygen_button, self.inventory_button)
        gap = 6
        section_gap = 18
        gold_height = self.gold_label.content_height + 8
        total_height = (
            gold_height + sum(button.option_button.height for button in buttons)
            + self.mines_button.height + gap * (len(buttons) - 1) + section_gap * 2
        )
        top = round(center_y + total_height / 2)
        self.mines_button.width = max(slot.row_width for slot in buttons)
        self.mines_button.left = round(center_x - self.mines_button.width / 2)
        self.mines_button.bottom = top - total_height

        panel_width = max(self.width, self.mines_button.width + 24)
        panel_height = max(self.height, total_height + 24)
        self.panel.draw_rect(
            rect=arcade.LBWH(
                center_x - panel_width / 2, center_y - panel_height / 2,
                panel_width, panel_height,
            ),
            pixelated=True,
        )

        # Draw the total gold label
        self.gold_label.x = round(self.mines_button.left + self.mines_button.width / 2)
        self.gold_label.y = top - gold_height / 2
        arcade.draw_rect_filled(
            arcade.LBWH(
                self.mines_button.left,
                self.gold_label.y - self.gold_label.content_height / 2 - 4,
                self.mines_button.width,
                self.gold_label.content_height + 8,
            ),
            arcade.color.ORANGE,
        )
        self.gold_label.draw()

        next_top = top - gold_height - section_gap
        for button in buttons:
            button.position = (center_x, next_top - button.option_button.height / 2)
            button.button_manager.camera = self.button_manager.camera
            button.draw()
            next_top -= button.option_button.height + gap

        # Draw the mines button
        self.button_manager.draw()

```

#### Upgrade Pickaxe Strength
---
Arcade is built on pyglet which has a signal system. We will use signals to notify the game than an upgrade has been purchased.

```python title=shop.py hl=6,11,113,170
import arcade
from dataclasses import replace
from functools import partial
from pathlib import Path
from arcade.gui import NinePatchTexture, UIManager
from pyglet.event import EventDispatcher

from button_theme import RoundedButton, button_style
from shop_button import ShopButtonUi

class ShopUi(EventDispatcher):
    def __init__(self, x=0, y=0, width=280, height=240, text_color=(40, 40, 48)):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.gold = 0  # Total gold the player has

        self.upgrades = {
            "pickaxe": {"level": 0, "max_level": 3, "costs": [200, 500, 1500]},
            "oxygen_tank": {"level": 0, "max_level": 3, "costs": [250, 600, 2000]},
            "inventory_size": {"level": 0, "max_level": 2, "costs": [500, 2500]},
        }

        self.separator_color = text_color
        self.position = (0, 0)
        arcade.load_font(Path(__file__).resolve().parent / "assets/font/m5x7.ttf")
        self.panel = NinePatchTexture(
            left=10, right=10, bottom=10, top=10,
            texture=arcade.load_texture(
                Path(__file__).resolve().parent / "assets/ui/DialogueBoxSimple.png"
            ),
        )

        # Create the total gold label
        self.gold_label = arcade.Text(
            text="Total Gold: 0", x=0, y=0,
            font_name="m5x7", font_size=12,
            color=(40, 40, 48), anchor_x="center", anchor_y="center",
        )

        # Create the 3 shop buttons for pickaxe level, oxygen level, inventory size
        self.pickaxe_button = ShopButtonUi("Pickaxe", "Level 0/3", "200 gold")
        self.oxygen_button = ShopButtonUi("Oxygen Tank", "Level 0/3", "250 gold")
        self.inventory_button = ShopButtonUi("Inventory Size", "Level 0/2", "500 gold")

        self.pickaxe_button = ShopButtonUi(
            button_name=self.pickaxe_button.shop_button.button,
            level=self.pickaxe_button.shop_button.level_label, 
            gold=self.pickaxe_button.shop_button.cost_label,
            text_color=text_color, 
        )
        self.oxygen_button = ShopButtonUi(
            button_name=self.oxygen_button.shop_button.button,
            level=self.oxygen_button.shop_button.level_label, 
            gold=self.oxygen_button.shop_button.cost_label,
            text_color=text_color, 
        )
        self.inventory_button = ShopButtonUi(
            button_name=self.inventory_button.shop_button.button,
            level=self.inventory_button.shop_button.level_label, 
            gold=self.inventory_button.shop_button.cost_label,
            text_color=text_color,
        )

        # Create the "Back To The Mines" button
        self.button_manager = UIManager()
        self.upgrade_buttons = {
            "pickaxe": self.pickaxe_button,
            "oxygen_tank": self.oxygen_button,
            "inventory_size": self.inventory_button,
        }
        for upgrade_name, button in self.upgrade_buttons.items():
            button.option_button.style = {
                **button_style,
                "disabled": replace(button_style["disabled"], bg=arcade.color.GRAY),
            }
            # Use the shop manager so all buttons share input and camera handling.
            button.button_manager.remove(button.option_button)
            self.button_manager.add(button.option_button)
            button.option_button.push_handlers(
                on_click=partial(self.buy_upgrade, upgrade_name),
            )
        self.shop_slot = ShopButtonUi(text_color=text_color)

        self.mines_button = self.button_manager.add(RoundedButton(
            text="Back To\nThe Mines", multiline=True,
            width=self.shop_slot.row_width, height=40, style=button_style,
        ))
        self.mines_button.ui_label._label.align = "center"

    def buy_upgrade(self, upgrade_name: str, event=None) -> None:
        """Buy one level if affordable and show the next upgrade price."""
        upgrade = self.upgrades[upgrade_name]
        if upgrade["level"] >= upgrade["max_level"]:
            return
        cost = upgrade["costs"][upgrade["level"]]
        if self.gold < cost:
            return

        self.set_gold(self.gold - cost)
        upgrade["level"] += 1
        button = self.upgrade_buttons[upgrade_name]
        maxed = upgrade["level"] >= upgrade["max_level"]
        button.setup(
            display_name=button.shop_button.button,
            level="MAX" if maxed else f"Level {upgrade['level']}/{upgrade['max_level']}",
            cost="MAX" if maxed else f"{upgrade['costs'][upgrade['level']]} gold",
        )
        button.option_button.disabled = maxed
        self.dispatch_event("on_upgrade_purchased", upgrade_name, self.gold)

    def set_gold(self, total_gold: int) -> None:
        """Set the total gold label."""
        self.gold_label.text = f"Total Gold: {total_gold}"
        self.gold = total_gold

    def draw(self):
        center_x, center_y = self.position
        buttons = (self.pickaxe_button, self.oxygen_button, self.inventory_button)
        gap = 6
        section_gap = 18
        gold_height = self.gold_label.content_height + 8
        total_height = (
            gold_height + sum(button.option_button.height for button in buttons)
            + self.mines_button.height + gap * (len(buttons) - 1) + section_gap * 2
        )
        top = round(center_y + total_height / 2)
        self.mines_button.width = max(slot.row_width for slot in buttons)
        self.mines_button.left = round(center_x - self.mines_button.width / 2)
        self.mines_button.bottom = top - total_height

        panel_width = max(self.width, self.mines_button.width + 24)
        panel_height = max(self.height, total_height + 24)
        self.panel.draw_rect(
            rect=arcade.LBWH(
                center_x - panel_width / 2, center_y - panel_height / 2,
                panel_width, panel_height,
            ),
            pixelated=True,
        )

        # Draw the total gold label
        self.gold_label.x = round(self.mines_button.left + self.mines_button.width / 2)
        self.gold_label.y = top - gold_height / 2
        arcade.draw_rect_filled(
            arcade.LBWH(
                self.mines_button.left,
                self.gold_label.y - self.gold_label.content_height / 2 - 4,
                self.mines_button.width,
                self.gold_label.content_height + 8,
            ),
            arcade.color.ORANGE,
        )
        self.gold_label.draw()

        next_top = top - gold_height - section_gap
        for button in buttons:
            button.position = (center_x, next_top - button.option_button.height / 2)
            button.button_manager.camera = self.button_manager.camera
            button.draw()
            next_top -= button.option_button.height + gap

        # Draw the mines button
        self.button_manager.draw()


ShopUi.register_event_type("on_upgrade_purchased")

```

Woohoo! We have signals, so the shop is decoupled from the game.

```python title=game.py hl=20,48-52
import arcade

from level_manager import LevelManager
from game_camera import GameCamera
from hud_camera import HudCamera
from summary_view import SummaryView
from inventory import Inventory
from inventory_slot import InventorySlot
from oxygen_system import OxygenSystem
from death_view import DeathView

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.gold = 0
        self.shop_view = None
        self.death_timer = None
        self.oxygen_system = OxygenSystem()

        self.camera = GameCamera()
        self.hud_camera = HudCamera(self.oxygen_system)
        self.level_manager = LevelManager(self)
        self.level_manager.load_first_level()

    def show_summary(self):
        self.oxygen_system.stop()
        self.player.change_x = 0
        self.player.change_y = 0
        self.player.pickaxe_held = False
        inventory = self.player.inventory
        summary_inventory = Inventory(len(inventory.slots))
        summary_inventory.slots = [
            InventorySlot(slot.ore_data, slot.quantity) if slot is not None else None
            for slot in inventory.slots
        ]
        summary = SummaryView(self, inventory=summary_inventory)
        self.gold += sum(
            slot.quantity * slot.ore_data.value
            for slot in summary_inventory.slots if slot is not None
        )
        inventory.slots[:] = [None] * len(inventory.slots)
        self.window.show_view(summary)

    def on_upgrade_purchased(self, upgrade_name: str, remaining_gold: int) -> None:
        """Apply successful shop purchases to the current game."""
        self.gold = remaining_gold
        if upgrade_name == "pickaxe":
            self.player.pickaxe_strength += 1

    def spend_gold(self, amount: int) -> bool:
        """Pay a whole-number price, returning False if funds are insufficient."""
        if type(amount) is not int or amount < 0:
            raise ValueError("Gold cost must be a non-negative integer")
        if amount > self.gold:
            return False
        self.gold -= amount
        return True

...
```

Level manager handles player pickaxe strength.
```python title=level_manager.py hl=8
...

        player = level.spawn_player(scene)
        previous_player = getattr(self.game_view, "player", None)
        if preserve_inventory and previous_player is not None:
            # Keep the same inventory when replacing the player for a new map.
            player.inventory = previous_player.inventory
            player.pickaxe_strength = previous_player.pickaxe_strength
        level.constrain_player(player)
        physics_engine = arcade.PhysicsEngineSimple(
            player,
            [scene["Collision_Walls"], scene["Rock"], scene["Ore"]],
        )

...
```

Now increase player damage to rocks based on pickaxe strength.
```python title=player.py hl=8
...

    def hit_rocks(self, rocks):
        if not self.pickaxe_active:
            return
        for rock in arcade.check_for_collision_with_list(self.pickaxe_hitbox, rocks):
            if rock not in self.rocks_hit_this_swing:
                rock.take_damage(self.pickaxe_strength)
                self.rocks_hit_this_swing.add(rock)
                
...
```

The shop view pushes the handler for the upgrade purchased signal.
```python title=shop_view.py hl=13-15
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

```

```python title=summary_view.py hl=51-53
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

```

#### Upgrade Oxygen Level
---
![[Pasted image 20261001102914.png|1000]]

![[Pasted image 20261001102948.png|1000]]

```python title=game.py hl=8-9
...

    def on_upgrade_purchased(self, upgrade_name: str, remaining_gold: int) -> None:
        """Apply successful shop purchases to the current game."""
        self.gold = remaining_gold
        if upgrade_name == "pickaxe":
            self.player.pickaxe_strength += 1
        elif upgrade_name == "oxygen_tank":
            self.oxygen_system.max_oxygen += 100

...
```

#### Upgrade Inventory Size
---

![[Pasted image 20261001103256.png|1000]]

![[Pasted image 20261001103335.png|1000]]

```python title=game.py hl=10-14
...

    def on_upgrade_purchased(self, upgrade_name: str, remaining_gold: int) -> None:
        """Apply successful shop purchases to the current game."""
        self.gold = remaining_gold
        if upgrade_name == "pickaxe":
            self.player.pickaxe_strength += 1
        elif upgrade_name == "oxygen_tank":
            self.oxygen_system.max_oxygen += 100
        elif upgrade_name == "inventory_size":
            inventory = self.player.inventory
            inventory.slots.append(None)
            inventory.max_slots = len(inventory.slots)
            self.hud_camera.inventory_ui.update()

...
```

GAME OVER! That was fun and entertaining to see this come together.
