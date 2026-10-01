from inventory_slot_ui import InventorySlotUi

class InventoryUi:
    def __init__(self, inventory=None, x=0, y=0, spacing=2, center_x=None, top=None):
        """Display the inventory, optionally anchored by its center and top."""
        self.inventory = inventory
        self.x = x
        self.y = y
        self.spacing = spacing
        self.center_x = center_x
        self.top = top
        self.slots = []
        self.update()

    def update(self):
        inventory_slots = self.inventory.slots if self.inventory is not None else []
        while len(self.slots) < len(inventory_slots):
            self.slots.append(InventorySlotUi())
        del self.slots[len(inventory_slots):]

        row_width = sum(slot.width for slot in self.slots)
        row_width += self.spacing * max(0, len(self.slots) - 1)
        next_x = self.x if self.center_x is None else self.center_x - row_width / 2
        for slot, item in zip(self.slots, inventory_slots):
            slot.left = next_x
            if self.top is None:
                slot.bottom = self.y
            else:
                slot.top = self.top
            next_x = slot.right + self.spacing
            icon = item.ore_data.texture if item is not None else None
            if slot.item_icon is not icon:
                slot.item_icon = icon
            quantity = f"x{item.quantity}" if item is not None else ""
            if slot.quantity_label.text != quantity:
                slot.quantity_label.text = quantity

    def draw(self):
        self.update()
        for slot in self.slots:
            slot.draw()
