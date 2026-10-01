Introduction and Character Creation
-  [x] Introduction
-  [x] Creating the Player
-  [x] Player Movement
-  [x] Player State Enumeration
-  [x] Adding Animations

### Introduction/Project Setup
---
IDE: VSCode
Language: Python 3.14
Game Library: Arcade 3.3.3
Project Name: Mining Roguelite Tutorial
Project Directory: `C:\arcade_tutorials\mining_roguelite_tutorial`
GitHub Repository: TBD
AI Assistant: ChatGPT Codex

Game Assets: `C:\Asset_Libraries\Coding with Russ\all_assets`

![[Pasted image 20260927142055.png]]

```Output title=Credits for Assets Used.txt
### Images:

- Cute Fantasy RPG - this is used for the character: https://kenmi-art.itch.io/cute-fantasy-rpg
- Hana caraka - for the main tileset and ores: https://otterisk.itch.io/hana-caraka-dungeon-mining
- DialogueBoxSimple.png from Ninja pack: https://pixel-boy.itch.io/ninja-adventure-asset-pack


### Sound effects:

- Pickaxe: https://freesound.org/people/NoisyRedFox/sounds/760566/
- Rock breaking: https://freesound.org/people/newlocknew/sounds/631485/

### Font:

- Font: https://managore.itch.io/m5x7
  
```

### Create Player
---
Create an Arcade window for testing the player.

![[Pasted image 20260927142630.png]]

```python title=game.py
import arcade

WINDOW_WIDTH = 640*1.5
WINDOW_HEIGHT = 360*1.5
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.BLACK
        self.scene = arcade.Scene()

    def on_draw(self):
        self.clear()
        self.scene.draw()

    def on_update(self, delta_time):
        self.scene.update(delta_time)

def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.center_window()

    game = GameView()
    window.show_view(game)
    arcade.run()  # Runs the Arcade game loop

if __name__ == "__main__":
    main()
    
```

Player spritesheet evaluation:
![[Player.png]]

Image size: 192x320
Image frames: 10x6 frames
Frame size: 32x32 px


![[Pasted image 20260927143655.png]]
```python title=player.py
from pathlib import Path

import arcade

class Player(arcade.Sprite):
    def __init__(self):
        asset_path = Path(__file__).resolve().parent / "assets/player/Player.png"
        sprite_sheet = arcade.load_spritesheet(asset_path)
        # The sheet has 6 columns and 10 rows of 32x32 frames.
        # The first frame starts at sheet coordinates (0, 0).
        first_frame = sprite_sheet.get_texture_grid(
            size=(32, 32), columns=6, count=1
        )[0]
        super().__init__(first_frame)

```

```python title=game.py hl=3,16-18
import arcade

from player import Player

WINDOW_WIDTH = 640*1.5
WINDOW_HEIGHT = 360*1.5
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.BLACK
        self.scene = arcade.Scene()

        self.player = Player()
        self.player.position = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
        self.scene.add_sprite("Player", self.player)

    def on_draw(self):
        self.clear()
        self.scene.draw(pixelated=True)

    def on_update(self, delta_time):
        self.scene.update(delta_time)

def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.center_window()

    game = GameView()
    window.show_view(game)
    arcade.run()  # Runs the Arcade game loop

if __name__ == "__main__":
    main()
    
```

### Game Camera
---
A 32x32 px player is too small for a large window. Create a game camera with a zoomed in view port of 320x180 px.

![[Pasted image 20260927144312.png|800]]

```python title=game_camera.py
import arcade

VIEW_WIDTH = 320
VIEW_HEIGHT = 180


class GameCamera(arcade.Camera2D):
    def __init__(self):
        super().__init__(
            projection=arcade.LRBT(
                -VIEW_WIDTH / 2, VIEW_WIDTH / 2,
                -VIEW_HEIGHT / 2, VIEW_HEIGHT / 2,
            ),
            position=(VIEW_WIDTH / 2, VIEW_HEIGHT / 2),
        )

    def resize(self):
        self.match_window(projection=False)

```

```python title=game.py hl=4,16,19,24,29
import arcade

from player import Player
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

def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.center_window()

    game = GameView()
    window.show_view(game)
    arcade.run()  # Runs the Arcade game loop

if __name__ == "__main__":
    main()
    

```

### Player Movement
---
Keyboard events are handled in the Arcade Game View class but we will delegate those functions to the player.
For this 2D top-down game, we will create an 4-way controller that moves the player left, right, up, or down.
Lets normalize the player diagonal speed so he moves at a constant speed in all 8 directions including up-left, up-right, down-left, and down-right.

```python title=player.py hl=4-5,18-31,33-37
import arcade
from pathlib import Path

PLAYER_SPEED = 3
DIAGONAL_SPEED = PLAYER_SPEED / 1.4142  # Diagonal Speed = Player Speed / sqrt(2)

class Player(arcade.Sprite):
    def __init__(self):
        asset_path = Path(__file__).resolve().parent / "assets/player/Player.png"
        sprite_sheet = arcade.load_spritesheet(asset_path)
        # The sheet has 6 columns and 10 rows of 32x32 frames.
        # The first frame starts at sheet coordinates (0, 0).
        first_frame = sprite_sheet.get_texture_grid(
            size=(32, 32), columns=6, count=1
        )[0]
        super().__init__(first_frame)

    def on_key_press(self, key, key_modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.change_x -= PLAYER_SPEED
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.change_x += PLAYER_SPEED
        elif key in (arcade.key.W, arcade.key.UP):
            self.change_y += PLAYER_SPEED
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.change_y -= PLAYER_SPEED

        # Normalize diagonal movement speed so the player speed is constant in all directions
        if self.change_x != 0 and self.change_y != 0:
            self.change_x = DIAGONAL_SPEED if self.change_x > 0 else -DIAGONAL_SPEED
            self.change_y = DIAGONAL_SPEED if self.change_y > 0 else -DIAGONAL_SPEED

    def on_key_release(self, key, key_modifiers):
        if key in (arcade.key.A, arcade.key.LEFT, arcade.key.D, arcade.key.RIGHT):
            self.change_x = 0
        elif key in (arcade.key.W, arcade.key.UP, arcade.key.S, arcade.key.DOWN):
            self.change_y = 0

```

```python title=game.py hl=34-38
import arcade

from player import Player
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

### Player Direction & Idle Animation
---
The Player.png file has the following animations:

Idle-Down: 0-5
Idle-Right: 6-11
Idle-Up: 12-17

Walk-Down: 18-23
Walk-Right: 24-29
Walk-Up: 30-35

Attack-Down: 36-39
Attack-Right: 42-45
Attack-Up: 48-51

Death: 54-57

In the player class, lets extract the animation frames for each animation.

```python title=player.py hl=12-32
import arcade
from pathlib import Path

PLAYER_SPEED = 3
DIAGONAL_SPEED = PLAYER_SPEED / 1.4142  # Diagonal Speed = Player Speed / sqrt(2)

class Player(arcade.Sprite):
    def __init__(self):
        asset_path = Path(__file__).resolve().parent / "assets/player/Player.png"
        sprite_sheet = arcade.load_spritesheet(asset_path)
        # The sheet has 6 columns and 10 rows of 32x32 frames.
        frames = sprite_sheet.get_texture_grid(
            size=(32, 32), columns=6, count=60
        )
        super().__init__(frames[0])

        self.idle_down = frames[0:6]
        self.idle_right = frames[6:12]
        self.idle_up = frames[12:18]
        self.idle_left = [frame.flip_left_right() for frame in self.idle_right]

        self.walk_down = frames[18:24]
        self.walk_right = frames[24:30]
        self.walk_up = frames[30:36]
        self.walk_left = [frame.flip_left_right() for frame in self.walk_right]

        self.attack_down = frames[36:40]
        self.attack_right = frames[42:46]
        self.attack_up = frames[48:52]
        self.attack_left = [frame.flip_left_right() for frame in self.attack_right]

        self.death = frames[54:58]

    def on_key_press(self, key, key_modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.change_x -= PLAYER_SPEED
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.change_x += PLAYER_SPEED
        elif key in (arcade.key.W, arcade.key.UP):
            self.change_y += PLAYER_SPEED
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.change_y -= PLAYER_SPEED

        # Normalize diagonal movement speed so the player speed is constant in all directions
        if self.change_x != 0 and self.change_y != 0:
            self.change_x = DIAGONAL_SPEED if self.change_x > 0 else -DIAGONAL_SPEED
            self.change_y = DIAGONAL_SPEED if self.change_y > 0 else -DIAGONAL_SPEED

    def on_key_release(self, key, key_modifiers):
        if key in (arcade.key.A, arcade.key.LEFT, arcade.key.D, arcade.key.RIGHT):
            self.change_x = 0
        elif key in (arcade.key.W, arcade.key.UP, arcade.key.S, arcade.key.DOWN):
            self.change_y = 0

```

Now, add an animation player class that I developed on an earlier project:

```python title=animation_player.py
import arcade

UPDATES_PER_FRAME = 5

class AnimationPlayer:
    def __init__(self):
        self.cur_texture = 0

    def update_animation(self, texture_list) -> arcade.Texture:
        # Assume this function is called in the on_update() method and updates every frame
        self.cur_texture += 1
        frame = (self.cur_texture // UPDATES_PER_FRAME) % len(texture_list)
        texture = texture_list[frame]

        return texture

```

Add an enumeration for Player Direction and a dictionary for the animations:

```python title=python.py hl=3,5,10-14,43-57,59-60,62-64,69,72,75,78
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

class Player(arcade.Sprite):
    def __init__(self):
        asset_path = Path(__file__).resolve().parent / "assets/player/Player.png"
        sprite_sheet = arcade.load_spritesheet(asset_path)
        # The sheet has 6 columns and 10 rows of 32x32 frames for a total of 60 frames
        frames = sprite_sheet.get_texture_grid(
            size=(32, 32), columns=6, count=60
        )
        super().__init__(frames[0])

        self.idle_down = frames[0:6]
        self.idle_right = frames[6:12]
        self.idle_up = frames[12:18]
        self.idle_left = [frame.flip_left_right() for frame in self.idle_right]

        self.walk_down = frames[18:24]
        self.walk_right = frames[24:30]
        self.walk_up = frames[30:36]
        self.walk_left = [frame.flip_left_right() for frame in self.walk_right]

        self.attack_down = frames[36:40]
        self.attack_right = frames[42:46]
        self.attack_up = frames[48:52]
        self.attack_left = [frame.flip_left_right() for frame in self.attack_right]

        self.death = frames[54:58]

        self.animations = {
            "idle_down": self.idle_down,
            "idle_right": self.idle_right,
            "idle_up": self.idle_up,
            "idle_left": self.idle_left,
            "walk_down": self.walk_down,
            "walk_right": self.walk_right,
            "walk_up": self.walk_up,
            "walk_left": self.walk_left,
            "attack_down": self.attack_down,
            "attack_right": self.attack_right,
            "attack_up": self.attack_up,
            "attack_left": self.attack_left,
            "death": self.death,
        }

        self.animation_player = AnimationPlayer()
        self.current_direction = Dir.DOWN

    def on_update(self, delta_time):
        textures = self.animations[f"idle_{self.current_direction.name.lower()}"]
        self.texture = self.animation_player.update_animation(textures)

    def on_key_press(self, key, key_modifiers):
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

        # Normalize diagonal movement speed so the player speed is constant in all directions
        if self.change_x != 0 and self.change_y != 0:
            self.change_x = DIAGONAL_SPEED if self.change_x > 0 else -DIAGONAL_SPEED
            self.change_y = DIAGONAL_SPEED if self.change_y > 0 else -DIAGONAL_SPEED

    def on_key_release(self, key, key_modifiers):
        if key in (arcade.key.A, arcade.key.LEFT, arcade.key.D, arcade.key.RIGHT):
            self.change_x = 0
        elif key in (arcade.key.W, arcade.key.UP, arcade.key.S, arcade.key.DOWN):
            self.change_y = 0

```

```python title=game.py hl=33
import arcade

from player import Player
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

This deserves a short video:

<video src=20260927-2150-56.2978498.mp4 controls width="1000"></video>

### Player State Enumeration
---
Create a player enumeration that defines all of the player states for this game. This is not a full state machine but a small enumeration system that I find works well in Arcade.

<video src=20260928-1210-33.2269330.mp4 controls width="1000"></video>

```python title=player.py hl=16-20,47-48,63-64,69,71-87,90-93,95-98,112-115,125,128
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
    WALK = auto()
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

        self.idle_down = frames[0:6]
        self.idle_right = frames[6:12]
        self.idle_up = frames[12:18]
        self.idle_left = [frame.flip_left_right() for frame in self.idle_right]

        self.walk_down = frames[18:24]
        self.walk_right = frames[24:30]
        self.walk_up = frames[30:36]
        self.walk_left = [frame.flip_left_right() for frame in self.walk_right]

        self.attack_down = frames[36:40]
        self.attack_right = frames[42:46]
        self.attack_up = frames[48:52]
        self.attack_left = [frame.flip_left_right() for frame in self.attack_right]

        self.death_right = frames[54:58]
        self.death_left = [frame.flip_left_right() for frame in self.death_right]

        self.animations = {
            "idle_down": self.idle_down,
            "idle_right": self.idle_right,
            "idle_up": self.idle_up,
            "idle_left": self.idle_left,
            "walk_down": self.walk_down,
            "walk_right": self.walk_right,
            "walk_up": self.walk_up,
            "walk_left": self.walk_left,
            "attack_down": self.attack_down,
            "attack_right": self.attack_right,
            "attack_up": self.attack_up,
            "attack_left": self.attack_left,
            "death_right": self.death_right,
            "death_left": self.death_left,
        }

        self.animation_player = AnimationPlayer()
        self.current_direction = Dir.DOWN
        self.current_state = State.IDLE

    def on_update(self, delta_time):
        match self.current_state:
            case State.IDLE:
                textures = self.animations[f"idle_{self.current_direction.name.lower()}"]
                self.texture = self.animation_player.update_animation(textures)
            case State.WALK:
                textures = self.animations[f"walk_{self.current_direction.name.lower()}"]
                self.texture = self.animation_player.update_animation(textures)
            case State.ATTACK:
                textures = self.animations[f"attack_{self.current_direction.name.lower()}"]
                self.texture = self.animation_player.update_animation(textures, one_shot=True)
            case State.DEATH:
                textures = self.animations[f"death_{self.current_direction.name.lower()}"]
                self.texture = self.animation_player.update_animation(textures, one_shot=True)
            case _:
                textures = self.animations[f"idle_{self.current_direction.name.lower()}"]
                self.texture = self.animation_player.update_animation(textures)                     

    def on_key_press(self, key, key_modifiers):
        if key in (arcade.key.LCTRL, arcade.key.RCTRL):
            self.animation_player.reset()
            self.current_state = State.ATTACK
            return

        if key == arcade.key.SPACE:
            self.animation_player.reset()
            self.current_state = State.DEATH
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

        self.current_state = State.WALK

        # Normalize diagonal movement speed so the player speed is constant in all directions
        if self.change_x != 0 and self.change_y != 0:
            self.change_x = DIAGONAL_SPEED if self.change_x > 0 else -DIAGONAL_SPEED
            self.change_y = DIAGONAL_SPEED if self.change_y > 0 else -DIAGONAL_SPEED

    def on_key_release(self, key, key_modifiers):
        if key in (arcade.key.A, arcade.key.LEFT, arcade.key.D, arcade.key.RIGHT):
            self.change_x = 0
            self.current_state = State.IDLE
        elif key in (arcade.key.W, arcade.key.UP, arcade.key.S, arcade.key.DOWN):
            self.change_y = 0
            self.current_state = State.IDLE

```