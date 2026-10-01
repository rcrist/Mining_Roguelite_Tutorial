from inventory_slot import InventorySlot

class Inventory:
    def __init__(self, starting_slots=4):
        self.slots = []
        self.starting_slots = starting_slots
        self.max_slots = starting_slots

        for i in range(self.max_slots):
            self.slots.append(None)

    def add_item(self, data) -> bool:
        # Try stacking with existing item
        for slot in self.slots:
            if slot is not None and slot.can_stack(data):
                slot.add_ore()
                print(slot.ore_data.name, "|", slot.quantity)
                return True

        # Find empty slot
        for i in range(len(self.slots)):
            if self.slots[i] is None:
                self.slots[i] = InventorySlot(data, 1)
                print(self.slots)
                return True

        # No space in the inventory
        return False
