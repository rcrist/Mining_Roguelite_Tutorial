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
    name: str = "stone_ore"
    value: int = 10
