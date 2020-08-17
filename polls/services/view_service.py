import json, time

from polls.models import User, Country, Trade
from polls.services.game_service import GameService
from polls.view_models.basic_statistic import BasicStatisticView, ChartBudgetData, ChartPopulationData, ChartProfitData, \
    ChartGoodsData, TableRowDataView
from polls.view_models.budget import BudgetView, TaxesCard
from polls.view_models.modifier import ModifierView


class CountryViewService:
    def get_basic_statistic(self, user_id):
        start = time.time()
        user = User.objects(_id=user_id).first()
        country = Country.objects(_id=user.country._id).first()

        total_profit = GameService().get_total_profit(country)
        economic_place = GameService().get_economic_place(country.name)
        army_place = GameService().get_army_place(country.name)

        profit_data = [history.value for history in country.budget.profit_history]
        expenses_data = [history.value for history in country.budget.expenses_history]
        x_budget_data = [str(history.time) for history in country.budget.profit_history]
        max_chart_budget_y_axis_value = max(max(profit_data), max(expenses_data)) * 1.1
        chart_budget = ChartBudgetData(profit_data, expenses_data, x_budget_data, max_chart_budget_y_axis_value)

        pop_data = [history.value for history in country.population.population_history]
        x_pop_data = [str(history.time) for history in country.budget.profit_history]
        chart_pop = ChartPopulationData(pop_data, x_pop_data)

        chart_profit_data = [
            GameService().get_pop_taxes_profit(country) / (total_profit + country.budget.military_expenses),
            GameService().get_mines_profit(country) / (total_profit + country.budget.military_expenses),
            GameService().get_farms_profit(country) / (total_profit + country.budget.military_expenses),
            GameService().get_factories_profit(country) / (total_profit + country.budget.military_expenses)
        ]

        chart_profit = ChartProfitData(chart_profit_data, ['Taxes', 'Mines', 'Farms', 'Industry'],
                                       max(chart_profit_data))

        goods_data = GameService().get_goods_data(country)
        chart_farms_goods_data = ChartGoodsData(goods_data['farms']['values'], goods_data['farms']['names'])
        chart_mines_goods_data = ChartGoodsData(goods_data['mines']['values'], goods_data['mines']['names'])
        chart_factories_goods_data = ChartGoodsData(goods_data['factories']['values'], goods_data['factories']['names'])
        chart_military_factories_goods_data = ChartGoodsData(goods_data['military factories']['values'],
                                                             goods_data['military factories']['names'])

        table_data = GameService().get_table_world_place_production()
        industry = []
        industry.extend(country.farms)
        industry.extend(country.mines)
        industry.extend(country.factories)
        industry.extend(country.military_factories)

        goods_table = []
        for building in industry:
            name_goods = GameService().get_name_goods_from_building(building.name)
            target_obj = next(filter(lambda x: x[0] == country.name, table_data[name_goods]))
            word_place = table_data[name_goods].index(target_obj) + 1
            goods_table.append(TableRowDataView(building.link_img,
                                                name_goods, building.number, word_place))
        farm_goods_table = goods_table[:len(country.farms)]
        mine_goods_table = goods_table[len(country.farms):len(country.farms) + len(country.mines)]
        industrial_goods_table = goods_table[
                                 len(country.farms) + len(country.mines):len(country.farms) + len(country.mines) + len(
                                     country.factories)]
        military_goods_table = goods_table[len(country.farms) + len(country.mines) + len(country.factories):]

        bsv = BasicStatisticView(
            country.link_img, country.name, country.population.total_population,
            country.budget.money, total_profit, economic_place, army_place, country.army.victories,
            country.army.losses, chart_budget, chart_pop, chart_profit, chart_farms_goods_data,
            chart_mines_goods_data, chart_factories_goods_data, chart_military_factories_goods_data,
            farm_goods_table, mine_goods_table, industrial_goods_table, military_goods_table
        )
        finish = time.time()
        return bsv

    def get_budget(self, user_id):
        start = time.time()
        user = User.objects(_id=user_id).first()
        country = Country.objects(_id=user.country._id).first()

        pop_taxes_profit = GameService().get_pop_taxes_profit(country)
        army_taxes_profit = GameService().get_army_taxes_profit(country)
        farms_taxes_profit = GameService().get_farms_taxes_profit(country)
        mines_taxes_profit = GameService().get_mines_taxes_profit(country)
        all_factory_taxes_profit = GameService().get_civil_factories_taxes_profit(country) \
            + GameService().get_military_factories_taxes_profit(country)
        taxes_profit = pop_taxes_profit \
            + farms_taxes_profit \
            + mines_taxes_profit \
            + all_factory_taxes_profit
        farms_profit = GameService().get_farms_production_profit(country)
        mines_profit = GameService().get_mines_production_profit(country)
        civil_factories_profit = GameService().get_civil_factories_production_profit(country)
        military_factories_profit = GameService().get_military_factories_production_profit(country)
        total_profit = taxes_profit + farms_profit + mines_profit + civil_factories_profit + military_factories_profit
        pop_tax_card = TaxesCard('population taxes',country.budget.population_taxes,
                        pop_taxes_profit,[ModifierView(mod.value,mod.address_from) for mod in country.population.modifiers])
        army_views_modifiers = [ModifierView(mod.value,mod.address_from) for mod in country.army.attack_modifiers]
        army_views_modifiers.extend([ModifierView(mod.value,mod.address_from) for mod in country.army.defence_modifiers])
        army_tax_card = TaxesCard('army taxes',country.budget.military_taxes,army_taxes_profit,army_views_modifiers)
        farms_tax_card = TaxesCard('farms taxes',country.budget.farms_taxes,farms_taxes_profit,
                        [ModifierView(mod.value,mod.address_from) for mod in country.industry_modifiers
                         if mod.address_to == 'farms' or mod.address_to == 'industry'])
        mines_tax_card = TaxesCard('mines taxes',country.budget.mines_taxes,mines_taxes_profit,
                        [ModifierView(mod.value,mod.address_from) for mod in country.industry_modifiers
                         if mod.address_to == 'mines' or mod.address_to == 'industry'])
        factories_tax_card = TaxesCard('factories taxes', country.budget.factories_taxes, all_factory_taxes_profit,
                  [ModifierView(mod.value, mod.address_from) for mod in country.industry_modifiers
                   if mod.address_to == 'factories' or mod.address_to == 'industry'])

        budget_view = BudgetView(country.budget.money, taxes_profit,farms_profit,
            mines_profit,civil_factories_profit + military_factories_profit,
            country.budget.military_expenses,total_profit,pop_tax_card,army_tax_card,
            farms_tax_card,mines_tax_card,factories_tax_card
        )

        finish = time.time()
        return budget_view

    def get_technology(self, user_id):
        pass

    def get_industry(self, user_id):
        pass

    def get_warehouse(self, user_id):
        pass

    def get_politics(self, user_id):
        pass

    def get_population(self, user_id):
        pass

    def get_trade(self, user_id):
        pass

    def get_army(self, user_id):
        pass


class NewsViewService:
    def get_news(self):
        pass
