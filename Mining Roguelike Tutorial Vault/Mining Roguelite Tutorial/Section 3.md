Level Creation
-  [x] Create Base Level
-  [x] Player Camera
-  [x] Set Map Background Color
-  [x] Player Spawn Marker
-  [x] Railway Props
-  [x] Level Collision
-  [x] Procedural Rock Generation
-  [x] More Rock Types
-  [x] Create Rocks based on Depth and Rarity
-  [x] Ladder Class
-  [x] Ladder chance and one ladder/level
-  [x] Level Manager
-  [x] Multiple Maps
-  [x] Random Level Maps
### Create Base Level
---

Godot Map - Using Terrain Set
![[Pasted image 20260929061533.png]]

Tiled Project-Map-Tileset

Ground - dark.png
![[Ground - dark.png|400]]

Tiled terrain set
![[Pasted image 20260929065735.png]]

`base_map.json`
![[Pasted image 20260929070017.png]]


![[Pasted image 20260929065633.png|1000]]

```python title=level.py
import arcade
from pathlib import Path

class Level:
    def __init__(self):
        map_path = Path(__file__).resolve().parent / "assets" / "maps" / "base_map.json"
        self.tile_map = arcade.load_tilemap(map_path)

```

```python title=game.py hl=4,17-18,20-22,26,30,35
import arcade

from player import Player
from level import Level
from rock import Rock
from game_camera import GameCamera

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.BLACK
        self.level = Level()
        self.scene = arcade.Scene.from_tilemap(self.level.tile_map)
        self.camera = GameCamera()
        tile_map = self.level.tile_map
        spawn_x = tile_map.width * tile_map.tile_width / 2
        spawn_y = tile_map.height * tile_map.tile_height / 2
        self.camera.position = (spawn_x, spawn_y)

        self.rock1 = Rock(type="Stone", scene=self.scene)
        self.rock1.position = (spawn_x + 50, spawn_y)
        self.scene.add_sprite("Rock", self.rock1)

        self.rock2 = Rock(type="Iron", scene=self.scene)
        self.rock2.position = (spawn_x + 50, spawn_y + 20)
        self.scene.add_sprite("Rock", self.rock2)
        self.scene.add_sprite_list("Ore")

        self.player = Player()
        self.player.position = (spawn_x, spawn_y)
        self.scene.add_sprite("Player", self.player)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, [self.scene["Rock"], self.scene["Ore"]]
        )

...
```

### Player Camera
---
To explore the level, we need the camera to follow the player within the level boundaries. We should probably limit the player's movement to within the level boundaries also.

![[Pasted image 20260929070750.png]]

```python title=level.py hl=11-20
import arcade
from pathlib import Path

class Level:
    def __init__(self):
        map_path = Path(__file__).resolve().parent / "assets" / "maps" / "base_map.json"
        self.tile_map = arcade.load_tilemap(map_path)
        self.width = self.tile_map.width * self.tile_map.tile_width
        self.height = self.tile_map.height * self.tile_map.tile_height

    def constrain_player(self, player):
        # Keep the player's movement hit box inside the map rectangle.
        if player.left < 0:
            player.left = 0
        elif player.right > self.width:
            player.right = self.width
        if player.bottom < 0:
            player.bottom = 0
        elif player.top > self.height:
            player.top = self.height

```

```python title=game_camera.py hl=20-30
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

    def follow(self, player, level):
        # Stop scrolling when the edge of the view reaches the map boundary.
        half_width = VIEW_WIDTH / 2
        half_height = VIEW_HEIGHT / 2
        x = max(half_width, min(player.center_x, level.width - half_width))
        y = max(half_height, min(player.center_y, level.height - half_height))
        if level.width < VIEW_WIDTH:
            x = level.width / 2
        if level.height < VIEW_HEIGHT:
            y = level.height / 2
        self.position = (x, y)

```

```python title=game.py hl=20-21,35-36,60,74,81
import arcade

from player import Player
from level import Level
from rock import Rock
from game_camera import GameCamera

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.BLACK
        self.level = Level()
        self.scene = arcade.Scene.from_tilemap(self.level.tile_map)
        self.camera = GameCamera()
        spawn_x = self.level.width / 2
        spawn_y = self.level.height / 2

        self.rock1 = Rock(type="Stone", scene=self.scene)
        self.rock1.position = (spawn_x + 50, spawn_y)
        self.scene.add_sprite("Rock", self.rock1)

        self.rock2 = Rock(type="Iron", scene=self.scene)
        self.rock2.position = (spawn_x + 50, spawn_y + 20)
        self.scene.add_sprite("Rock", self.rock2)
        self.scene.add_sprite_list("Ore")

        self.player = Player()
        self.player.position = (spawn_x, spawn_y)
        self.scene.add_sprite("Player", self.player)
        self.level.constrain_player(self.player)
        self.camera.follow(self.player, self.level)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, [self.scene["Rock"], self.scene["Ore"]]
        )

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

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.camera.resize()
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
        # The physics engine moves the player and resolves rock and ore collisions.
        collisions = self.physics_engine.update()
        self.level.constrain_player(self.player)
        for sprite in collisions:
            if sprite in self.scene["Ore"]:
                if self.player.add_ore(sprite.ore_data):
                    sprite.remove_from_sprite_lists()
        self.player.on_update(delta_time)
        self.player.hit_rocks(self.scene["Rock"])
        self.camera.follow(self.player, self.level)

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

### Set Map Background Color
---
This can be done two ways:
- Create a Background layer and draw a rectangle of dark tiles on it
- Set the Background Color in map settings using the Pick Screen Color option - Color = RGB(#333c3a)

```python title=game.py hl=15
from player import Player
from level import Level
from rock import Rock
from game_camera import GameCamera

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.level = Level()
        self.background_color = self.level.tile_map.background_color or arcade.color.BLACK
        self.scene = arcade.Scene.from_tilemap(self.level.tile_map)
        self.camera = GameCamera()
        spawn_x = self.level.width / 2
        spawn_y = self.level.height / 2
        
...
```

![[Pasted image 20260929072801.png|1000]]


### Player Spawn Marker
---
In Arcade Tiled map, create an Object Layer called Characters. Create a new tileset called `Characters.tsx `and add the player.png image to it so that each player image becomes a tile. Place the idle down image of the player at the spawn point using the insert tile image button. Add a custom property called Type and set it to "Player". Modify level.py to spawn the player at the marker position. This works better than placing a marker symbol since you can see the actual character in the Tiled map.

`Characters.tsx`
![[Pasted image 20260929074412.png]]

`base_map.json`
![[Pasted image 20260929074303.png]]


![[Pasted image 20260929074511.png|1000]]

Woohoo! We can now place the player in the Tiled map and spawn him in the game.

```python title=level.py hl=13-26
import arcade
from pathlib import Path

from player import Player

class Level:
    def __init__(self):
        map_path = Path(__file__).resolve().parent / "assets" / "maps" / "base_map.json"
        self.tile_map = arcade.load_tilemap(map_path)
        self.width = self.tile_map.width * self.tile_map.tile_width
        self.height = self.tile_map.height * self.tile_map.tile_height

    def spawn_player(self, scene):
        markers = [
            marker
            for marker in self.tile_map.sprite_lists.get("Characters", [])
            if marker.properties.get("Type") == "Player"
        ]
        if len(markers) != 1:
            raise ValueError("Characters must contain exactly one marker with Type = Player")

        player = Player()
        player.position = markers[0].position
        scene.remove_sprite_list_by_name("Characters")
        scene.add_sprite("Player", player)
        return player

    def constrain_player(self, player):
        # Keep the player's movement hit box inside the map rectangle.
        if player.left < 0:
            player.left = 0
        elif player.right > self.width:
            player.right = self.width
        if player.bottom < 0:
            player.bottom = 0
        elif player.top > self.height:
            player.top = self.height

```

```python title=game.py hl=31
import arcade

from level import Level
from rock import Rock
from game_camera import GameCamera

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.level = Level()
        self.background_color = self.level.tile_map.background_color or arcade.color.BLACK
        self.scene = arcade.Scene.from_tilemap(self.level.tile_map)
        self.camera = GameCamera()
        spawn_x = self.level.width / 2
        spawn_y = self.level.height / 2

        self.rock1 = Rock(type="Stone", scene=self.scene)
        self.rock1.position = (spawn_x + 50, spawn_y)
        self.scene.add_sprite("Rock", self.rock1)

        self.rock2 = Rock(type="Iron", scene=self.scene)
        self.rock2.position = (spawn_x + 50, spawn_y + 20)
        self.scene.add_sprite("Rock", self.rock2)
        self.scene.add_sprite_list("Ore")

        self.player = self.level.spawn_player(self.scene)
        self.level.constrain_player(self.player)
        self.camera.follow(self.player, self.level)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, [self.scene["Rock"], self.scene["Ore"]]
        )
        
...
```


### Railway Props
---
Godot reference image:
![[Pasted image 20260929075208.png]]

In Arcade create a new tileset using the railway props. Create a new layer called Props and place the layer below the Characters layer. Add the railway sections shown in the reference image.

`Railway.tsx`
![[Pasted image 20260929075757.png]]

`base_map.json`
![[Pasted image 20260929075844.png]]

![[Pasted image 20260929075707.png|1000]]

No change to the code required...

### Level Collision
---
Although custom colliders can be applied to tiles in a Tiled tileset, the Arcade way of handling colliders is to simply create a layer for colliders and draw boundary tiles around the edges of the map.

Since the images on the boundary tiles don't extend to the edge, we need to define a custom collider on all the edge tiles. Then we redraw the edge on the `Collision_Walls` layer which allows collision with the player.

![[Pasted image 20260929104611.png]]

This seems to work the best for this game.

![[Pasted image 20260929104816.png|1000]]

```python title=game.py hl=37
import arcade

from level import Level
from rock import Rock
from game_camera import GameCamera

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.level = Level()
        self.background_color = self.level.tile_map.background_color or arcade.color.BLACK
        self.scene = arcade.Scene.from_tilemap(self.level.tile_map)
        self.camera = GameCamera()
        spawn_x = self.level.width / 2
        spawn_y = self.level.height / 2

        self.rock1 = Rock(type="Stone", scene=self.scene)
        self.rock1.position = (spawn_x + 50, spawn_y)
        self.scene.add_sprite("Rock", self.rock1)

        self.rock2 = Rock(type="Iron", scene=self.scene)
        self.rock2.position = (spawn_x + 50, spawn_y + 20)
        self.scene.add_sprite("Rock", self.rock2)
        self.scene.add_sprite_list("Ore")

        self.player = self.level.spawn_player(self.scene)
        self.level.constrain_player(self.player)
        self.camera.follow(self.player, self.level)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            [self.scene["Collision_Walls"], self.scene["Rock"], self.scene["Ore"]],
        )
```

### Procedural Rock Generation
---
![[Pasted image 20260929113046.png|1000]]

The procedural algorithm fills 40% of the available solid ground tiles with rocks.

```python title=level.py hl=3,6,8,43-76
import arcade
from pathlib import Path
from random import shuffle

from player import Player
from rock import Rock

FILL_PERCENTAGE = 0.40

class Level:
    def __init__(self):
        map_path = Path(__file__).resolve().parent / "assets" / "maps" / "base_map.json"
        self.tile_map = arcade.load_tilemap(map_path)
        self.width = self.tile_map.width * self.tile_map.tile_width
        self.height = self.tile_map.height * self.tile_map.tile_height

    def spawn_player(self, scene):
        markers = [
            marker
            for marker in self.tile_map.sprite_lists.get("Characters", [])
            if marker.properties.get("Type") == "Player"
        ]
        if len(markers) != 1:
            raise ValueError("Characters must contain exactly one marker with Type = Player")

        player = Player()
        player.position = markers[0].position
        scene.remove_sprite_list_by_name("Characters")
        scene.add_sprite("Player", player)
        return player

    def constrain_player(self, player):
        # Keep the player's movement hit box inside the map rectangle.
        if player.left < 0:
            player.left = 0
        elif player.right > self.width:
            player.right = self.width
        if player.bottom < 0:
            player.bottom = 0
        elif player.top > self.height:
            player.top = self.height

    # Procedural rock generation
    def generate_rocks(self, scene):
        # Clear the Rock spritelist
        if "Rock" not in scene:
            scene.add_sprite_list("Rock")
        scene["Rock"].clear()

        # Avoid props and spawned characters
        blockers = list(scene["Collision_Walls"]) + list(scene["Props"])
        # Keep spawn markers reserved even after spawn_player removes their layer.
        blockers.extend(self.tile_map.sprite_lists.get("Characters", []))
        for layer in ("Characters", "Player"):
            if layer in scene:
                blockers.extend(scene[layer])

        # Find all available sprite cells (positions)
        available_positions = []
        for tile in scene["Ground"]:
            # Use full sprite rectangles so partially occupied tiles stay clear.
            occupied = any(
                abs(tile.center_x - blocker.center_x) < (tile.width + blocker.width) / 2
                and abs(tile.center_y - blocker.center_y) < (tile.height + blocker.height) / 2
                for blocker in blockers
            )
            if not occupied:
                available_positions.append(tile.position)

        # Randomize the available positions & fill 40% with rocks
        shuffle(available_positions)
        num_rocks = int(len(available_positions) * FILL_PERCENTAGE)
        for position in available_positions[:num_rocks]:
            rock = Rock(scene=scene)
            rock.position = position
            scene.add_sprite("Rock", rock)

```

### More Rock Types
---
![[Pasted image 20260929131438.png|1000]]

```python type=rock.py hl=28-77
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
                filename = "Ores/stone.png"
                rock_frame = 10
                max_health = 3
                rarity = 50
                min_depth = 1
                ore_value = 10
            case "Iron":
                filename = "Ores/iron.png"
                rock_frame = 2
                max_health = 4
                rarity = 40
                min_depth = 2
                ore_value = 20
            case "Gold":
                filename = "Ores/gold.png"
                rock_frame = 2
                max_health = 6
                rarity = 5
                min_depth = 6
                ore_value = 100
            case "Silver":
                filename = "Ores/silver.png"
                rock_frame = 2
                max_health = 4
                rarity = 10
                min_depth = 4
                ore_value = 50
            case "Diamond":
                filename = "Gems/diamond.png"
                rock_frame = 2
                max_health = 10
                rarity = 1
                min_depth = 8
                ore_value = 250
            case "Amethyst":
                filename = "Gems/amethyst.png"
                rock_frame = 2
                max_health = 5
                rarity = 15
                min_depth = 4
                ore_value = 150
            case _:
                filename = "Ores/stone.png"
                rock_frame = 10
                max_health = 3
                rarity = 50
                min_depth = 1
                ore_value = 10

        asset_path = Path(__file__).resolve().parent / "assets/mine_tiles/Ore n Gems/" / filename
        sprite_sheet = arcade.load_spritesheet(asset_path)
        frames = sprite_sheet.get_texture_grid(size=(16, 16), columns=3, count=12)
        self.data = RockData(
            texture=frames[rock_frame],
            ore=frames[0],
            max_health=max_health,
            rarity=rarity,
            min_depth=min_depth,
        )
    
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

```python title=level.py hl=74
import arcade
from pathlib import Path
from random import choice, shuffle

from player import Player
from rock import Rock

FILL_PERCENTAGE = 0.40

class Level:
    def __init__(self):
        map_path = Path(__file__).resolve().parent / "assets" / "maps" / "base_map.json"
        self.tile_map = arcade.load_tilemap(map_path)
        self.width = self.tile_map.width * self.tile_map.tile_width
        self.height = self.tile_map.height * self.tile_map.tile_height

    def spawn_player(self, scene):
        markers = [
            marker
            for marker in self.tile_map.sprite_lists.get("Characters", [])
            if marker.properties.get("Type") == "Player"
        ]
        if len(markers) != 1:
            raise ValueError("Characters must contain exactly one marker with Type = Player")

        player = Player()
        player.position = markers[0].position
        scene.remove_sprite_list_by_name("Characters")
        scene.add_sprite("Player", player)
        return player

    def constrain_player(self, player):
        # Keep the player's movement hit box inside the map rectangle.
        if player.left < 0:
            player.left = 0
        elif player.right > self.width:
            player.right = self.width
        if player.bottom < 0:
            player.bottom = 0
        elif player.top > self.height:
            player.top = self.height

    # Procedural rock generation
    def generate_rocks(self, scene):
        # Clear the Rock spritelist
        if "Rock" not in scene:
            scene.add_sprite_list("Rock")
        scene["Rock"].clear()

        # Avoid props and spawned characters
        blockers = list(scene["Collision_Walls"]) + list(scene["Props"])
        # Keep spawn markers reserved even after spawn_player removes their layer.
        blockers.extend(self.tile_map.sprite_lists.get("Characters", []))
        for layer in ("Characters", "Player"):
            if layer in scene:
                blockers.extend(scene[layer])

        # Find all available sprite cells (positions)
        available_positions = []
        for tile in scene["Ground"]:
            # Use full sprite rectangles so partially occupied tiles stay clear.
            occupied = any(
                abs(tile.center_x - blocker.center_x) < (tile.width + blocker.width) / 2
                and abs(tile.center_y - blocker.center_y) < (tile.height + blocker.height) / 2
                for blocker in blockers
            )
            if not occupied:
                available_positions.append(tile.position)

        # Randomize the available positions & fill 40% with rocks
        shuffle(available_positions)
        num_rocks = int(len(available_positions) * FILL_PERCENTAGE)
        for position in available_positions[:num_rocks]:
            rock = Rock(type=choice(("Stone", "Iron", "Gold","Silver","Diamond","Amethyst")), scene=scene)
            rock.position = position
            scene.add_sprite("Rock", rock)

```

### Create Rocks based on Depth and Rarity
---
![[Pasted image 20260929133755.png|1000]]

```resources.py
import arcade
from dataclasses import dataclass

@dataclass(frozen=True)
class RockDefinition:
    filename: str
    rock_frame: int
    max_health: int
    rarity: int
    min_depth: int
    ore_value: int


ROCK_TYPES = {
    "Stone": RockDefinition(
        filename="Ores/stone.png", rock_frame=10,
        max_health=3, rarity=50, min_depth=1, ore_value=10,
    ),
    "Iron": RockDefinition(
        filename="Ores/iron.png", rock_frame=2,
        max_health=4, rarity=40, min_depth=2, ore_value=20,
    ),
    "Gold": RockDefinition(
        filename="Ores/gold.png", rock_frame=2,
        max_health=6, rarity=5, min_depth=6, ore_value=100,
    ),
    "Silver": RockDefinition(
        filename="Ores/silver.png", rock_frame=2,
        max_health=4, rarity=10, min_depth=4, ore_value=50,
    ),
    "Diamond": RockDefinition(
        filename="Gems/diamond.png", rock_frame=2,
        max_health=10, rarity=1, min_depth=8, ore_value=250,
    ),
    "Amethyst": RockDefinition(
        filename="Gems/amethyst.png", rock_frame=2,
        max_health=5, rarity=15, min_depth=4, ore_value=150,
    ),
}


@dataclass
class RockData:
    texture: arcade.Texture
    ore: arcade.Texture
    max_health: int = 3
    rarity: int = 50
    min_depth: int = 1
    ore_value: int = 10

@dataclass
class OreData:
    texture: arcade.Texture
    Name: str = "stone_ore"
    value: int = 10

```

```python title=level.py hl=76-79
import arcade
from pathlib import Path
from random import choice, shuffle

from player import Player
from rock import Rock
from resources import ROCK_TYPES

FILL_PERCENTAGE = 0.40

class Level:
    def __init__(self):
        map_path = Path(__file__).resolve().parent / "assets" / "maps" / "base_map.json"
        self.tile_map = arcade.load_tilemap(map_path)
        self.width = self.tile_map.width * self.tile_map.tile_width
        self.height = self.tile_map.height * self.tile_map.tile_height
        self.current_depth = 1

    def spawn_player(self, scene):
        markers = [
            marker
            for marker in self.tile_map.sprite_lists.get("Characters", [])
            if marker.properties.get("Type") == "Player"
        ]
        if len(markers) != 1:
            raise ValueError("Characters must contain exactly one marker with Type = Player")

        player = Player()
        player.position = markers[0].position
        scene.remove_sprite_list_by_name("Characters")
        scene.add_sprite("Player", player)
        return player

    def constrain_player(self, player):
        # Keep the player's movement hit box inside the map rectangle.
        if player.left < 0:
            player.left = 0
        elif player.right > self.width:
            player.right = self.width
        if player.bottom < 0:
            player.bottom = 0
        elif player.top > self.height:
            player.top = self.height

    # Procedural rock generation
    def generate_rocks(self, scene):
        # Clear the Rock spritelist
        if "Rock" not in scene:
            scene.add_sprite_list("Rock")
        scene["Rock"].clear()

        # Avoid props and spawned characters
        blockers = list(scene["Collision_Walls"]) + list(scene["Props"])
        # Keep spawn markers reserved even after spawn_player removes their layer.
        blockers.extend(self.tile_map.sprite_lists.get("Characters", []))
        for layer in ("Characters", "Player"):
            if layer in scene:
                blockers.extend(scene[layer])

        # Find all available sprite cells (positions)
        available_positions = []
        for tile in scene["Ground"]:
            # Use full sprite rectangles so partially occupied tiles stay clear.
            occupied = any(
                abs(tile.center_x - blocker.center_x) < (tile.width + blocker.width) / 2
                and abs(tile.center_y - blocker.center_y) < (tile.height + blocker.height) / 2
                for blocker in blockers
            )
            if not occupied:
                available_positions.append(tile.position)

        # Randomize the available positions & fill 40% with rocks
        shuffle(available_positions)
        num_rocks = int(len(available_positions) * FILL_PERCENTAGE)

        valid_rocks = []
        for rock_type, definition in ROCK_TYPES.items():
            if self.current_depth >= definition.min_depth:
                valid_rocks.append(rock_type)

        if not valid_rocks:
            return

        for position in available_positions[:num_rocks]:
            rock = Rock(type=choice(valid_rocks), scene=scene)
            rock.position = position
            scene.add_sprite("Rock", rock)

```

Current Depth = 10
![[Pasted image 20260929135237.png|1000]]

```python title=level.py hl=84-90
import arcade
from pathlib import Path
from random import choices, shuffle

from player import Player
from rock import Rock
from resources import ROCK_TYPES

FILL_PERCENTAGE = 0.40

class Level:
    def __init__(self):
        map_path = Path(__file__).resolve().parent / "assets" / "maps" / "base_map.json"
        self.tile_map = arcade.load_tilemap(map_path)
        self.width = self.tile_map.width * self.tile_map.tile_width
        self.height = self.tile_map.height * self.tile_map.tile_height
        self.current_depth = 10

    def spawn_player(self, scene):
        markers = [
            marker
            for marker in self.tile_map.sprite_lists.get("Characters", [])
            if marker.properties.get("Type") == "Player"
        ]
        if len(markers) != 1:
            raise ValueError("Characters must contain exactly one marker with Type = Player")

        player = Player()
        player.position = markers[0].position
        scene.remove_sprite_list_by_name("Characters")
        scene.add_sprite("Player", player)
        return player

    def constrain_player(self, player):
        # Keep the player's movement hit box inside the map rectangle.
        if player.left < 0:
            player.left = 0
        elif player.right > self.width:
            player.right = self.width
        if player.bottom < 0:
            player.bottom = 0
        elif player.top > self.height:
            player.top = self.height

    # Procedural rock generation
    def generate_rocks(self, scene):
        # Clear the Rock spritelist
        if "Rock" not in scene:
            scene.add_sprite_list("Rock")
        scene["Rock"].clear()

        # Avoid props and spawned characters
        blockers = list(scene["Collision_Walls"]) + list(scene["Props"])
        # Keep spawn markers reserved even after spawn_player removes their layer.
        blockers.extend(self.tile_map.sprite_lists.get("Characters", []))
        for layer in ("Characters", "Player"):
            if layer in scene:
                blockers.extend(scene[layer])

        # Find all available sprite cells (positions)
        available_positions = []
        for tile in scene["Ground"]:
            # Use full sprite rectangles so partially occupied tiles stay clear.
            occupied = any(
                abs(tile.center_x - blocker.center_x) < (tile.width + blocker.width) / 2
                and abs(tile.center_y - blocker.center_y) < (tile.height + blocker.height) / 2
                for blocker in blockers
            )
            if not occupied:
                available_positions.append(tile.position)

        # Randomize the available positions & fill 40% with rocks
        shuffle(available_positions)
        num_rocks = int(len(available_positions) * FILL_PERCENTAGE)

        valid_rocks = []
        for rock_type, definition in ROCK_TYPES.items():
            if self.current_depth >= definition.min_depth:
                valid_rocks.append(rock_type)

        if not valid_rocks:
            return

        # Higher rarity values give a rock type a larger share of the spawns.
        weights = [ROCK_TYPES[rock_type].rarity for rock_type in valid_rocks]
        for position in available_positions[:num_rocks]:
            rock_type = choices(valid_rocks, weights=weights, k=1)[0]
            rock = Rock(type=rock_type, scene=scene)
            rock.position = position
            scene.add_sprite("Rock", rock)

```

### Ladder Class
---
In this section, when the user breaks a rock, it will be replaced by a down ladder. The player can climb up/down ladders to reach other depths in the mine. So the current depth will be updated when the player moves up/down a ladder.

ladders.png - up ladder (left) and down ladder (right)
![[ladder.png|400]]

![[Pasted image 20260929140951.png|1000]]

```python title=ladder.py
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

```

Note that the ladder instance can be configured as either a "Down" or "Up" ladder.

```python title=rock.py hl=7,91-93
import arcade
from random import choice
from pathlib import Path
from PIL import Image

from ore import Ore
from ladder import Ladder
from resources import ROCK_TYPES, RockData, OreData
from arcade.easing import ease_value, ease_out, ease_in

FLASH_COLOR = arcade.color.WHITE
FLASH_DURATION = 0.1
HIT_SOUND_VOLUME = 0.2
BREAK_SOUND_VOLUME = 0.2

class Rock(arcade.Sprite):
    _hit_sound = None
    _break_sound = None

    def __init__(self, type="Stone", scene=None):
        self.type = type
        if Rock._hit_sound is None:
            Rock._hit_sound = arcade.load_sound(
                Path(__file__).resolve().parent / "assets/audio/pickaxe_hit.ogg"
            )
        if Rock._break_sound is None:
            Rock._break_sound = arcade.load_sound(
                Path(__file__).resolve().parent / "assets/audio/rock_breaking.wav"
            )
        definition = ROCK_TYPES.get(type, ROCK_TYPES["Stone"])
        asset_path = (
            Path(__file__).resolve().parent
            / "assets/mine_tiles/Ore n Gems"
            / definition.filename
        )
        sprite_sheet = arcade.load_spritesheet(asset_path)
        frames = sprite_sheet.get_texture_grid(size=(16, 16), columns=3, count=12)
        self.data = RockData(
            texture=frames[definition.rock_frame],
            ore=frames[0],
            max_health=definition.max_health,
            rarity=definition.rarity,
            min_depth=definition.min_depth,
            ore_value=definition.ore_value,
        )
    
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
        ore_data = OreData(
            texture=self.data.ore,
            Name=f"{self.type.lower()}_ore",
            value=self.data.ore_value,
        )
        ore = Ore(self.position, ore_data)
        self.scene.add_sprite("Ore", ore)
        self._ore_animation(ore)
        arcade.play_sound(Rock._break_sound, volume=BREAK_SOUND_VOLUME)
        self.remove_from_sprite_lists()

        ladder = Ladder(type="Down")
        ladder.position = self.position
        self.scene.add_sprite("Ladder", ladder)

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

```python title=game.py hl=18
import arcade

from level import Level
from game_camera import GameCamera

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.level = Level()
        self.background_color = self.level.tile_map.background_color or arcade.color.BLACK
        self.scene = arcade.Scene.from_tilemap(self.level.tile_map)
        self.camera = GameCamera()
        self.scene.add_sprite_list("Ladder")
        self.level.generate_rocks(self.scene)
        self.scene.add_sprite_list("Ore")

        self.player = self.level.spawn_player(self.scene)
        self.level.constrain_player(self.player)
        self.camera.follow(self.player, self.level)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            [self.scene["Collision_Walls"], self.scene["Rock"], self.scene["Ore"]],
        )
        
...
```

### Ladder chance and one ladder/level
---
![[Pasted image 20260929142550.png|1000]]

Note: Ladder chance is set to 0.1 so there is only a 10% chance that a ladder will appear when a rock is destroyed.

```python title=rock.py hl=15,95-97
import arcade
from random import choice, random
from pathlib import Path
from PIL import Image

from ore import Ore
from ladder import Ladder
from resources import ROCK_TYPES, RockData, OreData
from arcade.easing import ease_value, ease_out, ease_in

FLASH_COLOR = arcade.color.WHITE
FLASH_DURATION = 0.1
HIT_SOUND_VOLUME = 0.2
BREAK_SOUND_VOLUME = 0.2
LADDER_CHANCE = 0.10  # Chance per destroyed rock, from 0.0 to 1.0.

class Rock(arcade.Sprite):
    _hit_sound = None
    _break_sound = None

    def __init__(self, type="Stone", scene=None):
        self.type = type
        if Rock._hit_sound is None:
            Rock._hit_sound = arcade.load_sound(
                Path(__file__).resolve().parent / "assets/audio/pickaxe_hit.ogg"
            )
        if Rock._break_sound is None:
            Rock._break_sound = arcade.load_sound(
                Path(__file__).resolve().parent / "assets/audio/rock_breaking.wav"
            )
        definition = ROCK_TYPES.get(type, ROCK_TYPES["Stone"])
        asset_path = (
            Path(__file__).resolve().parent
            / "assets/mine_tiles/Ore n Gems"
            / definition.filename
        )
        sprite_sheet = arcade.load_spritesheet(asset_path)
        frames = sprite_sheet.get_texture_grid(size=(16, 16), columns=3, count=12)
        self.data = RockData(
            texture=frames[definition.rock_frame],
            ore=frames[0],
            max_health=definition.max_health,
            rarity=definition.rarity,
            min_depth=definition.min_depth,
            ore_value=definition.ore_value,
        )
    
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
        ore_data = OreData(
            texture=self.data.ore,
            Name=f"{self.type.lower()}_ore",
            value=self.data.ore_value,
        )
        ore = Ore(self.position, ore_data)
        self.scene.add_sprite("Ore", ore)
        self._ore_animation(ore)
        arcade.play_sound(Rock._break_sound, volume=BREAK_SOUND_VOLUME)
        self.remove_from_sprite_lists()

        has_down_ladder = "Ladder" in self.scene and any(
            ladder.type == "Down" for ladder in self.scene["Ladder"]
        )
        # Guarantee an exit if all previous rolls failed.
        last_rock = len(self.scene["Rock"]) == 0
        if not has_down_ladder and (random() < LADDER_CHANCE or last_rock):
            ladder = Ladder(type="Down")
            ladder.position = self.position
            self.scene.add_sprite("Ladder", ladder)

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

### Ladder Collision
---
```Output
Down ladder found
Down ladder found
Down ladder found
Down ladder found
Down ladder found
```

```python title=game.py hl=22-24
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
        # The physics engine resolves movement against walls, rocks, and ore.
        collisions = self.physics_engine.update()
        self.level.constrain_player(self.player)
        for sprite in collisions:
            if sprite in self.scene["Ore"]:
                if self.player.add_ore(sprite.ore_data):
                    sprite.remove_from_sprite_lists()
        self.player.on_update(delta_time)
        self.player.hit_rocks(self.scene["Rock"])
        for ladder in arcade.check_for_collision_with_list(self.player, self.scene["Ladder"]):
            if ladder.type == "Down":
                print("Down ladder found")
        self.camera.follow(self.player, self.level)
        
...
```

Now use the L key to climb down a ladder.

```output
Down ladder found
Go to next level
Down ladder found
Go to next level
```

```python title=game.py hl=23,53-59
import arcade

from level import Level
from game_camera import GameCamera

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.level = Level()
        self.background_color = self.level.tile_map.background_color or arcade.color.BLACK
        self.scene = arcade.Scene.from_tilemap(self.level.tile_map)
        self.camera = GameCamera()
        self.scene.add_sprite_list("Ladder")
        self.level.generate_rocks(self.scene)
        self.scene.add_sprite_list("Ore")

        self.player = self.level.spawn_player(self.scene)
        self.player_on_ladder = False
        self.level.constrain_player(self.player)
        self.camera.follow(self.player, self.level)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            [self.scene["Collision_Walls"], self.scene["Rock"], self.scene["Ore"]],
        )

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
        if on_down_ladder and not self.player_on_ladder:
            print("Down ladder found")
        self.player_on_ladder = on_down_ladder
        self.camera.follow(self.player, self.level)
        
...
```

### Level Manager
---
This class will manage transitions from level to level. When the user hits the L key while a player is on a ladder, the scene will change from the current level to the next lower level.

![[20260929-2056-49.5577355.mp4]]

```python title=level_manager.py
import arcade
from level import Level

class LevelManager:
    def __init__(self, game_view):
        self.game_view = game_view

    def load_first_level(self):
        level = Level()
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
        view.scene = scene
        view.player = player
        view.physics_engine = physics_engine
        view.player_on_ladder = False
        view.background_color = level.tile_map.background_color or arcade.color.BLACK
        view.camera.follow(player, level)

    def next_level(self):
        # Reload the first level until additional levels are available.
        self.load_first_level()

```

```python title=ladder.py hl=20-22
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
        return key == arcade.key.L and self.type == "Down"

```

```python title=game.py hl=3,15-16,46-51
import arcade

from level_manager import LevelManager
from game_camera import GameCamera

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Coding with Russ - Mining Roguelite Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.camera = GameCamera()
        self.level_manager = LevelManager(self)
        self.level_manager.load_first_level()
        
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
                
...
```

### Multiple Maps
---
![[Pasted image 20260929151320.png]]

This is level 3!

```Output
Current depth: 2
Current depth: 3
```

```python title=level_manager.py
import arcade
from level import Level

class LevelManager:
    def __init__(self, game_view):
        self.game_view = game_view

    def load_first_level(self):
        self.load_level(1)

    def load_level(self, depth):
        level = Level()
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
        view.scene = scene
        view.player = player
        view.physics_engine = physics_engine
        view.player_on_ladder = False
        view.background_color = level.tile_map.background_color or arcade.color.BLACK
        view.camera.follow(player, level)

    def next_level(self):
        self.load_level(self.game_view.level.current_depth + 1)
        print(f"Current depth: {self.game_view.level.current_depth}")

```

That was easy. We now have levels with the same map but pseudo-random procedural rocks on each level.
- The type of rocks changes based on the current depth'

### Multiple Maps
---
`map_1.json`
![[Pasted image 20260929154405.png]]


![[Pasted image 20260929154312.png|1000]]

Nice!

```python title=level.py hl=7-9
from rock import Rock
from resources import ROCK_TYPES

FILL_PERCENTAGE = 0.40

class Level:
    def __init__(self, map_name="base_map.json"):
        map_path = Path(__file__).resolve().parent / "assets" / "maps" / map_name
        self.tile_map = arcade.load_tilemap(map_path)
        self.width = self.tile_map.width * self.tile_map.tile_width
        self.height = self.tile_map.height * self.tile_map.tile_height
        self.current_depth = 1
        
...
```

```python title=game_manager.py hl=12-13
import arcade
from level import Level

class LevelManager:
    def __init__(self, game_view):
        self.game_view = game_view

    def load_first_level(self):
        self.load_level(1)

    def load_level(self, depth):
        map_name = "map_1.json" if depth == 2 else "base_map.json"
        level = Level(map_name=map_name)
        level.current_depth = depth
        scene = arcade.Scene.from_tilemap(level.tile_map)
        scene.add_sprite_list("Ladder")
        level.generate_rocks(scene)
        scene.add_sprite_list("Ore")
        
...
```

### Random Level Maps
---
![[Pasted image 20260929160730.png]]

![[Pasted image 20260929160618.png|1000]]

```python title=level_manager.py hl=9,15-22,45
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

