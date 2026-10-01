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
