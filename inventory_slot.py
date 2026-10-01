STACK_SIZE = 5

class InventorySlot:
    def __init__(self, data, qty):
        self.ore_data = data
        self.quantity = qty

    def can_stack(self, data) -> bool:
        return self.ore_data.name == data.name and self.quantity < STACK_SIZE

    def add_ore(self):
        self.quantity += 1
