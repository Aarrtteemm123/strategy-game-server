from polls.view_models.modifier import ModifierView

class TaxesCard:
    def __init__(self, name='', percent_value=0, profit=0, modifiers=None):
        if modifiers is None:
            modifiers = [ModifierView()]
        self.name = name
        self.percent_value = percent_value
        self.profit = profit
        self.modifiers = modifiers


class BudgetView:
    def __init__(self, money=0, taxes_profit=0, farms_profit=0, mines_profit=0,
                 factories_profit=0, military_expenses=0,
                 total_profit=0, population_taxes=TaxesCard(), army_taxes=TaxesCard(),
                 farms_taxes=TaxesCard(), mines_taxes=TaxesCard(),
                 factories_taxes=TaxesCard()):
        self.money = money
        self.taxes_profit = taxes_profit
        self.farms_profit = farms_profit
        self.mines_profit = mines_profit
        self.factories_profit = factories_profit
        self.military_expenses = military_expenses
        self.total_profit = total_profit
        self.population_taxes = population_taxes
        self.army_taxes = army_taxes
        self.farms_taxes = farms_taxes
        self.mines_taxes = mines_taxes
        self.factories_taxes = factories_taxes
