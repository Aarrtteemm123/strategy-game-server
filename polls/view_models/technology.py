import json

from polls.view_models.modifier import ModifierView


class TechnologyView:
    def __init__(self, name = '', price_upgrade = 0, level = 0, max_level = 100,
                 percent_total_result = 0, modifiers=None):
        if modifiers is None:
            modifiers = [ModifierView()]
        self.name = name
        self.price_upgrade = price_upgrade
        self.level = level
        self.max_level = max_level
        self.percent_total_result = percent_total_result
        self.modifiers = modifiers


#print(json.dumps(tv.__dict__, default=lambda x: x.__dict__))