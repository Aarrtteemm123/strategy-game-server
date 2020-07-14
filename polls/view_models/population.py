import json
from polls.view_models.modifier import ModifierView

class PopulationView:
    def __init__(self, population = 0, farmers = 0, miners = 0, workers = 0, soldiers = 0,
                 other = 0, percent_total_progress = 0, modifiers=None):
        if modifiers is None:
            modifiers = [ModifierView()]
        self.population = population
        self.farmers = farmers
        self.miners = miners
        self.workers = workers
        self.soldiers = soldiers
        self.other = other
        self.percent_total_progress = percent_total_progress
        self.modifiers = modifiers

tv = PopulationView()
print(json.dumps(tv.__dict__, default=lambda x: x.__dict__))