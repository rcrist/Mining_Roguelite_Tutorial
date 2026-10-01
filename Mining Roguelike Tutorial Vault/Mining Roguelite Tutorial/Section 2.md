Breakable Rocks and Mining Mechanics
-  [x] Creating a Basic Rock Sprite
-  [x] Player and Rock Colliders (Hit-Boxes)
-  [x] Using Data Classes to Store Rock Properties
-  [x] Player Mining Animation
-  [x] Mining Hitbox
-  [x] Destroy Rock and Drop Ore
-  [x] Continuous Pickaxe Swing
-  [x] Ore Class
-  [x] Resources Module
-  [x] Pickup Ore
-  [x] Mining Polish
	-  [x] Ore Drop Animation
	-  [x] Random Horizontal Bounce
	-  [x] Ore Pickup Flash Effect
	-  [x] Rock Hit Sound Effect
	-  [x] Rock Destroyed Sound Effect
	-  [ ] Player walk dust particles
	-  [ ] Ore spawn dust particles

### Create a Basic Rock Sprite
---
![[Pasted image 20260928084500.png|1000]]

```python title=rock.py
import arcade
from pathlib import Path

class Rock(arcade.Sprite):
    def __init__(self):
        asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
        sprite_sheet = arcade.load_spritesheet(asset_path)
        frames = sprite_sheet.get_texture_grid(
                    size=(16, 16), columns=3, count=12
                )
        super().__init__(self.data.texture)

```

```python title=game.py hl=4,19-21,
import arcade

from player import Player
from rock import Rock
from game_camera import GameCamera, VIEW_WIDTH, VIEW_HEIGHT

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.BLACK
        self.scene = arcade.Scene()
        self.camera = GameCamera()

        self.rock = Rock()
        self.rock.position = (VIEW_WIDTH/2 + 50, VIEW_HEIGHT/2)
        self.scene.add_sprite("Rock", self.rock)

        self.player = Player()
        self.player.position = (VIEW_WIDTH/2, VIEW_HEIGHT/2)
        self.scene.add_sprite("Player", self.player)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw(pixelated=True)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.camera.resize()

    def on_update(self, delta_time):
        self.scene.update(delta_time)
        self.player.on_update(delta_time)

    def on_key_press(self, key, key_modifiers):
        self.player.on_key_press(key, key_modifiers)

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

### Player and Rock Colliders (Hit-Boxes)
---
At this point, we will turn on Arcade hit-boxes which are colliders for the player and rock. We will adjust the player hit-box so the player's upper-body can "walk" in front of the stone before colliding. We will use the Arcade simple physics engine to check for collisions between player and stone. We will change the `on_update()` method to update the physics engine rather than the scene.

![[Pasted image 20260928085221.png|1000]]

If you move the player toward the stone, the player collides with the stone as if it were solid. The default hit box for the stone is shown above and is a better fit than a simple circle.

```python title=player.py hl=32-37
import arcade
from pathlib import Path
from enum import Enum, auto

from animation_player import AnimationPlayer

PLAYER_SPEED = 3
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

class Player(arcade.Sprite):
    def __init__(self):
        asset_path = Path(__file__).resolve().parent / "assets/player/Player.png"
        sprite_sheet = arcade.load_spritesheet(asset_path)
        # The sheet has 6 columns and 10 rows of 32x32 frames for a total of 60 frames
        frames = sprite_sheet.get_texture_grid(
            size=(32, 32), columns=6, count=60
        )
        super().__init__(frames[0])

        # Fixed lower-body rectangle, above the ankles and below the waist.
        self.hit_box = arcade.hitbox.RotatableHitBox(
            [(-4, -6), (4, -6), (4, -3), (-4, -3)],
            position=self.position,
            scale=self.scale,
        )

...
```

```python title=game.py hl=27-29,35-38,45-46
import arcade

from player import Player
from rock import Rock
from game_camera import GameCamera, VIEW_WIDTH, VIEW_HEIGHT

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.BLACK
        self.scene = arcade.Scene()
        self.camera = GameCamera()

        self.rock = Rock()
        self.rock.position = (VIEW_WIDTH/2 + 50, VIEW_HEIGHT/2)
        self.scene.add_sprite("Rock", self.rock)

        self.player = Player()
        self.player.position = (VIEW_WIDTH/2, VIEW_HEIGHT/2)
        self.scene.add_sprite("Player", self.player)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.scene["Rock"]
        )

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw(pixelated=True)
        self.scene.draw_hit_boxes(
            color=arcade.color.YELLOW,
            line_thickness=1,
        )

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.camera.resize()

    def on_update(self, delta_time):
        # The physics engine moves the player and resolves rock collisions.
        self.physics_engine.update()
        self.player.on_update(delta_time)

    def on_key_press(self, key, key_modifiers):
        self.player.on_key_press(key, key_modifiers)

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
### Using Data Classes to Store Rock Properties
---
As discussed in the reference tutorial, we will create a "configurable" rock that can represent different ores which when mined will "drop" a refined ore such as small stone, silver, iron, etc. We will use a Python data class to define the properties of each ore type and then set the type when the ore is instantiated.

![[Pasted image 20260928090211.png|1000]]

```python title=rock.py hl=2,5-11,13-19,21-46
import arcade
from dataclasses import dataclass
from pathlib import Path

@dataclass
class StoneData:
    texture: arcade.Texture
    ore: arcade.Texture
    max_health: int = 3
    rarity: int = 50
    min_depth: int = 1

@dataclass
class IronData:
    texture: arcade.Texture
    ore: arcade.Texture
    max_health: int = 4
    rarity: int = 25
    min_depth: int = 3

class Rock(arcade.Sprite):
    def __init__(self, type="Stone"):
        match type:
            case "Stone":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = StoneData(texture=frames[10], ore=frames[0])
            case "Iron":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/iron.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = StoneData(texture=frames[2], ore=frames[0])
            case _:
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=6
                        )
                self.data = StoneData(texture=frames[10], ore=frames[0])
    
        super().__init__(self.data.texture)

```

```python title=game.py hl=19
import arcade

from player import Player
from rock import Rock
from game_camera import GameCamera, VIEW_WIDTH, VIEW_HEIGHT

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.BLACK
        self.scene = arcade.Scene()
        self.camera = GameCamera()

        self.rock = Rock(type="Iron")
        self.rock.position = (VIEW_WIDTH/2 + 50, VIEW_HEIGHT/2)
        self.scene.add_sprite("Rock", self.rock)

        self.player = Player()
        self.player.position = (VIEW_WIDTH/2, VIEW_HEIGHT/2)
        self.scene.add_sprite("Player", self.player)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.scene["Rock"]
        )

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw(pixelated=True)
        self.scene.draw_hit_boxes(
            color=arcade.color.YELLOW,
            line_thickness=1,
        )

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.camera.resize()

    def on_update(self, delta_time):
        # The physics engine moves the player and resolves rock collisions.
        self.physics_engine.update()
        self.player.on_update(delta_time)

    def on_key_press(self, key, key_modifiers):
        self.player.on_key_press(key, key_modifiers)

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

### Player Mining Animation
---
This game won't use the ATTACK animation so we can leave the animation code (in case we add it later) but change the input controller so that the space key controls the `swing_pickaxe` animation. The swing pickaxe animation is in a different asset file called `Player_Actions.png`. We will process the second player animation file similar to the way we processed `Player.png`.

![[Player_Actions.png]]

Image Size: 96x576 px
Frames: 12 rows x 2 columns = 24 frames
Frame Size: 48x48 px which is interesting since the original player sprites are 32x32 px. Solution is to scale the larger sprite down to match the original size, I think.

<video src=20260928-1526-02.7644189.mp4 controls width="1000"></video>

```python title=player.py hl=21,32-37,65-68,85-88,109-114,132
import arcade
from pathlib import Path
from enum import Enum, auto

from animation_player import AnimationPlayer

PLAYER_SPEED = 3
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

    def on_update(self, delta_time):
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
                self.texture = self.animation_player.update_animation(textures, one_shot=True)
                if self.animation_player.finished:
                    self.current_state = State.IDLE
                    self.animation_player.reset()
            case _:
                textures = self.animations[f"idle_{self.current_direction.name.lower()}"]
                self.texture = self.animation_player.update_animation(textures)                     

    def on_key_press(self, key, key_modifiers):
        if self.current_state == State.SWING_PICKAXE:
            return

        if key in (arcade.key.LCTRL, arcade.key.RCTRL):
            self.animation_player.reset()
            self.current_state = State.ATTACK
            return

        if key == arcade.key.SPACE:
            self.change_x = 0
            self.change_y = 0
            self.animation_player.reset()
            self.current_state = State.SWING_PICKAXE
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
        if self.current_state == State.SWING_PICKAXE:
            return

        if key in (arcade.key.A, arcade.key.LEFT, arcade.key.D, arcade.key.RIGHT):
            self.change_x = 0
            self.current_state = State.IDLE
        elif key in (arcade.key.W, arcade.key.UP, arcade.key.S, arcade.key.DOWN):
            self.change_y = 0
            self.current_state = State.IDLE

```

### Mining Hitbox
---
The mining hitbox will follow the player pickaxe motion so that it can collide with rocks in the scene. When the pickaxe hitbox collides with a rock, health is decreased by 1 and initially printed to the terminal. I am not going to worry about hitting multiple rocks for this tutorial because it seems like a minor detail.

```python title=player.py hl=24-30,104-106,126,135-143,145-151
import arcade
from pathlib import Path
from enum import Enum, auto

from animation_player import AnimationPlayer, UPDATES_PER_FRAME

PLAYER_SPEED = 3
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

    def on_update(self, delta_time):
        self.pickaxe_active = False
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
            case _:
                textures = self.animations[f"idle_{self.current_direction.name.lower()}"]
                self.texture = self.animation_player.update_animation(textures)                     

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
                rock.take_damage(1)
                self.rocks_hit_this_swing.add(rock)

    def on_key_press(self, key, key_modifiers):
        if self.current_state == State.SWING_PICKAXE:
            return

        if key in (arcade.key.LCTRL, arcade.key.RCTRL):
            self.animation_player.reset()
            self.current_state = State.ATTACK
            return

        if key == arcade.key.SPACE:
            self.rocks_hit_this_swing.clear()
            self.change_x = 0
            self.change_y = 0
            self.animation_player.reset()
            self.current_state = State.SWING_PICKAXE
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
        if self.current_state == State.SWING_PICKAXE:
            return

        if key in (arcade.key.A, arcade.key.LEFT, arcade.key.D, arcade.key.RIGHT):
            self.change_x = 0
            self.current_state = State.IDLE
        elif key in (arcade.key.W, arcade.key.UP, arcade.key.S, arcade.key.DOWN):
            self.change_y = 0
            self.current_state = State.IDLE

```

### Destroy Rock and Drop Ore
---
Let's implement the rock destroy() method that is called when the rock health is <= 0. The rock texture is set to the ore texture in the associated data class. The ore cannot take further damage from the player. In other words, when the rock is destroyed, it morphs into its ore element.

![[Pasted image 20260928104705.png|1000]]

```Output
Rock health: 3
Rock health: 2
Rock health: 1
Rock health: 0
```

```python title=rock.py hl=48,50-60,62-64
import arcade
from dataclasses import dataclass
from pathlib import Path

@dataclass
class StoneData:
    texture: arcade.Texture
    ore: arcade.Texture
    max_health: int = 3
    rarity: int = 50
    min_depth: int = 1

@dataclass
class IronData:
    texture: arcade.Texture
    ore: arcade.Texture
    max_health: int = 4
    rarity: int = 25
    min_depth: int = 3

class Rock(arcade.Sprite):
    def __init__(self, type="Stone"):
        match type:
            case "Stone":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = StoneData(texture=frames[10], ore=frames[0])
            case "Iron":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/iron.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = IronData(texture=frames[2], ore=frames[0])
            case _:
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=6
                        )
                self.data = StoneData(texture=frames[10], ore=frames[0])
    
        super().__init__(self.data.texture)
        self.health = self.data.max_health
        self.is_ore = False

    def take_damage(self, amount):
        if self.is_ore:
            return

        previous_health = self.health
        self.health = max(0, self.health - amount)
        if self.health != previous_health:
            print(f"Rock health: {self.health}")

        if self.health <= 0:
            self._destroy()

    def _destroy(self) -> None:
        self.is_ore = True
        self.texture = self.data.ore

```

### Continuous Pickaxe Swing
---
Changed the player pickaxe to a continuous animation with a cooldown timer set to 0.3 s. Made it so that if the user holds down the space bar, he can continuously swing the pickaxe after the cooldown.

```python title=player.py hl=8,109-110,114-118,137-140,145-154,175-181,211-216
import arcade
from pathlib import Path
from enum import Enum, auto

from animation_player import AnimationPlayer, UPDATES_PER_FRAME

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

```

### Ore Class
---
After further consideration, when the rock is mined, we need to create a new object of type Ore. I suspect this will make the mining system inventory easier to manage down the road.

```python title=ore.py
import arcade
from pathlib import Path

class Ore(arcade.Sprite):
    def __init__(self, position, data):
        super().__init__(data.ore)
        self.position = position
        self.data = data

```

```python title=rock.py hl=5,24,50-51,62-65
import arcade
from dataclasses import dataclass
from pathlib import Path

from ore import Ore

@dataclass
class StoneData:
    texture: arcade.Texture
    ore: arcade.Texture
    max_health: int = 3
    rarity: int = 50
    min_depth: int = 1

@dataclass
class IronData:
    texture: arcade.Texture
    ore: arcade.Texture
    max_health: int = 4
    rarity: int = 25
    min_depth: int = 3

class Rock(arcade.Sprite):
    def __init__(self, type="Stone", scene=None):
        match type:
            case "Stone":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = StoneData(texture=frames[10], ore=frames[0])
            case "Iron":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/iron.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = IronData(texture=frames[2], ore=frames[0])
            case _:
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=6
                        )
                self.data = StoneData(texture=frames[10], ore=frames[0])
    
        super().__init__(self.data.texture)
        self.health = self.data.max_health
        self.type = type
        self.scene = scene

    def take_damage(self, amount):
        previous_health = self.health
        self.health = max(0, self.health - amount)
        if self.health != previous_health:
            print(f"Rock health: {self.health}")

        if self.health <= 0:
            self._destroy()

    def _destroy(self) -> None:
        ore = Ore(self.position, self.data)
        self.scene.add_sprite("Ore", ore)
        self.remove_from_sprite_lists()

```

```python title=game.py hl=19
import arcade

from player import Player
from rock import Rock
from game_camera import GameCamera, VIEW_WIDTH, VIEW_HEIGHT

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.BLACK
        self.scene = arcade.Scene()
        self.camera = GameCamera()

        self.rock = Rock(type="Iron", scene=self.scene)
        self.rock.position = (VIEW_WIDTH/2 + 50, VIEW_HEIGHT/2)
        self.scene.add_sprite("Rock", self.rock)

        self.player = Player()
        self.player.position = (VIEW_WIDTH/2, VIEW_HEIGHT/2)
        self.scene.add_sprite("Player", self.player)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.scene["Rock"]
        )

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw(pixelated=True)
        self.scene.draw_hit_boxes(
            color=arcade.color.YELLOW,
            line_thickness=1,
        )
        if self.player.pickaxe_active:
            arcade.draw_polygon_outline(
                self.player.pickaxe_hitbox.hit_box.get_adjusted_points(),
                arcade.color.RED,
                1,
            )

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.camera.resize()

    def on_update(self, delta_time):
        # The physics engine moves the player and resolves rock collisions.
        self.physics_engine.update()
        self.player.on_update(delta_time)
        self.player.hit_rocks(self.scene["Rock"])

    def on_key_press(self, key, key_modifiers):
        self.player.on_key_press(key, key_modifiers)

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

### Resources Module
---
![[Pasted image 20260928150018.png|1000]]

```python title=resources.py
import arcade
from dataclasses import dataclass

@dataclass
class RockData:
    texture: arcade.Texture
    ore: arcade.Texture
    max_health: int = 3
    rarity: int = 50
    min_depth: int = 1

@dataclass
class OreData:
    texture: arcade.Texture
    Name: str = "stone_ore"
    value: int = 10

```

```python title=rock.py hl=5
import arcade
from pathlib import Path

from ore import Ore
from resources import RockData, OreData

class Rock(arcade.Sprite):
    def __init__(self, type="Stone", scene=None):
        match type:
            case "Stone":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = RockData(texture=frames[10], ore=frames[0])
            case "Iron":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/iron.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = RockData(texture=frames[2], ore=frames[0])
            case _:
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=6
                        )
                self.data = RockData(texture=frames[10], ore=frames[0])
    
        super().__init__(self.data.texture)
        self.health = self.data.max_health
        self.type = type
        self.scene = scene

    def take_damage(self, amount):
        previous_health = self.health
        self.health = max(0, self.health - amount)
        if self.health != previous_health:
            print(f"Rock health: {self.health}")

        if self.health <= 0:
            self._destroy()

    def _destroy(self) -> None:
        ore = Ore(self.position, self.data)
        self.scene.add_sprite("Ore", ore)
        self.remove_from_sprite_lists()

```

```python title=game.py hl=19-26,33
import arcade

from player import Player
from rock import Rock
from game_camera import GameCamera, VIEW_WIDTH, VIEW_HEIGHT

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.BLACK
        self.scene = arcade.Scene()
        self.camera = GameCamera()

        self.rock1 = Rock(type="Stone", scene=self.scene)
        self.rock1.position = (VIEW_WIDTH/2 + 50, VIEW_HEIGHT/2)
        self.scene.add_sprite("Rock", self.rock1)

        self.rock2 = Rock(type="Iron", scene=self.scene)
        self.rock2.position = (VIEW_WIDTH/2 + 50, VIEW_HEIGHT/2 + 20)
        self.scene.add_sprite("Rock", self.rock2)
        self.scene.add_sprite_list("Ore")

        self.player = Player()
        self.player.position = (VIEW_WIDTH/2, VIEW_HEIGHT/2)
        self.scene.add_sprite("Player", self.player)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, [self.scene["Rock"], self.scene["Ore"]]
        )

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw(pixelated=True)
        self.scene.draw_hit_boxes(
            color=arcade.color.YELLOW,
            line_thickness=1,
        )
        if self.player.pickaxe_active:
            arcade.draw_polygon_outline(
                self.player.pickaxe_hitbox.hit_box.get_adjusted_points(),
                arcade.color.RED,
                1,
            )

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.camera.resize()

    def on_update(self, delta_time):
        # The physics engine moves the player and resolves rock and ore collisions.
        self.physics_engine.update()
        self.player.on_update(delta_time)
        self.player.hit_rocks(self.scene["Rock"])

    def on_key_press(self, key, key_modifiers):
        self.player.on_key_press(key, key_modifiers)

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

### Pickup Ore
---
![[Pasted image 20260928151540.png|1000]]

```python title=ore.py
import arcade
from resources import OreData

class Ore(arcade.Sprite):
    def __init__(self, position, data: OreData):
        super().__init__(data.texture)
        self.position = position
        self.ore_data = data

```

```python title=rock.py hl=46-50
import arcade
from pathlib import Path

from ore import Ore
from resources import RockData, OreData

class Rock(arcade.Sprite):
    def __init__(self, type="Stone", scene=None):
        match type:
            case "Stone":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = RockData(texture=frames[10], ore=frames[0])
            case "Iron":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/iron.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = RockData(texture=frames[2], ore=frames[0])
            case _:
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=6
                        )
                self.data = RockData(texture=frames[10], ore=frames[0])
    
        super().__init__(self.data.texture)
        self.health = self.data.max_health
        self.type = type
        self.scene = scene

    def take_damage(self, amount):
        previous_health = self.health
        self.health = max(0, self.health - amount)
        if self.health != previous_health:
            print(f"Rock health: {self.health}")

        if self.health <= 0:
            self._destroy()

    def _destroy(self) -> None:
        ore_data = OreData(texture=self.data.ore, Name=f"{self.type.lower()}_ore")
        ore = Ore(self.position, ore_data)
        self.scene.add_sprite("Ore", ore)
        self.remove_from_sprite_lists()

```

```python title=player.py hl=6,29-31
import arcade
from pathlib import Path
from enum import Enum, auto

from animation_player import AnimationPlayer, UPDATES_PER_FRAME
from resources import OreData

PLAYER_SPEED = 3
PICKAXE_COOLDOWN = 0.3
DIAGONAL_SPEED = PLAYER_SPEED / 1.4142  # Diagonal Speed = Player Speed / sqrt(2)

...

    def on_key_release(self, key, key_modifiers):
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
        print(data)
        return True
        
```

```python title=game.py hl=33,57-61
import arcade

from player import Player
from rock import Rock
from game_camera import GameCamera, VIEW_WIDTH, VIEW_HEIGHT

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.BLACK
        self.scene = arcade.Scene()
        self.camera = GameCamera()

        self.rock1 = Rock(type="Stone", scene=self.scene)
        self.rock1.position = (VIEW_WIDTH/2 + 50, VIEW_HEIGHT/2)
        self.scene.add_sprite("Rock", self.rock1)

        self.rock2 = Rock(type="Iron", scene=self.scene)
        self.rock2.position = (VIEW_WIDTH/2 + 50, VIEW_HEIGHT/2 + 20)
        self.scene.add_sprite("Rock", self.rock2)
        self.scene.add_sprite_list("Ore")

        self.player = Player()
        self.player.position = (VIEW_WIDTH/2, VIEW_HEIGHT/2)
        self.scene.add_sprite("Player", self.player)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, [self.scene["Rock"], self.scene["Ore"]]
        )

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw(pixelated=True)
        self.scene.draw_hit_boxes(
            color=arcade.color.YELLOW,
            line_thickness=1,
        )
        if self.player.pickaxe_active:
            arcade.draw_polygon_outline(
                self.player.pickaxe_hitbox.hit_box.get_adjusted_points(),
                arcade.color.RED,
                1,
            )

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.camera.resize()

    def on_update(self, delta_time):
        # The physics engine moves the player and resolves rock and ore collisions.
        collisions = self.physics_engine.update()
        for sprite in collisions:
            if sprite in self.scene["Ore"]:
                if self.player.add_ore(sprite.ore_data):
                    sprite.remove_from_sprite_lists()
        self.player.on_update(delta_time)
        self.player.hit_rocks(self.scene["Rock"])

    def on_key_press(self, key, key_modifiers):
        self.player.on_key_press(key, key_modifiers)

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

### Mining Polish
---
- Ore drop animation - ore "bounces" into existence

#### Ore drop animation
Godot tween = arcade easing

This code caused an ore upward movement by 16 pixels over 0.25 seconds.

```python
from arcade.easing import ease_value, ease_update, ease_out

# In Ore.__init__, after setting self.position:
self.move_tween = ease_value(
    self.center_y,
    self.center_y + 16,
    time=0.25,
    ease_function=ease_out,
)
```

Create a `ease_value` for moving the ore up and moving the ore down.

```python title=rock.py hl=6,51,54-67
import arcade
from pathlib import Path

from ore import Ore
from resources import RockData, OreData
from arcade.easing import ease_value, ease_out, ease_in

class Rock(arcade.Sprite):
    def __init__(self, type="Stone", scene=None):
        match type:
            case "Stone":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = RockData(texture=frames[10], ore=frames[0])
            case "Iron":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/iron.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = RockData(texture=frames[2], ore=frames[0])
            case _:
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=6
                        )
                self.data = RockData(texture=frames[10], ore=frames[0])
    
        super().__init__(self.data.texture)
        self.health = self.data.max_health
        self.type = type
        self.scene = scene

    def take_damage(self, amount):
        previous_health = self.health
        self.health = max(0, self.health - amount)
        if self.health != previous_health:
            print(f"Rock health: {self.health}")

        if self.health <= 0:
            self._destroy()

    def _destroy(self) -> None:
        ore_data = OreData(texture=self.data.ore, Name=f"{self.type.lower()}_ore")
        ore = Ore(self.position, ore_data)
        self.scene.add_sprite("Ore", ore)
        self._ore_animation(ore)
        self.remove_from_sprite_lists()

    def _ore_animation(self, ore) -> None:
        ore.move_tween = ease_value(
            ore.center_y,
            ore.center_y + 16,
            time=0.25,
            ease_function=ease_out,
        )

        ore.next_move_tween = ease_value(
            ore.center_y + 16,
            ore.center_y,
            time=0.25,
            ease_function=ease_in,
        )

```

Now, we need to update the ore for the ore animation:

```python title=ore.py hl=2,10-11,13-18
import arcade
from arcade.easing import ease_update
from resources import OreData

class Ore(arcade.Sprite):
    def __init__(self, position, data: OreData):
        super().__init__(data.texture)
        self.position = position
        self.ore_data = data
        self.move_tween = None
        self.next_move_tween = None

    def update(self, delta_time=1 / 60, *args, **kwargs):
        if self.move_tween is not None:
            done, self.center_y = ease_update(self.move_tween, delta_time)
            if done:
                self.move_tween = self.next_move_tween
                self.next_move_tween = None

```

Then we update the Ore spritelist in the scene:

```python title=game.py hl=56
import arcade

from player import Player
from rock import Rock
from game_camera import GameCamera, VIEW_WIDTH, VIEW_HEIGHT

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.BLACK
        self.scene = arcade.Scene()
        self.camera = GameCamera()

        self.rock1 = Rock(type="Stone", scene=self.scene)
        self.rock1.position = (VIEW_WIDTH/2 + 50, VIEW_HEIGHT/2)
        self.scene.add_sprite("Rock", self.rock1)

        self.rock2 = Rock(type="Iron", scene=self.scene)
        self.rock2.position = (VIEW_WIDTH/2 + 50, VIEW_HEIGHT/2 + 20)
        self.scene.add_sprite("Rock", self.rock2)
        self.scene.add_sprite_list("Ore")

        self.player = Player()
        self.player.position = (VIEW_WIDTH/2, VIEW_HEIGHT/2)
        self.scene.add_sprite("Player", self.player)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, [self.scene["Rock"], self.scene["Ore"]]
        )

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw(pixelated=True)
        self.scene.draw_hit_boxes(
            color=arcade.color.YELLOW,
            line_thickness=1,
        )
        if self.player.pickaxe_active:
            arcade.draw_polygon_outline(
                self.player.pickaxe_hitbox.hit_box.get_adjusted_points(),
                arcade.color.RED,
                1,
            )

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.camera.resize()

    def on_update(self, delta_time):
        self.scene["Ore"].update(delta_time)
        # The physics engine moves the player and resolves rock and ore collisions.
        collisions = self.physics_engine.update()
        for sprite in collisions:
            if sprite in self.scene["Ore"]:
                if self.player.add_ore(sprite.ore_data):
                    sprite.remove_from_sprite_lists()
        self.player.on_update(delta_time)
        self.player.hit_rocks(self.scene["Rock"])

    def on_key_press(self, key, key_modifiers):
        self.player.on_key_press(key, key_modifiers)

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

![[20260928-2145-29.0559658.mp4]]

Awesome! This adds a little polish to the ore instantiation.

#### Random Horizontal Bounce

Add a horizontal tween that moves the rock from its current `position.x` to a random + or - 15 px.

```python title=rock.py hl=2,56-60
import arcade
from random import choice
from pathlib import Path

from ore import Ore
from resources import RockData, OreData
from arcade.easing import ease_value, ease_out, ease_in

class Rock(arcade.Sprite):
    def __init__(self, type="Stone", scene=None):
        match type:
            case "Stone":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = RockData(texture=frames[10], ore=frames[0])
            case "Iron":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/iron.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = RockData(texture=frames[2], ore=frames[0])
            case _:
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=6
                        )
                self.data = RockData(texture=frames[10], ore=frames[0])
    
        super().__init__(self.data.texture)
        self.health = self.data.max_health
        self.type = type
        self.scene = scene

    def take_damage(self, amount):
        previous_health = self.health
        self.health = max(0, self.health - amount)
        if self.health != previous_health:
            print(f"Rock health: {self.health}")

        if self.health <= 0:
            self._destroy()

    def _destroy(self) -> None:
        ore_data = OreData(texture=self.data.ore, Name=f"{self.type.lower()}_ore")
        ore = Ore(self.position, ore_data)
        self.scene.add_sprite("Ore", ore)
        self._ore_animation(ore)
        self.remove_from_sprite_lists()

    def _ore_animation(self, ore) -> None:
        ore.horizontal_tween = ease_value(
            ore.center_x,
            ore.center_x + choice((-15, 15)),
            time=0.5,
        )
        
        ore.move_tween = ease_value(
            ore.center_y,
            ore.center_y + 16,
            time=0.25,
            ease_function=ease_out,
        )

        ore.next_move_tween = ease_value(
            ore.center_y + 16,
            ore.center_y,
            time=0.25,
            ease_function=ease_in,
        )

```

```python title=ore.py hl=12,15-18
import arcade
from arcade.easing import ease_update
from resources import OreData

class Ore(arcade.Sprite):
    def __init__(self, position, data: OreData):
        super().__init__(data.texture)
        self.position = position
        self.ore_data = data
        self.move_tween = None
        self.next_move_tween = None
        self.horizontal_tween = None

    def update(self, delta_time=1 / 60, *args, **kwargs):
        if self.horizontal_tween is not None:
            done, self.center_x = ease_update(self.horizontal_tween, delta_time)
            if done:
                self.horizontal_tween = None
        if self.move_tween is not None:
            done, self.center_y = ease_update(self.move_tween, delta_time)
            if done:
                self.move_tween = self.next_move_tween
                self.next_move_tween = None

```

```python title=game.py hl=55-71
import arcade

from player import Player
from rock import Rock
from game_camera import GameCamera, VIEW_WIDTH, VIEW_HEIGHT

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.BLACK
        self.scene = arcade.Scene()
        self.camera = GameCamera()

        self.rock1 = Rock(type="Stone", scene=self.scene)
        self.rock1.position = (VIEW_WIDTH/2 + 50, VIEW_HEIGHT/2)
        self.scene.add_sprite("Rock", self.rock1)

        self.rock2 = Rock(type="Iron", scene=self.scene)
        self.rock2.position = (VIEW_WIDTH/2 + 50, VIEW_HEIGHT/2 + 20)
        self.scene.add_sprite("Rock", self.rock2)
        self.scene.add_sprite_list("Ore")

        self.player = Player()
        self.player.position = (VIEW_WIDTH/2, VIEW_HEIGHT/2)
        self.scene.add_sprite("Player", self.player)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, [self.scene["Rock"], self.scene["Ore"]]
        )

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw(pixelated=True)
        self.scene.draw_hit_boxes(
            color=arcade.color.YELLOW,
            line_thickness=1,
        )
        if self.player.pickaxe_active:
            arcade.draw_polygon_outline(
                self.player.pickaxe_hitbox.hit_box.get_adjusted_points(),
                arcade.color.RED,
                1,
            )

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.camera.resize()

    def on_update(self, delta_time):
        self.scene["Ore"].update(delta_time)
        # Animated drops can overlap the player before physics moves them apart.
        overlapping_ores = arcade.check_for_collision_with_list(
            self.player, self.scene["Ore"]
        )
        for ore in overlapping_ores:
            if self.player.add_ore(ore.ore_data):
                ore.remove_from_sprite_lists()
        # The physics engine moves the player and resolves rock and ore collisions.
        collisions = self.physics_engine.update()
        for sprite in collisions:
            if sprite in self.scene["Ore"]:
                if self.player.add_ore(sprite.ore_data):
                    sprite.remove_from_sprite_lists()
        self.player.on_update(delta_time)
        self.player.hit_rocks(self.scene["Rock"])

    def on_key_press(self, key, key_modifiers):
        self.player.on_key_press(key, key_modifiers)

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

![[20260928-2202-30.1551893.mp4]]

#### Rock Hit Flash Effect
This is kind of an interesting effect where we show a white flash for 0.1 sec if the player hits a rock before it is destroyed.

```python title=rock.py hl=10-11,42-47,49-54,60-64
import arcade
from random import choice
from pathlib import Path
from PIL import Image

from ore import Ore
from resources import RockData, OreData
from arcade.easing import ease_value, ease_out, ease_in

FLASH_COLOR = arcade.color.WHITE
FLASH_DURATION = 0.1

class Rock(arcade.Sprite):
    def __init__(self, type="Stone", scene=None):
        match type:
            case "Stone":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = RockData(texture=frames[10], ore=frames[0])
            case "Iron":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/iron.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = RockData(texture=frames[2], ore=frames[0])
            case _:
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=6
                        )
                self.data = RockData(texture=frames[10], ore=frames[0])
    
        super().__init__(self.data.texture)
        self.health = self.data.max_health
        self.type = type
        self.scene = scene
        self._normal_color = self.color
        self._flash_remaining = 0.0
        # Sprite colors multiply the texture; a white silhouette makes white visible.
        flash_image = Image.new("RGBA", self.texture.image.size, "white")
        flash_image.putalpha(self.texture.image.getchannel("A"))
        self._flash_texture = arcade.Texture(flash_image)

    def update(self, delta_time=1 / 60, *args, **kwargs):
        if self._flash_remaining > 0:
            self._flash_remaining = max(0.0, self._flash_remaining - delta_time)
            if self._flash_remaining == 0:
                self.texture = self.data.texture
                self.color = self._normal_color

    def take_damage(self, amount):
        previous_health = self.health
        self.health = max(0, self.health - amount)
        if self.health != previous_health:
            if self._flash_remaining == 0:
                self._normal_color = self.color
            self.texture = self._flash_texture
            self.color = FLASH_COLOR
            self._flash_remaining = FLASH_DURATION

        if self.health <= 0:
            self._destroy()

    def _destroy(self) -> None:
        ore_data = OreData(texture=self.data.ore, Name=f"{self.type.lower()}_ore")
        ore = Ore(self.position, ore_data)
        self.scene.add_sprite("Ore", ore)
        self._ore_animation(ore)
        self.remove_from_sprite_lists()

    def _ore_animation(self, ore) -> None:
        ore.horizontal_tween = ease_value(
            ore.center_x,
            ore.center_x + choice((-15, 15)),
            time=0.5,
        )
        ore.move_tween = ease_value(
            ore.center_y,
            ore.center_y + 16,
            time=0.25,
            ease_function=ease_out,
        )

        ore.next_move_tween = ease_value(
            ore.center_y + 16,
            ore.center_y,
            time=0.25,
            ease_function=ease_in,
        )

```

```python title=game.py hl=4
...

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
        # The physics engine moves the player and resolves rock and ore collisions.
        collisions = self.physics_engine.update()
        for sprite in collisions:
            if sprite in self.scene["Ore"]:
                if self.player.add_ore(sprite.ore_data):
                    sprite.remove_from_sprite_lists()
        self.player.on_update(delta_time)
        self.player.hit_rocks(self.scene["Rock"])

...
```

![[20260928-2212-32.8578367.mp4]]

#### Rock Hit Sound Effect

Sound file: assets/audio/pickaxe_hit.ogg

```python title=rock.py hl=14,17-20,66
import arcade
from random import choice
from pathlib import Path
from PIL import Image

from ore import Ore
from resources import RockData, OreData
from arcade.easing import ease_value, ease_out, ease_in

FLASH_COLOR = arcade.color.WHITE
FLASH_DURATION = 0.1

class Rock(arcade.Sprite):
    _hit_sound = None

    def __init__(self, type="Stone", scene=None):
        if Rock._hit_sound is None:
            Rock._hit_sound = arcade.load_sound(
                Path(__file__).resolve().parent / "assets/audio/pickaxe_hit.ogg"
            )
        match type:
            case "Stone":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = RockData(texture=frames[10], ore=frames[0])
            case "Iron":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/iron.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = RockData(texture=frames[2], ore=frames[0])
            case _:
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=6
                        )
                self.data = RockData(texture=frames[10], ore=frames[0])
    
        super().__init__(self.data.texture)
        self.health = self.data.max_health
        self.type = type
        self.scene = scene
        self._normal_color = self.color
        self._flash_remaining = 0.0
        # Sprite colors multiply the texture; a white silhouette makes white visible.
        flash_image = Image.new("RGBA", self.texture.image.size, "white")
        flash_image.putalpha(self.texture.image.getchannel("A"))
        self._flash_texture = arcade.Texture(flash_image)

    def update(self, delta_time=1 / 60, *args, **kwargs):
        if self._flash_remaining > 0:
            self._flash_remaining = max(0.0, self._flash_remaining - delta_time)
            if self._flash_remaining == 0:
                self.texture = self.data.texture
                self.color = self._normal_color

    def take_damage(self, amount):
        previous_health = self.health
        self.health = max(0, self.health - amount)
        if self.health != previous_health:
            arcade.play_sound(Rock._hit_sound)
            if self._flash_remaining == 0:
                self._normal_color = self.color
            self.texture = self._flash_texture
            self.color = FLASH_COLOR
            self._flash_remaining = FLASH_DURATION

        if self.health <= 0:
            self._destroy()

    def _destroy(self) -> None:
        ore_data = OreData(texture=self.data.ore, Name=f"{self.type.lower()}_ore")
        ore = Ore(self.position, ore_data)
        self.scene.add_sprite("Ore", ore)
        self._ore_animation(ore)
        self.remove_from_sprite_lists()

    def _ore_animation(self, ore) -> None:
        ore.horizontal_tween = ease_value(
            ore.center_x,
            ore.center_x + choice((-15, 15)),
            time=0.5,
        )
        ore.move_tween = ease_value(
            ore.center_y,
            ore.center_y + 16,
            time=0.25,
            ease_function=ease_out,
        )

        ore.next_move_tween = ease_value(
            ore.center_y + 16,
            ore.center_y,
            time=0.25,
            ease_function=ease_in,
        )

```

#### Rock Destroyed Sound Effect

Sound file: assets/audio/rock_breaking.wav

I also lowered the volume on both sound effects so they are more subtle.

```python title=game.py hl=12-13,73,88
import arcade
from random import choice
from pathlib import Path
from PIL import Image

from ore import Ore
from resources import RockData, OreData
from arcade.easing import ease_value, ease_out, ease_in

FLASH_COLOR = arcade.color.WHITE
FLASH_DURATION = 0.1
HIT_SOUND_VOLUME = 0.2
BREAK_SOUND_VOLUME = 0.2

class Rock(arcade.Sprite):
    _hit_sound = None
    _break_sound = None

    def __init__(self, type="Stone", scene=None):
        if Rock._hit_sound is None:
            Rock._hit_sound = arcade.load_sound(
                Path(__file__).resolve().parent / "assets/audio/pickaxe_hit.ogg"
            )
        if Rock._break_sound is None:
            Rock._break_sound = arcade.load_sound(
                Path(__file__).resolve().parent / "assets/audio/rock_breaking.wav"
            )
        match type:
            case "Stone":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = RockData(texture=frames[10], ore=frames[0])
            case "Iron":
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/iron.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=12
                        )
                self.data = RockData(texture=frames[2], ore=frames[0])
            case _:
                asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/ores/stone.png"
                sprite_sheet = arcade.load_spritesheet(asset_path)
                frames = sprite_sheet.get_texture_grid(
                            size=(16, 16), columns=3, count=6
                        )
                self.data = RockData(texture=frames[10], ore=frames[0])
    
        super().__init__(self.data.texture)
        self.health = self.data.max_health
        self.type = type
        self.scene = scene
        self._normal_color = self.color
        self._flash_remaining = 0.0
        # Sprite colors multiply the texture; a white silhouette makes white visible.
        flash_image = Image.new("RGBA", self.texture.image.size, "white")
        flash_image.putalpha(self.texture.image.getchannel("A"))
        self._flash_texture = arcade.Texture(flash_image)

    def update(self, delta_time=1 / 60, *args, **kwargs):
        if self._flash_remaining > 0:
            self._flash_remaining = max(0.0, self._flash_remaining - delta_time)
            if self._flash_remaining == 0:
                self.texture = self.data.texture
                self.color = self._normal_color

    def take_damage(self, amount):
        previous_health = self.health
        self.health = max(0, self.health - amount)
        if self.health != previous_health:
            arcade.play_sound(Rock._hit_sound, volume=HIT_SOUND_VOLUME)
            if self._flash_remaining == 0:
                self._normal_color = self.color
            self.texture = self._flash_texture
            self.color = FLASH_COLOR
            self._flash_remaining = FLASH_DURATION

        if self.health <= 0:
            self._destroy()

    def _destroy(self) -> None:
        ore_data = OreData(texture=self.data.ore, Name=f"{self.type.lower()}_ore")
        ore = Ore(self.position, ore_data)
        self.scene.add_sprite("Ore", ore)
        self._ore_animation(ore)
        arcade.play_sound(Rock._break_sound, volume=BREAK_SOUND_VOLUME)       
        self.remove_from_sprite_lists()

    def _ore_animation(self, ore) -> None:
        ore.horizontal_tween = ease_value(
            ore.center_x,
            ore.center_x + choice((-15, 15)),
            time=0.5,
        )
        ore.move_tween = ease_value(
            ore.center_y,
            ore.center_y + 16,
            time=0.25,
            ease_function=ease_out,
        )

        ore.next_move_tween = ease_value(
            ore.center_y + 16,
            ore.center_y,
            time=0.25,
            ease_function=ease_in,
        )

```

