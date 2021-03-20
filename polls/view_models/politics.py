from typing import List

from polls.view_models.modifier import ModifierView


class LawView:
    def __init__(self, name: str, description: str, modifiers: List[ModifierView], value=''):
        self.value = value
        self.modifiers = modifiers
        self.description = description
        self.name = name

class PoliticsView:
    def __init__(self, selected_laws=None, conscription_laws=None, pop_laws=None):
        if pop_laws is None:
            pop_laws = []
        self.pop_laws = pop_laws
        if conscription_laws is None:
            conscription_laws = []
        self.conscription_laws = conscription_laws
        if selected_laws is None:
            selected_laws = []
        self.selected_laws = selected_laws