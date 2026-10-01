import arcade
from dataclasses import replace
from functools import partial
from pathlib import Path
from arcade.gui import NinePatchTexture, UIManager
from pyglet.event import EventDispatcher

from button_theme import RoundedButton, button_style
from shop_button import ShopButtonUi

class ShopUi(EventDispatcher):
    def __init__(self, x=0, y=0, width=280, height=240, text_color=(40, 40, 48)):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.gold = 0  # Total gold the player has

        self.upgrades = {
            "pickaxe": {"level": 0, "max_level": 3, "costs": [200, 500, 1500]},
            "oxygen_tank": {"level": 0, "max_level": 3, "costs": [250, 600, 2000]},
            "inventory_size": {"level": 0, "max_level": 2, "costs": [500, 2500]},
        }

        self.separator_color = text_color
        self.position = (0, 0)
        arcade.load_font(Path(__file__).resolve().parent / "assets/font/m5x7.ttf")
        self.panel = NinePatchTexture(
            left=10, right=10, bottom=10, top=10,
            texture=arcade.load_texture(
                Path(__file__).resolve().parent / "assets/ui/DialogueBoxSimple.png"
            ),
        )

        # Create the total gold label
        self.gold_label = arcade.Text(
            text="Total Gold: 0", x=0, y=0,
            font_name="m5x7", font_size=12,
            color=(40, 40, 48), anchor_x="center", anchor_y="center",
        )

        # Create the 3 shop buttons for pickaxe level, oxygen level, inventory size
        self.pickaxe_button = ShopButtonUi("Pickaxe", "Level 0/3", "200 gold")
        self.oxygen_button = ShopButtonUi("Oxygen Tank", "Level 0/3", "250 gold")
        self.inventory_button = ShopButtonUi("Inventory Size", "Level 0/2", "500 gold")

        self.pickaxe_button = ShopButtonUi(
            button_name=self.pickaxe_button.shop_button.button,
            level=self.pickaxe_button.shop_button.level_label, 
            gold=self.pickaxe_button.shop_button.cost_label,
            text_color=text_color, 
        )
        self.oxygen_button = ShopButtonUi(
            button_name=self.oxygen_button.shop_button.button,
            level=self.oxygen_button.shop_button.level_label, 
            gold=self.oxygen_button.shop_button.cost_label,
            text_color=text_color, 
        )
        self.inventory_button = ShopButtonUi(
            button_name=self.inventory_button.shop_button.button,
            level=self.inventory_button.shop_button.level_label, 
            gold=self.inventory_button.shop_button.cost_label,
            text_color=text_color,
        )

        # Create the "Back To The Mines" button
        self.button_manager = UIManager()
        self.upgrade_buttons = {
            "pickaxe": self.pickaxe_button,
            "oxygen_tank": self.oxygen_button,
            "inventory_size": self.inventory_button,
        }
        for upgrade_name, button in self.upgrade_buttons.items():
            button.option_button.style = {
                **button_style,
                "disabled": replace(button_style["disabled"], bg=arcade.color.GRAY),
            }
            # Use the shop manager so all buttons share input and camera handling.
            button.button_manager.remove(button.option_button)
            self.button_manager.add(button.option_button)
            button.option_button.push_handlers(
                on_click=partial(self.buy_upgrade, upgrade_name),
            )
        self.shop_slot = ShopButtonUi(text_color=text_color)

        self.mines_button = self.button_manager.add(RoundedButton(
            text="Back To\nThe Mines", multiline=True,
            width=self.shop_slot.row_width, height=40, style=button_style,
        ))
        self.mines_button.ui_label._label.align = "center"

    def buy_upgrade(self, upgrade_name: str, event=None) -> None:
        """Buy one level if affordable and show the next upgrade price."""
        upgrade = self.upgrades[upgrade_name]
        if upgrade["level"] >= upgrade["max_level"]:
            return
        cost = upgrade["costs"][upgrade["level"]]
        if self.gold < cost:
            return

        self.set_gold(self.gold - cost)
        upgrade["level"] += 1
        button = self.upgrade_buttons[upgrade_name]
        maxed = upgrade["level"] >= upgrade["max_level"]
        button.setup(
            display_name=button.shop_button.button,
            level="MAX" if maxed else f"Level {upgrade['level']}/{upgrade['max_level']}",
            cost="MAX" if maxed else f"{upgrade['costs'][upgrade['level']]} gold",
        )
        button.option_button.disabled = maxed
        self.dispatch_event("on_upgrade_purchased", upgrade_name, self.gold)

    def set_gold(self, total_gold: int) -> None:
        """Set the total gold label."""
        self.gold_label.text = f"Total Gold: {total_gold}"
        self.gold = total_gold

    def draw(self):
        center_x, center_y = self.position
        buttons = (self.pickaxe_button, self.oxygen_button, self.inventory_button)
        gap = 6
        section_gap = 18
        gold_height = self.gold_label.content_height + 8
        total_height = (
            gold_height + sum(button.option_button.height for button in buttons)
            + self.mines_button.height + gap * (len(buttons) - 1) + section_gap * 2
        )
        top = round(center_y + total_height / 2)
        self.mines_button.width = max(slot.row_width for slot in buttons)
        self.mines_button.left = round(center_x - self.mines_button.width / 2)
        self.mines_button.bottom = top - total_height

        panel_width = max(self.width, self.mines_button.width + 24)
        panel_height = max(self.height, total_height + 24)
        self.panel.draw_rect(
            rect=arcade.LBWH(
                center_x - panel_width / 2, center_y - panel_height / 2,
                panel_width, panel_height,
            ),
            pixelated=True,
        )

        # Draw the total gold label
        self.gold_label.x = round(self.mines_button.left + self.mines_button.width / 2)
        self.gold_label.y = top - gold_height / 2
        arcade.draw_rect_filled(
            arcade.LBWH(
                self.mines_button.left,
                self.gold_label.y - self.gold_label.content_height / 2 - 4,
                self.mines_button.width,
                self.gold_label.content_height + 8,
            ),
            arcade.color.ORANGE,
        )
        self.gold_label.draw()

        next_top = top - gold_height - section_gap
        for button in buttons:
            button.position = (center_x, next_top - button.option_button.height / 2)
            button.button_manager.camera = self.button_manager.camera
            button.draw()
            next_top -= button.option_button.height + gap

        # Draw the mines button
        self.button_manager.draw()


ShopUi.register_event_type("on_upgrade_purchased")
