import arcade
from pathlib import Path
from random import choices, shuffle

from player import Player
from ladder import Ladder
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

    def spawn_exit_ladders(self, scene):
        for marker in self.tile_map.sprite_lists.get("Exit", []):
            ladder = Ladder(type="Up")
            ladder.position = marker.position
            scene.add_sprite("Ladder", ladder)
        if "Exit" in scene:
            scene.remove_sprite_list_by_name("Exit")

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
        for layer in ("Characters", "Player", "Ladder"):
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
