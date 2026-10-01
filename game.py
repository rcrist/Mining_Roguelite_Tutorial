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
        elif upgrade_name == "oxygen_tank":
            self.oxygen_system.max_oxygen += 100
        elif upgrade_name == "inventory_size":
            inventory = self.player.inventory
            inventory.slots.append(None)
            inventory.max_slots = len(inventory.slots)
            self.hud_camera.inventory_ui.update()

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
