class WarehouseCardView:
    def __init__(self,name = '',link_img = '',value = 0,capacity = 0,filling_speed = 0,
                 level = 0, max_level = 0, price_upgrade = 0,added_capacity = 0,
                 increase_price=0):
        self.name = name
        self.link_img = link_img
        self.value = value
        self.capacity = capacity
        self.filling_speed = filling_speed
        self.level = level
        self.max_level = max_level
        self.price_upgrade = price_upgrade
        self.added_capacity = added_capacity
        self.increase_price = increase_price