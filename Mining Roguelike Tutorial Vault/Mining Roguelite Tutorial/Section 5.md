Exiting The Mines
-  [x] Exit Ladder
-  [x] UI To Show Summary of Collected Ores
-  [x] Count Collected Ores
-  [x] Update Summary Display
-  [x] Configure Summary Buttons
	-  [x] Collect Gold

### Exit Ladder
---
![[Pasted image 20260930101853.png|1000]]

```python title=ladder.py hl=22-23
import arcade
from pathlib import Path

class Ladder(arcade.Sprite):
    def __init__(self, type="Down"):
        asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Props/ladder.png"
        sprite_sheet = arcade.load_spritesheet(asset_path)
        frames = sprite_sheet.get_texture_grid(size=(48, 48), columns=2, count=2)
        match type:
            case "Down":
                texture = frames[1]
            case "Up":
                texture = frames[0]
            case _:
                raise ValueError(f"Unknown ladder type: {type!r}. Expected 'Up' or 'Down'.")

        super().__init__(texture)
        self.type = type

    def on_key_press(self, key, key_modifiers):
        # GameView forwards input only while the player overlaps this ladder.
        return (key == arcade.key.L and self.type == "Down") or (
            key == arcade.key.E and self.type == "Up"
        )

```

```python title=level_manager.py hl=10,13,18-20,58,64-71
import arcade
from pathlib import Path
from random import choice
from level import Level

class LevelManager:
    def __init__(self, game_view):
        self.game_view = game_view
        self.current_map = None
        self.maps_by_depth = {}

    def load_first_level(self):
        self.maps_by_depth.clear()
        self.load_level(1, preserve_inventory=False)

    def load_level(self, depth, preserve_inventory=True):
        map_name = "base_map.json"
        if depth in self.maps_by_depth:
            map_name = self.maps_by_depth[depth]
        elif depth > 1:
            maps_path = Path(__file__).resolve().parent / "assets" / "maps"
            map_names = ["base_map.json"] + sorted(
                path.name for path in maps_path.glob("map_*.json") if path.is_file()
            )
            other_maps = [name for name in map_names if name != self.current_map]
            map_name = choice(other_maps or map_names)
        level = Level(map_name=map_name)
        level.current_depth = depth
        scene = arcade.Scene.from_tilemap(level.tile_map)
        scene.add_sprite_list("Ladder")
        level.spawn_exit_ladders(scene)
        level.generate_rocks(scene)
        scene.add_sprite_list("Ore")

        player = level.spawn_player(scene)
        previous_player = getattr(self.game_view, "player", None)
        if preserve_inventory and previous_player is not None:
            # Keep the same inventory when replacing the player for a new map.
            player.inventory = previous_player.inventory
        level.constrain_player(player)
        physics_engine = arcade.PhysicsEngineSimple(
            player,
            [scene["Collision_Walls"], scene["Rock"], scene["Ore"]],
        )

        view = self.game_view
        view.level = level
        view.hud_camera.DepthText.text = f"Depth: {level.current_depth}"
        view.scene = scene
        view.player = player
        view.hud_camera.inventory_ui.inventory = player.inventory
        view.hud_camera.inventory_ui.update()
        view.physics_engine = physics_engine
        view.player_on_ladder = False
        view.background_color = level.tile_map.background_color or arcade.color.BLACK
        view.camera.follow(player, level)
        self.current_map = map_name
        self.maps_by_depth[depth] = map_name

    def next_level(self):
        self.load_level(self.game_view.level.current_depth + 1)
        print(f"Current depth: {self.game_view.level.current_depth}")

    def previous_level(self):
        if self.current_map == "base_map.json":
            print("The player is exiting the mine")
            return
        depth = self.game_view.level.current_depth
        if depth > 1:
            self.load_level(depth - 1)
            print(f"Current depth: {self.game_view.level.current_depth}")

```

```python title=game.py
   ...
   
   def on_key_press(self, key, key_modifiers):
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
                
...
```

Note: I did not disable player movement on top level exit. First, I want to see where he goes.
### UI To Show Summary of Collected Ores
---
Reference image for the exit screen:

![[Pasted image 20260930103131.png]]

Rounded buttons are a pain in Arcade, so I made them square.

![[Pasted image 20260930114924.png]]

```python title=summary_row.py
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

```

![[Pasted image 20260930115032.png]]

```python title=test_summary_row.py
"""Run this file to preview the summary row. Press Escape to close."""

import arcade

from summary_row_ui import SummaryRow


class SummaryRowPreview(arcade.Window):
    def __init__(self, visible=True):
        super().__init__(640, 360, "Summary Row Preview", visible=visible)
        self.background_color = (245, 245, 248)
        self.camera = arcade.Camera2D(
            projection=arcade.LRBT(-160, 160, -90, 90),
            position=(160, 90),
        )
        self.row = SummaryRow(color=(40, 40, 48))
        self.row.x = (320 - self.row.width) / 2
        self.row.y = (180 - self.row.height) / 2

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.row.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.close()


if __name__ == "__main__":
    SummaryRowPreview()
    arcade.run()

```

```python title=button_theme.py
"""Shared styles for UI buttons."""

import arcade
from arcade.gui import UIFlatButton


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

```python title=test_summary.py
"""Run this file to preview the summary UI. Press Escape to close."""

import arcade

from summary_ui import SummaryUi

PREVIEW_WIDTH = 400
PREVIEW_HEIGHT = 300

class SummaryUiPreview(arcade.Window):
    def __init__(self, visible=True):
        super().__init__(800, 600, "Summary UI Preview", visible=visible)
        self.background_color = (0, 0, 0)
        self.camera = arcade.Camera2D(
            projection=arcade.LRBT(
                -PREVIEW_WIDTH / 2, PREVIEW_WIDTH / 2,
                -PREVIEW_HEIGHT / 2, PREVIEW_HEIGHT / 2,
            ),
            position=(PREVIEW_WIDTH / 2, PREVIEW_HEIGHT / 2),
        )
        self.summary_ui = SummaryUi()
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

```

### Count Collected Ores & Update Summary Display
---
![[Pasted image 20260930120507.png|1058]]

```python title=summary_view.py
"""Inventory summary shown when leaving the mine."""

import arcade

from summary_ui import SummaryUi

class SummaryView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.background_color = arcade.color.BLACK
        self.camera = arcade.Camera2D()
        self.summary_ui = SummaryUi(inventory=game_view.player.inventory)
        self.summary_ui.button_manager.camera = self.camera
        self.summary_ui.mines_button.push_handlers(on_click=self._return_to_mines)
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

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self._return_to_mines()

```

```python title=level_manager.py hl=4
...

    def previous_level(self):
        if self.current_map == "base_map.json":
            print("The player is exiting the mine")
            self.game_view.show_summary()
            return
        depth = self.game_view.level.current_depth
        if depth > 1:
            self.load_level(depth - 1)
            print(f"Current depth: {self.game_view.level.current_depth}")
            
...
```

```python title=game.py hl=6,21-30
import arcade

from level_manager import LevelManager
from game_camera import GameCamera
from hud_camera import HudCamera
from summary_view import SummaryView

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.camera = GameCamera()
        self.hud_camera = HudCamera()
        self.level_manager = LevelManager(self)
        self.level_manager.load_first_level()

    def show_summary(self):
        self.player.change_x = 0
        self.player.change_y = 0
        self.player.pickaxe_held = False
        self.window.show_view(SummaryView(self))

    def on_show_view(self):
        self.camera.resize()
        self.hud_camera.resize()
        self.camera.follow(self.player, self.level)
                
...
```

### Configure Summary Buttons
---
```Output
Shop!
```

```python title=summary_ui.py hl=29,48-49
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
        self.shop_button.push_handlers(on_click=self._on_shop_click)
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

    def _on_shop_click(self, event):
        print("Shop!")

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

#### Collect Gold
---
When the player exits the mine we will add the total value of the inventory to a persistent gold variable. The inventory is cleared so we don't count the inventory items twice.

```python title=game.py hl=7,8,17,28-49
import arcade

from level_manager import LevelManager
from game_camera import GameCamera
from hud_camera import HudCamera
from summary_view import SummaryView
from inventory import Inventory
from inventory_slot import InventorySlot

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.gold = 0

        self.camera = GameCamera()
        self.hud_camera = HudCamera()
        self.level_manager = LevelManager(self)
        self.level_manager.load_first_level()

    def show_summary(self):
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
        self.camera.resize()
        self.hud_camera.resize()
        self.camera.follow(self.player, self.level)

...
```

```python title=summary_view.py hl=8,13-15
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
        self.shop_button.push_handlers(on_click=self._on_shop_click)
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

    def _on_shop_click(self, event):
        print("Shop!")

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