from polls.view_models.modifier import ModifierView


class PoliticalLawsView:
    def __init__(self, name = '', description = '', price = 0, modifiers=None):
        if modifiers is None:
            modifiers = [ModifierView()]
        self.name = name
        self.description = description
        self.price = price
        self.modifiers = modifiers