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
