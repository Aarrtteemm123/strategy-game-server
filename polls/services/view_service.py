import time,re
import json

from datetime import datetime
from polls.models import User, Country, Trade, News, ArmyUnit, Cache, GlobalSettings, FQA, Law
from polls.services.game_service import GameService
from polls.view_models.account import AccountView
from polls.view_models.army import ArmyCardView, UnitCharacteristicView
from polls.view_models.basic_statistic import BasicStatisticView, ChartBudgetData, ChartPopulationData, ChartProfitData, ChartGoodsData, TableRowDataView
from polls.view_models.budget import BudgetView, TaxesCard
from polls.view_models.industry import IndustrialCardView, TableRowGoodsView
from polls.view_models.modifier import ModifierView
from polls.view_models.news import NewsView
from polls.view_models.player import PlayerView, TopPlayersPage
from polls.view_models.politics import LawView, PoliticsView
from polls.view_models.population import PopulationView
from polls.view_models.technology import TechnologyView
from polls.view_models.trade import TradeCardView, TableRowProducerView, ChartPriceGoods
from polls.view_models.warehouse import WarehouseCardView

class CountryViewService:
    def get_basic_statistic(self, user_id: str):
        start = time.time()
        user = User.objects(id=user_id).first()
        country = Country.objects(id=user.country.id).first()

        total_profit = int(GameService().get_total_profit(country))
        economic_place = GameService().get_economic_place(country.name)
        army_place = GameService().get_army_place(country.name)

        money_history = [int(history.value) for history in country.budget.budget_history]
        x_money_data = [str(history.time) for history in country.budget.budget_history]
        chart_money = ChartPopulationData(money_history,x_money_data)

        profit_data = [int(history.value) for history in country.budget.profit_history]
        expenses_data = [int(history.value) for history in country.budget.expenses_history]
        x_budget_data = [str(history.time) for history in country.budget.profit_history]
        max_chart_budget_y_axis_value = 0
        if profit_data and expenses_data:
            max_chart_budget_y_axis_value = max(max(profit_data), max(expenses_data))
        chart_budget = ChartBudgetData(profit_data, expenses_data, x_budget_data, max_chart_budget_y_axis_value)

        pop_data = [round(history.value,1) for history in country.population.population_history]
        x_pop_data = [str(history.time) for history in country.population.population_history]
        chart_pop = ChartPopulationData(pop_data, x_pop_data)

        chart_profit_data = [
            round(GameService().get_pop_taxes_profit(country) / (total_profit + country.budget.military_expenses) * 100),
            round(GameService().get_mines_profit(country) / (total_profit + country.budget.military_expenses) * 100),
            round(GameService().get_farms_profit(country) / (total_profit + country.budget.military_expenses) * 100),
            round(GameService().get_factories_profit(country) / (total_profit + country.budget.military_expenses) * 100)
        ]

        chart_profit = ChartProfitData(chart_profit_data, ['Taxes', 'Mines', 'Farms', 'Industry'],
                                       round(max(chart_profit_data)))

        goods_data = GameService().get_goods_data(country)
        chart_farms_goods_data = ChartGoodsData(goods_data['farms']['values'], goods_data['farms']['names'])
        chart_mines_goods_data = ChartGoodsData(goods_data['mines']['values'], goods_data['mines']['names'])
        chart_factories_goods_data = ChartGoodsData(goods_data['factories']['values'], goods_data['factories']['names'])
        chart_military_factories_goods_data = ChartGoodsData(goods_data['military factories']['values'],goods_data['military factories']['names'])

        table_data = GameService().get_table_world_place_production()
        industry = []
        industry.extend(country.farms)
        industry.extend(country.mines)
        industry.extend(country.factories)
        industry.extend(country.military_factories)

        goods_table = []
        for building in industry:
            name_goods = GameService().get_name_goods_from_building(building.name)
            target_country = next(filter(lambda x: x[0] == country.name, table_data[name_goods]))
            word_place = table_data[name_goods].index(target_country) + 1
            goods_table.append(TableRowDataView(building.link_img,name_goods, building.number, word_place))

        farm_goods_table = goods_table[:len(country.farms)]
        mine_goods_table = goods_table[len(country.farms):len(country.farms) + len(country.mines)]
        industrial_goods_table = goods_table[len(country.farms) + len(country.mines):len(country.farms) + len(country.mines) + len(country.factories)]
        military_goods_table = goods_table[len(country.farms) + len(country.mines) + len(country.factories):]

        bsv = BasicStatisticView(
            country.link_img, country.name, country.population.total_population,
            country.budget.money, total_profit, economic_place, army_place, country.army.victories,
            country.army.losses,chart_money, chart_budget, chart_pop, chart_profit, chart_farms_goods_data,
            chart_mines_goods_data, chart_factories_goods_data, chart_military_factories_goods_data,
            farm_goods_table, mine_goods_table, industrial_goods_table, military_goods_table
        )
        finish = time.time()
        return bsv

    def get_budget(self, user_id: str):
        start = time.time()
        user = User.objects(id=user_id).first()
        country = Country.objects(id=user.country.id).first()

        pop_taxes_profit = int(GameService().get_pop_taxes_profit(country))
        army_taxes_profit = int(GameService().get_army_taxes_profit(country))
        farms_taxes_profit = int(GameService().get_farms_taxes_profit(country))
        mines_taxes_profit = int(GameService().get_mines_taxes_profit(country))
        factories_taxes_profit = int(GameService().get_factories_taxes_profit(country))

        taxes_profit = pop_taxes_profit + farms_taxes_profit + mines_taxes_profit + factories_taxes_profit
        farms_profit = int(GameService().get_farms_production_profit(country))
        mines_profit = int(GameService().get_mines_production_profit(country))
        factories_profit = int(GameService().get_factories_production_profit(country))
        total_profit = taxes_profit + farms_profit + mines_profit + factories_profit

        pop_tax_card = TaxesCard('population taxes',country.budget.population_taxes,pop_taxes_profit,[ModifierView(round(mod.value,2),mod.address_from) for mod in country.population.modifiers])
        army_views_modifiers = [ModifierView(round(mod.value,2),'to attack, '+mod.address_from) for mod in country.army.attack_modifiers]
        army_views_modifiers.extend([ModifierView(round(mod.value,2),'to defence, '+mod.address_from) for mod in country.army.defence_modifiers])
        army_tax_card = TaxesCard('army taxes',country.budget.military_taxes,army_taxes_profit,army_views_modifiers)
        farms_tax_card = TaxesCard('farms taxes',country.budget.farms_taxes,farms_taxes_profit,[ModifierView(round(mod.value,2),mod.address_from) for mod in country.industry_modifiers if mod.address_to == 'farms' or mod.address_to == 'industry'])
        mines_tax_card = TaxesCard('mines taxes',country.budget.mines_taxes,mines_taxes_profit,[ModifierView(round(mod.value,2),mod.address_from) for mod in country.industry_modifiers if mod.address_to == 'mines' or mod.address_to == 'industry'])
        factories_tax_card = TaxesCard('factories taxes', country.budget.factories_taxes, factories_taxes_profit,[ModifierView(round(mod.value,2), mod.address_from) for mod in country.industry_modifiers if mod.address_to == 'factories' or mod.address_to == 'industry'])

        budget_view = BudgetView(int(country.budget.money), taxes_profit,farms_profit,
            mines_profit,factories_profit,
            country.budget.military_expenses,total_profit,pop_tax_card,army_tax_card,
            farms_tax_card,mines_tax_card,factories_tax_card
        )

        finish = time.time()
        return budget_view

    def get_technologies(self, user_id: str):
        start = time.time()
        user = User.objects(id=user_id).first()
        country = Country.objects(id=user.country.id).first()

        technologies_view_list = []
        for technology in country.technologies:
            technology_view = TechnologyView(technology.name,technology.price_upgrade,
                    technology.level,technology.max_level,technology.level * technology.modifiers[0].value,
                    [ModifierView(mod.value,mod.address_to) for mod in technology.modifiers])
            technologies_view_list.append(technology_view)

        finish = time.time()
        return technologies_view_list

    def get_industry(self, user_id: str):
        start = time.time()
        user = User.objects(id=user_id).first()
        country = Country.objects(id=user.country.id).first()
        industry_dict = {}
        farms_list = []
        mines_list = []
        factories_list = []
        game_service = GameService()

        farms_modifiers = game_service.get_industry_modifiers(country, 'farms')
        mines_modifiers = game_service.get_industry_modifiers(country, 'mines')
        factories_modifiers = game_service.get_industry_modifiers(country, 'factories')

        for farm in country.farms:
            industrial_card_view = IndustrialCardView(
                farm.name,farm.link_img,round(farm.production_speed,2),
                round(farm.active_number * farm.production_speed * farms_modifiers,2),
                farm.price_build,farm.workers,farm.number,farm.active_number,farm.number * farm.workers,[]
            )
            farms_list.append(industrial_card_view)

        industry_dict['farms'] = farms_list

        for mine in country.mines:
            industrial_card_view = IndustrialCardView(
                mine.name,mine.link_img,round(mine.production_speed,2),
                round(mine.active_number * mine.production_speed * mines_modifiers,2),
                mine.price_build,mine.workers,mine.number,mine.active_number,mine.number * mine.workers,[]
            )
            mines_list.append(industrial_card_view)

        industry_dict['mines'] = mines_list

        for factory in country.factories + country.military_factories:
            industrial_card_view = IndustrialCardView(
                factory.name,factory.link_img,round(factory.production_speed,2),
                round(factory.active_number * factory.production_speed * factories_modifiers),
                factory.price_build,factory.workers,factory.number,factory.active_number,factory.number * factory.workers,
                [TableRowGoodsView(item.link_img,item.name,item.value) for item in factory.need_goods]
            )
            factories_list.append(industrial_card_view)

        industry_dict['factories'] = factories_list[:18]
        industry_dict['military_factories'] = factories_list[18:]
        finish = time.time()
        return industry_dict

    def get_warehouses(self, user_id: str):
        start = time.time()
        user = User.objects(id=user_id).first()
        country = Country.objects(id=user.country.id).first()

        warehouses_list = []
        for warehouse in country.warehouses:
            warehouse_card_view = WarehouseCardView(
                warehouse.goods.name,warehouse.goods.link_img,
                round(warehouse.goods.value,2),warehouse.capacity,
                round(warehouse.filling_speed,2),warehouse.level,warehouse.max_level,
                warehouse.price_upgrade,warehouse.added_capacity,warehouse.increase_price
            )
            warehouses_list.append(warehouse_card_view)

        finish = time.time()
        return warehouses_list

    def get_cache_politics_laws(self, user_id: str):
        user = User.objects(id=user_id).first()
        country = Country.objects(id=user.country.id).first()
        cache = Cache.objects().first()
        if cache.politics != '':
            politics_view = json.loads(cache.politics)
            politics_view['selected_laws'] = country.adopted_laws
            return politics_view
        else:
            return self.get_politics_laws(user_id)

    def get_politics_laws(self, user_id: str):
        user = User.objects(id=user_id).first()
        country = Country.objects(id=user.country.id).first()
        conscription_laws = []
        pop_laws = []
        for law in Law.objects():
            if 'Conscript law:' in law.name:
                conscription_percent = re.split(' ',law.description)[-1]
                conscription_laws.append(LawView(law.name,law.description,[ModifierView(mod.value,mod.address_to) for mod in law.modifiers],conscription_percent))
            else:
                pop_laws.append(LawView(law.name,f' ({law.description})',[ModifierView(mod.value,mod.address_to) for mod in law.modifiers]))
        return PoliticsView(country.adopted_laws,conscription_laws,pop_laws)

    def get_population(self, user_id: str):
        start = time.time()
        user = User.objects(id=user_id).first()
        country = Country.objects(id=user.country.id).first()
        modifiers_view_list = []
        population_modifiers = 0  # -> 1(100%)

        for mod in country.population.modifiers:
            modifiers_view_list.append(ModifierView(round(mod.value,2),mod.address_from))
            population_modifiers += mod.value
        modifiers_view_list.append(ModifierView(country.population.basic_percent_growth_rate,'basic percent'))

        percent_total_progress = round((population_modifiers+country.population.basic_percent_growth_rate),2)

        pie_chart_labels = ['Farmers','Miners','Workers','Solders','Free','Others']
        pie_chart_data = [
            country.population.farmers,country.population.miners,
            country.population.factory_workers,country.population.solders,
            country.population.free_people,country.population.total_population*(country.population.min_percent_others/100)
        ]

        population_view = PopulationView(
            country.population.total_population,country.population.farmers,
            country.population.miners,country.population.factory_workers,
            country.population.solders,country.population.free_people,
            country.population.others,percent_total_progress,modifiers_view_list,
            pie_chart_data,pie_chart_labels
        )
        finish = time.time()
        return population_view

    def get_cache_trade(self,user_id: str):
        cache = Cache.objects().first()
        if cache.trade != '':
            trade_view = json.loads(cache.trade)
            user = User.objects(id=user_id).first()
            target_country = Country.objects(id=user.country.id).first()
            for trade_card in trade_view:
                warehouse = next(filter(lambda x:x.goods.name==trade_card['name'],target_country.warehouses),None)
                trade_card['warehouse_has'] = round(warehouse.goods.value,2)
                trade_card['warehouse_capacity'] = warehouse.capacity
            return trade_view
        else:
            return self.get_trade(user_id)

    def get_trade(self, user_id: str):
        start = time.time()
        user = User.objects(id=user_id).first()
        goods = Trade.objects
        target_country = Country.objects(id=user.country.id).first()
        countries = Country.objects

        trade_cards_view_list = []
        production_data = GameService().get_table_world_place_production()

        for item in goods:
            data_top_producer = []
            if len(production_data[item.name]) > 2:
                data_top_producer_buffer = production_data[item.name][:3]
            else:
                data_top_producer_buffer = production_data[item.name]

            for producer in data_top_producer_buffer:
                producer_view = TableRowProducerView(
                    countries.filter(name=producer[0]).first().link_img,
                    producer[0],producer[1]
                )
                data_top_producer.append(producer_view)

            data_top_producer.sort(key=lambda x: x.number, reverse=True)
            warehouse = next(filter(lambda x:x.goods.name==item.name,target_country.warehouses),None)
            price_list = [round(history.value,2) for history in item.history_price]

            if not price_list:
                price_list = [round(item.price_now,2)]

            chart_price_goods = ChartPriceGoods(
                price_list,[history.time.strftime("%H:%M:%S") for history in item.history_price],
                item.name,max(price_list) * 1.2, min(price_list) * 0.9
            )

            trade_card_view = TradeCardView(
                item.name,warehouse.goods.link_img,
                round(item.price_now),round(warehouse.goods.value,2),warehouse.capacity,data_top_producer,chart_price_goods
            )
            trade_cards_view_list.append(trade_card_view)
        finish = time.time()
        return trade_cards_view_list

    def get_army(self, user_id: str):
        start = time.time()
        user = User.objects(id=user_id).first()
        country = Country.objects(id=user.country.id).first()
        army = country.army.units
        army_units = ArmyUnit.objects()
        army_view_list = []
        sum_attack_modifiers = GameService().get_army_modifiers(country,'attack')
        sum_defence_modifiers = GameService().get_army_modifiers(country,'defence')

        for name_unit in army:
            if name_unit == 'Infantry':
                warehouse = next(filter(lambda x:x.goods.name=='Infantry equipment',country.warehouses),None)
                weapons = warehouse.goods.value
                storage_capacity = warehouse.capacity

            elif name_unit == 'Artillery':
                warehouse = next(filter(lambda x:x.goods.name=='Artillery',country.warehouses),None)
                weapons = warehouse.goods.value
                storage_capacity = warehouse.capacity

            elif name_unit == 'Anti-tank gun':
                warehouse = next(filter(lambda x:x.goods.name=='Anti-tank gun',country.warehouses),None)
                weapons = warehouse.goods.value
                storage_capacity = warehouse.capacity

            elif name_unit == 'Air defense':
                warehouse = next(filter(lambda x:x.goods.name=='Air defense',country.warehouses),None)
                weapons = warehouse.goods.value
                storage_capacity = warehouse.capacity

            elif name_unit == 'Tank':
                warehouse = next(filter(lambda x:x.goods.name=='Tanks',country.warehouses),None)
                weapons = warehouse.goods.value
                storage_capacity = warehouse.capacity

            elif name_unit == 'Aviation':
                warehouse = next(filter(lambda x:x.goods.name=='Aviation',country.warehouses),None)
                weapons = warehouse.goods.value
                storage_capacity = warehouse.capacity

            unit = army_units.filter(name=name_unit).first()
            unit_characteristic_view_list = [UnitCharacteristicView(item.unit_name,
                item.attack_value * sum_attack_modifiers,
                item.defence_value * sum_defence_modifiers)
                for item in unit.unit_characteristic.values()]

            modifiers = [ModifierView(mod.value,mod.address_from+' TO ATTACK') for mod in country.army.attack_modifiers]
            modifiers.extend([ModifierView(mod.value,mod.address_from+' TO DEFENCE') for mod in country.army.defence_modifiers])

            army_card_view = ArmyCardView(
                name_unit,unit.link_img,army[name_unit],unit.need_peoples,
                unit.maintenance_price,unit.maintenance_price*army[name_unit],
                country.army.reserve_military_manpower,round(weapons,2),storage_capacity,modifiers,unit_characteristic_view_list
            )
            army_view_list.append(army_card_view)
        finish = time.time()
        return army_view_list

class FQAViewService:
    def get_FQA(self):
        return [dict(question=fqa_obj.question,answer=fqa_obj.answer) for fqa_obj in FQA.objects()]

class NewsViewService:
    def get_news(self):
        start = time.time()
        news_view_list = [NewsView(news.title,str(news.date),re.split(';',news.text)) for news in News.objects]
        finish = time.time()
        return news_view_list

class PlayerViewService:
    def get_account(self,user_id: str):
        user = User.objects(id=user_id).first()
        country = Country.objects(id=user.country.id).first()
        game_service = GameService()
        days_in_game = (datetime.utcnow() - user.date_registration).days
        date_reg = user.date_registration.strftime('%d.%m.%Y')
        account_view = AccountView(
            user_id,country.link_img,country.name,game_service.get_total_profit(country),
            game_service.get_economic_place(country.name),game_service.get_army_place(country.name),
            user.username,user.email,date_reg,days_in_game
        )
        return account_view

    def get_player(self, username: str):
        start = time.time()
        user = User.objects(username=username).first()
        if user is not None:
            country = Country.objects(id=user.country.id).first()

            player_view = PlayerView(
                country.link_img,country.name,user.username,GameService().get_economic_place(country.name),
                GameService().get_army_place(country.name),country.budget.money,country.population.total_population,
                sum([farm.number for farm in country.farms]),sum([mine.number for mine in country.mines]),
                sum([sum([factory.number for factory in country.factories]),sum([factory.number for factory in country.military_factories])]),
                country.population.solders,country.army.units)
            finish = time.time()
            return player_view

    def get_top_players(self,number: int):
        view_list = [self.get_player(user.username) for user in User.objects()]
        if number > len(view_list):
            number = len(view_list)
        return sorted(view_list,key=lambda x: x.economic_place)[:number]

    def get_view_page(self,user_id: str):
        user = User.objects(id=user_id).first()
        country = Country.objects(id=user.country.id).first()
        economic_place = GameService().get_economic_place(country.name)
        army_place = GameService().get_army_place(country.name)
        cache = Cache.objects().first()
        if cache.top_players != '':
            top_players = json.loads(cache.top_players)
        else:
            global_settings = GlobalSettings.objects().first()
            top_players = self.get_top_players(global_settings.number_top_players)
        return TopPlayersPage(economic_place,army_place,top_players)
