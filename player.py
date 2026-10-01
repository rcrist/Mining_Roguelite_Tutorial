import arcade
from pathlib import Path
from enum import Enum, auto

from animation_player import AnimationPlayer, UPDATES_PER_FRAME
from resources import OreData
from inventory import Inventory

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
    CLIMB_DOWN = auto()
    CLIMB_UP = auto()

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
        self.pickaxe_strength = 1
        self.pickaxe_held = False
        self.pickaxe_cooldown_remaining = 0.0
        self.inventory = Inventory(4)  # Create invetory with 4 slots

    def die(self):
        if self.current_state == State.DEATH:
            return
        self.change_x = 0
        self.change_y = 0
        self.pickaxe_held = False
        self.pickaxe_active = False
        # The sprite sheet only has horizontal death animations.
        if self.current_direction != Dir.LEFT:
            self.current_direction = Dir.RIGHT
        self.animation_player.reset()
        self.current_state = State.DEATH

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
                rock.take_damage(self.pickaxe_strength)
                self.rocks_hit_this_swing.add(rock)

    def on_key_press(self, key, key_modifiers):
        if self.current_state == State.DEATH:
            return
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
        if self.current_state == State.DEATH:
            return
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
        return self.inventory.add_item(data)
