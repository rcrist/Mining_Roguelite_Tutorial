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
            player.pickaxe_strength = previous_player.pickaxe_strength
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
            self.game_view.show_summary()
            return
        depth = self.game_view.level.current_depth
        if depth > 1:
            self.load_level(depth - 1)
            print(f"Current depth: {self.game_view.level.current_depth}")
