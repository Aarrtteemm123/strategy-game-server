import json
from polls.view_models.modifier import ModifierView

class PopulationView:
    def __init__(self, population = 0, farmers = 0, miners = 0, workers = 0, soldiers = 0,
                 free = 0, others = 0, percent_total_progress = 0, modifiers=None,
                 pie_chart_data=None, pie_chart_labels=None):
        if pie_chart_labels is None:
            pie_chart_labels = []
        if pie_chart_data is None:
            pie_chart_data = []
        if modifiers is None:
            modifiers = [ModifierView()]
        self.population = population
        self.farmers = farmers
        self.miners = miners
        self.workers = workers
        self.soldiers = soldiers
        self.free = free
        self.others = others
        self.percent_total_progress = percent_total_progress
        self.modifiers = modifiers
        self.pie_chart_data = pie_chart_data
        self.pie_chart_labels = pie_chart_labels
