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
LADDER_CHANCE = 0.20  # Chance per destroyed rock, from 0.0 to 1.0.

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
            name=f"{self.type.lower()}_ore",
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
