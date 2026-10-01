Oxygen System
-  [x] Oxygen System Setup
	-  [x] Oxygen Warning Alert
-  [ ] Death Sequence

### Oxygen System
---
![[Pasted image 20260930140830.png|729]]

Oops, the player has no oxygen.

```python title=oxygen_system.py
# Player oxygen limits the time spent in the mines
class OxygenSystem:
    def __init__(self):
        self.max_oxygen = 100
        self.oxygen: int
        self.oxygen_use = 5
        self.oxygen_time = 1.0
        self.running = True

        self._reset_oxygen()

    def _reset_oxygen(self):
        self.oxygen = self.max_oxygen
        self.oxygen_timer = 0.0

    def start(self):
        self._reset_oxygen()
        self.running = True

    def stop(self):
        self.running = False
        self.oxygen_timer = 0.0

    def on_update(self, delta_time):
        if not self.running:
            return
        self.oxygen_timer += delta_time
        while self.oxygen_timer >= self.oxygen_time:
            self.oxygen_timer -= self.oxygen_time
            self.oxygen = max(0, self.oxygen - self.oxygen_use)

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
        arcade.draw_rect_filled(
            arcade.XYWH(self.OxygenText.x, self.OxygenText.y, PANEL_WIDTH, PANEL_HEIGHT),
            arcade.color.TEAL,
        )
        self.OxygenText.draw()
        arcade.draw_rect_filled(
            arcade.XYWH(self.DepthText.x, PANEL_HEIGHT / 2, PANEL_WIDTH, PANEL_HEIGHT),
            PANEL_COLOR,
        )
        self.DepthText.draw()
        if self.inventory_visible:
            self.inventory_ui.draw()

```

#### Oxygen Warning Alert
---
![[Pasted image 20260930141511.png|857]]

```python title=hud_camera.py hl=63-68
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

```

### Player Death
---
If the oxygen level reaches 0, play the player death animation. Wait 5 seconds then show then show a screen with the message "You Died!" and a button to restart the game.

Note: I implemented a death screen rather than fade in/out on the summary.

![[Pasted image 20260930144317.png|1000]]

![[Pasted image 20260930144344.png|1000]]

```python title=death_view.py
"""Game-over screen with a fresh-game restart."""

from pathlib import Path

import arcade
from arcade.gui import UIFlatButton, UIManager

from button_theme import button_style


class DeathView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK
        arcade.load_font(Path(__file__).resolve().parent / "assets/font/m5x7.ttf")
        self.camera = arcade.Camera2D()
        self.manager = UIManager()
        self.manager.camera = self.camera
        self.message = arcade.Text(
            "You Died!", 0, 0, arcade.color.WHITE,
            font_size=32, font_name="m5x7",
            anchor_x="center", anchor_y="center",
        )
        self.restart_button = self.manager.add(UIFlatButton(
            text="Restart", width=100, height=32, style=button_style,
        ))
        self.restart_button.push_handlers(on_click=self._restart)
        self._resize()

    def _resize(self):
        height = 300
        width = height * self.window.width / max(1, self.window.height)
        self.camera.match_window()
        self.camera.projection = arcade.LRBT(-width / 2, width / 2, -height / 2, height / 2)
        self.camera.position = (width / 2, height / 2)
        self.message.x = width / 2
        self.message.y = height / 2 + 30
        self.restart_button.left = (width - self.restart_button.width) / 2
        self.restart_button.bottom = height / 2 - 40

    def on_show_view(self):
        self.manager.enable()
        self._resize()

    def on_hide_view(self):
        self.manager.disable()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self._resize()

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.message.draw()
        self.manager.draw()

    def _restart(self, event=None):
        from game import GameView

        self.window.show_view(GameView())

```

```python title=player.py
import arcade
from pathlib import Path
from enum import Enum, auto

from animation_player import AnimationPlayer, UPDATES_PER_FRAME
from resources import OreData
from inventory import Inventory

PLAYER_SPEED = 3
PICKAXE_COOLDOWN = 0.3
DIAGONAL_SPEED = PLAYER_SPEED / 1.4142  # Diagonal Speed = Player Speed / sqrt(2)

class Dir(Enum):
    RIGHT = auto()
    LEFT = auto()
    UP = auto()
    DOWN = auto()

class State(Enum):
    IDLE = auto()
    RUN = auto()
    ATTACK = auto()
    DEATH = auto()
    SWING_PICKAXE = auto()
    CLIMB_DOWN = auto()
    CLIMB_UP = auto()

# Local (left, right, bottom, top) bounds for the windup and strike frames.
PICKAXE_BOUNDS = {
    Dir.RIGHT: [(-16, -3, 0, 12), (4, 17, -10, 2)],
    Dir.LEFT: [(3, 16, 0, 12), (-17, -4, -10, 2)],
    Dir.DOWN: [(-7, 2, 5, 23), (-6, 7, -22, -8)],
    Dir.UP: [(0, 10, 5, 23), (4, 13, -10, 5)],
}

class Player(arcade.Sprite):
    def __init__(self):
        asset_path = Path(__file__).resolve().parent / "assets/player/Player.png"
        sprite_sheet = arcade.load_spritesheet(asset_path)
        # The sheet has 6 columns and 10 rows of 32x32 frames for a total of 60 frames
        frames = sprite_sheet.get_texture_grid(
            size=(32, 32), columns=6, count=60
        )

        actions_path = Path(__file__).resolve().parent / "assets/player/Player_Actions.png"
        sprite_sheet = arcade.load_spritesheet(actions_path)
        # The sheet has 2 columns and 12 rows of 48x48 frames for a total of 24 frames
        action_frames = sprite_sheet.get_texture_grid(
            size=(48, 48), columns=2, count=24
        )
        super().__init__(frames[0])

        # Fixed lower-body rectangle, above the ankles and below the waist.
        self.hit_box = arcade.hitbox.RotatableHitBox(
            [(-4, -6), (4, -6), (4, -3), (-4, -3)],
            position=self.position,
            scale=self.scale,
        )

        self.idle_down = frames[0:6]
        self.idle_right = frames[6:12]
        self.idle_up = frames[12:18]
        self.idle_left = [frame.flip_left_right() for frame in self.idle_right]

        self.run_down = frames[18:24]
        self.run_right = frames[24:30]
        self.run_up = frames[30:36]
        self.run_left = [frame.flip_left_right() for frame in self.run_right]

        self.attack_down = frames[36:40]
        self.attack_right = frames[42:46]
        self.attack_up = frames[48:52]
        self.attack_left = [frame.flip_left_right() for frame in self.attack_right]

        self.death_right = frames[54:58]
        self.death_left = [frame.flip_left_right() for frame in self.death_right]

        self.swing_pickaxe_right = action_frames[0:2]
        self.swing_pickaxe_down = action_frames[2:4]
        self.swing_pickaxe_up = action_frames[4:6]
        self.swing_pickaxe_left = [frame.flip_left_right() for frame in self.swing_pickaxe_right]

        self.animations = {
            "idle_down": self.idle_down,
            "idle_right": self.idle_right,
            "idle_up": self.idle_up,
            "idle_left": self.idle_left,
            "run_down": self.run_down,
            "run_right": self.run_right,
            "run_up": self.run_up,
            "run_left": self.run_left,
            "attack_down": self.attack_down,
            "attack_right": self.attack_right,
            "attack_up": self.attack_up,
            "attack_left": self.attack_left,
            "death_right": self.death_right,
            "death_left": self.death_left,
            "swing_pickaxe_right": self.swing_pickaxe_right,
            "swing_pickaxe_down": self.swing_pickaxe_down,
            "swing_pickaxe_up": self.swing_pickaxe_up,
            "swing_pickaxe_left": self.swing_pickaxe_left,
        }

        self.animation_player = AnimationPlayer()
        self.current_direction = Dir.DOWN
        self.current_state = State.IDLE
        # Collision-only sprite; keep it out of the scene and movement physics.
        self.pickaxe_hitbox = arcade.SpriteSolidColor(48, 48, color=arcade.color.WHITE)
        self.pickaxe_active = False
        self.rocks_hit_this_swing = set()
        self.pickage_strength = 1  # Future ability increase
        self.pickaxe_held = False
        self.pickaxe_cooldown_remaining = 0.0
        self.inventory = Inventory(4)  # Create invetory with 4 slots

    def die(self):
        if self.current_state == State.DEATH:
            return
        self.change_x = 0
        self.change_y = 0
        self.pickaxe_held = False
        self.pickaxe_active = False
        # The sprite sheet only has horizontal death animations.
        if self.current_direction != Dir.LEFT:
            self.current_direction = Dir.RIGHT
        self.animation_player.reset()
        self.current_state = State.DEATH

    def on_update(self, delta_time):
        self.pickaxe_active = False
        self.pickaxe_cooldown_remaining = max(
            0.0, self.pickaxe_cooldown_remaining - delta_time
        )
        if self.pickaxe_held:
            self._try_start_pickaxe_swing()
        match self.current_state:
            case State.IDLE:
                textures = self.animations[f"idle_{self.current_direction.name.lower()}"]
                self.texture = self.animation_player.update_animation(textures)
            case State.RUN:
                textures = self.animations[f"run_{self.current_direction.name.lower()}"]
                self.texture = self.animation_player.update_animation(textures)
            case State.ATTACK:
                textures = self.animations[f"attack_{self.current_direction.name.lower()}"]
                self.texture = self.animation_player.update_animation(textures, one_shot=True)
            case State.DEATH:
                textures = self.animations[f"death_{self.current_direction.name.lower()}"]
                self.texture = self.animation_player.update_animation(textures, one_shot=True)
            case State.SWING_PICKAXE:
                textures = self.animations[f"swing_pickaxe_{self.current_direction.name.lower()}"]
                frame = min(self.animation_player.cur_texture // UPDATES_PER_FRAME, len(textures) - 1)
                self._update_pickaxe_hitbox(frame)
                self.texture = self.animation_player.update_animation(textures, one_shot=True)
                if self.animation_player.finished:
                    self.current_state = State.IDLE
                    self.animation_player.reset()
                    self.pickaxe_cooldown_remaining = PICKAXE_COOLDOWN
            case _:
                textures = self.animations[f"idle_{self.current_direction.name.lower()}"]
                self.texture = self.animation_player.update_animation(textures)                     

    def _try_start_pickaxe_swing(self):
        if self.current_state not in (State.IDLE, State.RUN):
            return
        if self.pickaxe_cooldown_remaining > 0:
            return
        self.rocks_hit_this_swing.clear()
        self.change_x = 0
        self.change_y = 0
        self.animation_player.reset()
        self.current_state = State.SWING_PICKAXE

    def _update_pickaxe_hitbox(self, frame):
        left, right, bottom, top = PICKAXE_BOUNDS[self.current_direction][frame]
        self.pickaxe_hitbox.position = self.position
        self.pickaxe_hitbox.hit_box = arcade.hitbox.RotatableHitBox(
            [(left, bottom), (right, bottom), (right, top), (left, top)],
            position=self.position,
            scale=self.scale,
        )
        self.pickaxe_active = True

    def hit_rocks(self, rocks):
        if not self.pickaxe_active:
            return
        for rock in arcade.check_for_collision_with_list(self.pickaxe_hitbox, rocks):
            if rock not in self.rocks_hit_this_swing:
                rock.take_damage(self.pickage_strength)
                self.rocks_hit_this_swing.add(rock)

    def on_key_press(self, key, key_modifiers):
        if self.current_state == State.DEATH:
            return
        if key == arcade.key.SPACE:
            self.pickaxe_held = True
            self._try_start_pickaxe_swing()
            return

        if self.current_state == State.SWING_PICKAXE:
            return

        if key in (arcade.key.LCTRL, arcade.key.RCTRL):
            self.animation_player.reset()
            self.current_state = State.ATTACK
            return

        if key in (arcade.key.A, arcade.key.LEFT):
            self.change_x -= PLAYER_SPEED
            self.current_direction = Dir.LEFT
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.change_x += PLAYER_SPEED
            self.current_direction = Dir.RIGHT
        elif key in (arcade.key.W, arcade.key.UP):
            self.change_y += PLAYER_SPEED
            self.current_direction = Dir.UP
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.change_y -= PLAYER_SPEED
            self.current_direction = Dir.DOWN
        else:
            return

        self.current_state = State.RUN

        # Normalize diagonal movement speed so the player speed is constant in all directions
        if self.change_x != 0 and self.change_y != 0:
            self.change_x = DIAGONAL_SPEED if self.change_x > 0 else -DIAGONAL_SPEED
            self.change_y = DIAGONAL_SPEED if self.change_y > 0 else -DIAGONAL_SPEED

    def on_key_release(self, key, key_modifiers):
        if self.current_state == State.DEATH:
            return
        if key == arcade.key.SPACE:
            self.pickaxe_held = False
            return

        if self.current_state == State.SWING_PICKAXE:
            return

        if key in (arcade.key.A, arcade.key.LEFT, arcade.key.D, arcade.key.RIGHT):
            self.change_x = 0
            self.current_state = State.IDLE
        elif key in (arcade.key.W, arcade.key.UP, arcade.key.S, arcade.key.DOWN):
            self.change_y = 0
            self.current_state = State.IDLE

    def add_ore(self, data: OreData) -> bool:
        return self.inventory.add_item(data)

```

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