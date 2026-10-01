Player Inventory
-  [x] Initial UI
-  [x] Inventory System Setup
-  [x] Inventory UI
	-  [x] Inventory Slot UI
	-  [x] Inventory UI
	-  [x] Add Inventory to HUD
-  [x] Connecting Inventory to UI

### Initial UI
---
The Arcade way to handle the User Interface is to create a unique HUD camera that does not follow the player and is always visible on the display.

![[Pasted image 20260930051325.png|1000]]

```python title=hud_camera.py
import arcade
from pathlib import Path

DEFAULT_FONT = "m5x7"
VIEW_WIDTH = 320
VIEW_HEIGHT = 180
PANEL_WIDTH = 80
PANEL_HEIGHT = 14
PANEL_COLOR = (146, 99, 42)

class HudCamera(arcade.Camera2D):
    def __init__(self):
        super().__init__(
            projection=arcade.LRBT(
                -VIEW_WIDTH / 2, VIEW_WIDTH / 2,
                -VIEW_HEIGHT / 2, VIEW_HEIGHT / 2,
            ),
            position=(VIEW_WIDTH / 2, VIEW_HEIGHT / 2),
        )
        arcade.load_font(Path(__file__).resolve().parent / "assets" / "font" / "m5x7.ttf")
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
        self.resize()

    def resize(self):
        self.match_window(projection=False)

    def draw(self):
        self.use()
        arcade.draw_rect_filled(
            arcade.XYWH(self.DepthText.x, PANEL_HEIGHT / 2, PANEL_WIDTH, PANEL_HEIGHT),
            PANEL_COLOR,
        )
        self.DepthText.draw()

```

```python title=level_manager.py hl=39
import arcade
from pathlib import Path
from random import choice
from level import Level

class LevelManager:
    def __init__(self, game_view):
        self.game_view = game_view
        self.current_map = None

    def load_first_level(self):
        self.load_level(1)

    def load_level(self, depth):
        map_name = "base_map.json"
        if depth > 1:
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
        level.generate_rocks(scene)
        scene.add_sprite_list("Ore")

        player = level.spawn_player(scene)
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
        view.physics_engine = physics_engine
        view.player_on_ladder = False
        view.background_color = level.tile_map.background_color or arcade.color.BLACK
        view.camera.follow(player, level)
        self.current_map = map_name

    def next_level(self):
        self.load_level(self.game_view.level.current_depth + 1)
        print(f"Current depth: {self.game_view.level.current_depth}")

```

```python title=game.py hl=5,16,35,40,
import arcade

from level_manager import LevelManager
from game_camera import GameCamera
from hud_camera import HudCamera

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
        self.player.on_key_press(key, key_modifiers)
        for ladder in arcade.check_for_collision_with_list(self.player, self.scene["Ladder"]):
            if ladder.on_key_press(key, key_modifiers):
                self.level_manager.next_level()
                return

    def on_key_release(self, key, key_modifiers):
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

### Inventory System Setup
---
The player inventory is a collection of inventory slots. When the player picks up an ore, it will go into the first slot. The next ore pickup will go into the next slot, and so on... 

```Output
[<inventory_slot.InventorySlot object at 0x000002EDB9FE2660>, None, None, None]
stone_ore | 2
```

```python title=inventory_slot.py
STACK_SIZE = 5

class InventorySlot:
    def __init__(self, data, qty):
        self.ore_data = data
        self.quantity = qty

    def can_stack(self, data) -> bool:
        return self.ore_data.name == data.name and self.quantity < STACK_SIZE

    def add_ore(self):
        self.quantity += 1

```

```python title=inventory.py
from inventory_slot import InventorySlot

class Inventory:
    def __init__(self, starting_slots=4):
        self.slots = []
        self.starting_slots = starting_slots
        self.max_slots = starting_slots

        for i in range(self.max_slots):
            self.slots.append(None)

    def add_item(self, data) -> bool:
        # Try stacking with existing item
        for slot in self.slots:
            if slot is not None and slot.can_stack(data):
                slot.add_ore()
                print(slot.ore_data.name, "|", slot.quantity)
                return True

        # Find empty slot
        for i in range(len(self.slots)):
            if self.slots[i] is None:
                self.slots[i] = InventorySlot(data, 1)
                print(self.slots)
                return True

        # No space in the inventory
        return False

```

```python title=player.py hl=7,16,23
import arcade
from pathlib import Path
from enum import Enum, auto

from animation_player import AnimationPlayer, UPDATES_PER_FRAME
from resources import OreData
from inventory import Inventory

PLAYER_SPEED = 3
PICKAXE_COOLDOWN = 0.3
DIAGONAL_SPEED = PLAYER_SPEED / 1.4142  # Diagonal Speed = Player Speed / sqrt(2)

...

        self.pickaxe_cooldown_remaining = 0.0
        self.inventory = Inventory(4)  # Create invetory with 4 slots

    def on_update(self, delta_time):
    
...

    def add_ore(self, data: OreData) -> bool:
        return self.inventory.add_item(data)
        
...
```

### Inventory UI
---
#### Inventory Slot UI
---
![[Pasted image 20260930062852.png]]

That is pretty close to the tutorial image.

```python title=inventory_slot_ui.py
import arcade
from pathlib import Path
from PIL import Image

from resources import ROCK_TYPES

class InventorySlotUi(arcade.Sprite):
    def __init__(self):
        # Create the inventory slot background image
        sprite_sheet = arcade.load_spritesheet(
            Path(__file__).resolve().parent
            / "assets/mine_tiles/Tilesets/Ground - deco 5.png"
        )
        frames = sprite_sheet.get_texture_grid(size=(8, 8), columns=10, count=60)
        background = frames[(2 - 1) * 10 + (2 - 1)].image.convert("RGBA").resize(
            (16, 16), Image.Resampling.NEAREST
        )

        # Create the inventory ore overlay image
        iron = ROCK_TYPES["Iron"]
        iron_sheet = arcade.load_spritesheet(
            Path(__file__).resolve().parent
            / "assets/mine_tiles/Ore n Gems"
            / iron.filename
        )
        iron_frames = iron_sheet.get_texture_grid(size=(16, 16), columns=3, count=12)
        self._background_image = background
        super().__init__(arcade.Texture(background))
        self.item_icon = iron_frames[iron.rock_frame]

        # Create the quantity label
        arcade.load_font(Path(__file__).resolve().parent / "assets/font/m5x7.ttf")
        self.quantity_label = arcade.Text(
            text="x0",
            x=self.right,
            y=self.bottom,
            font_name="m5x7",
            font_size=12,
            color=arcade.color.WHITE,
            anchor_x="right",
            anchor_y="bottom",
        )

    @property
    def item_icon(self) -> arcade.Texture | None:
        """The item texture; assign None to show an empty slot background."""
        return self._item_icon

    @item_icon.setter
    def item_icon(self, texture: arcade.Texture | None):
        background = self._background_image.copy()
        if texture is not None:
            icon_image = texture.image.convert("RGBA").resize(
                (14, 14), Image.Resampling.NEAREST
            )
            background.alpha_composite(icon_image, dest=(1, 1))
        self.texture = arcade.Texture(background)
        self._item_icon = texture

    def draw(self):
        """Draw the slot and its quantity overlay in the active camera."""
        arcade.draw_sprite(self, pixelated=True)
        self.quantity_label.x = self.right
        self.quantity_label.y = self.bottom
        self.quantity_label.draw()

```

```python title=test_inventory_slot.py
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

```

#### Inventory UI
---
The inventory UI displays the four inventory slots.

![[Pasted image 20260930063849.png]]

```python title=inventory_ui.python
from inventory_slot_ui import InventorySlotUi

class InventoryUi:
    def __init__(self, x=0, y=0, spacing=2):
        """Create a row of four slots with its bottom-left corner at (x, y)."""
        self.slots = []
        next_x = x
        for _ in range(4):
            slot = InventorySlotUi()
            slot.left = next_x
            slot.bottom = y
            self.slots.append(slot)
            next_x = slot.right + spacing

    def draw(self):
        for slot in self.slots:
            slot.draw()

```

```python title=test_inventory_ui.py
"""Run this file to preview four inventory slots. Press Escape to close."""

import arcade

from inventory_ui import InventoryUi


class InventoryUiPreview(arcade.Window):
    def __init__(self, visible=True):
        super().__init__(640, 360, "Inventory UI Preview", visible=visible)
        self.background_color = (40, 40, 48)
        self.camera = arcade.Camera2D(
            projection=arcade.LRBT(-160, 160, -90, 90),
            position=(160, 90),
        )
        self.inventory_ui = InventoryUi()
        slots = self.inventory_ui.slots
        row_width = slots[-1].right - slots[0].left
        offset_x = (320 - row_width) / 2 - slots[0].left
        for slot in slots:
            slot.center_x += offset_x
            slot.center_y = 90

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.inventory_ui.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.close()


if __name__ == "__main__":
    InventoryUiPreview()
    arcade.run()

```

#### Add Inventory to HUD
---
Added Inventory UI visibility toggle using Tab key. Visibility is initially off.

![[Pasted image 20260930064344.png|1000]]

```python title=hud_camera.py hl=4,33-40,46-47,49-53,62-63
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
    def __init__(self):
        super().__init__(
            projection=arcade.LRBT(
                -VIEW_WIDTH / 2, VIEW_WIDTH / 2,
                -VIEW_HEIGHT / 2, VIEW_HEIGHT / 2,
            ),
            position=(VIEW_WIDTH / 2, VIEW_HEIGHT / 2),
        )
        arcade.load_font(Path(__file__).resolve().parent / "assets" / "font" / "m5x7.ttf")
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
        self.inventory_ui = InventoryUi()
        self.inventory_visible = False
        slots = self.inventory_ui.slots
        row_width = slots[-1].right - slots[0].left
        offset_x = (VIEW_WIDTH - row_width) / 2 - slots[0].left
        for slot in slots:
            slot.center_x += offset_x
            slot.top = VIEW_HEIGHT
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
        arcade.draw_rect_filled(
            arcade.XYWH(self.DepthText.x, PANEL_HEIGHT / 2, PANEL_WIDTH, PANEL_HEIGHT),
            PANEL_COLOR,
        )
        self.DepthText.draw()
        if self.inventory_visible:
            self.inventory_ui.draw()

```

### Connecting Inventory to UI
---
I persisted the player inventory on level transitions.

![[Pasted image 20260930070240.png|1000]]

I set the background color on this map to 333c3a.

```python title=inventory.py
from inventory_slot import InventorySlot

class Inventory:
    def __init__(self, starting_slots=4):
        self.slots = []
        self.starting_slots = starting_slots
        self.max_slots = starting_slots

        for i in range(self.max_slots):
            self.slots.append(None)

    def add_item(self, data) -> bool:
        # Try stacking with existing item
        for slot in self.slots:
            if slot is not None and slot.can_stack(data):
                slot.add_ore()
                print(slot.ore_data.name, "|", slot.quantity)
                return True

        # Find empty slot
        for i in range(len(self.slots)):
            if self.slots[i] is None:
                self.slots[i] = InventorySlot(data, 1)
                print(self.slots)
                return True

        # No space in the inventory
        return False

```

```python title=level_manager.py
import arcade
from pathlib import Path
from random import choice
from level import Level

class LevelManager:
    def __init__(self, game_view):
        self.game_view = game_view
        self.current_map = None

    def load_first_level(self):
        self.load_level(1, preserve_inventory=False)

    def load_level(self, depth, preserve_inventory=True):
        map_name = "base_map.json"
        if depth > 1:
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

    def next_level(self):
        self.load_level(self.game_view.level.current_depth + 1)
        print(f"Current depth: {self.game_view.level.current_depth}")

```

```python title=hud_camera.py
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
    def __init__(self):
        super().__init__(
            projection=arcade.LRBT(
                -VIEW_WIDTH / 2, VIEW_WIDTH / 2,
                -VIEW_HEIGHT / 2, VIEW_HEIGHT / 2,
            ),
            position=(VIEW_WIDTH / 2, VIEW_HEIGHT / 2),
        )
        arcade.load_font(Path(__file__).resolve().parent / "assets" / "font" / "m5x7.ttf")
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
        arcade.draw_rect_filled(
            arcade.XYWH(self.DepthText.x, PANEL_HEIGHT / 2, PANEL_WIDTH, PANEL_HEIGHT),
            PANEL_COLOR,
        )
        self.DepthText.draw()
        if self.inventory_visible:
            self.inventory_ui.draw()

```
