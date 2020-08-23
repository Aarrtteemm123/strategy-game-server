import json

from polls.view_models.modifier import ModifierView


class UnitCharacteristicView:
    def __init__(self,unit_name = '',attack_value = 1.0,defence_value = 1.0):
        self.unit_name = unit_name
        self.attack_value = attack_value
        self.defence_value = defence_value


class ArmyCardView:
    def __init__(self, name = '', link_img = '', number = 0, need_peoples = 0,
                 maintenance_price = 0, total_maintenance_price = 0,
                 reserve = 0,modifiers=None,unit_characteristic=None):
        if modifiers is None:
            modifiers = [ModifierView()]
        if unit_characteristic is None:
            unit_characteristic = [UnitCharacteristicView()]
        self.name = name
        self.link_img = link_img
        self.number = number
        self.need_peoples = need_peoples
        self.maintenance_price = maintenance_price
        self.total_maintenance_price = total_maintenance_price
        self.reserve = reserve
        self.modifiers = modifiers
        self.unit_characteristic = unit_characteristic

#tv = ArmyCardView()
#print(json.dumps(tv.__dict__, default=lambda x: x.__dict__))