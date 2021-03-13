from datetime import datetime
import random,re
from django.utils import timezone
from polls.exceptions import *
from polls.models import Country, Modifier, Trade, Law, ArmyUnit, History, GlobalSettings, User, IndustrialBuilding

from polls.view_models.army import ResultWarView, ItemWarResult

class GameService:

    def update_budget(self, country: Country):
        time_sleep_sec = (datetime.utcnow() - country.budget.date_last_budget_update).seconds

        total_taxes_profit = self.get_pop_taxes_profit(country) + self.get_farms_taxes_profit(country) + self.get_mines_taxes_profit(country) + self.get_factories_taxes_profit(country)
        military_expenses = sum([country.army.units[unit.name] * unit.maintenance_price for unit in ArmyUnit.objects()])
        total_taxes_profit *= (time_sleep_sec/3600)
        military_expenses *= (time_sleep_sec/3600)

        if (total_taxes_profit > 1 or total_taxes_profit < -1) and (military_expenses > 1 or military_expenses == 0):
            country.budget.date_last_budget_update = datetime.utcnow()

            country.budget.total_profit += total_taxes_profit
            country.budget.total_expenses += military_expenses
            country.budget.money += (total_taxes_profit - military_expenses)

            if (datetime.utcnow() - country.budget.date_last_budget_chart_update).seconds > 3600:
                country.budget.date_last_budget_chart_update = datetime.utcnow()

                global_settings = GlobalSettings.objects().first()

                if len(country.budget.profit_history) > global_settings.length_budget_graphics:
                    country.budget.profit_history.pop(0)
                country.budget.profit_history.append(History(name='', value=country.budget.total_profit, time=timezone.now()))

                if len(country.budget.expenses_history) > global_settings.length_budget_graphics:
                    country.budget.expenses_history.pop(0)
                country.budget.expenses_history.append(
                    History(name='', value=country.budget.total_expenses, time=timezone.now()))

                if len(country.budget.budget_history) > global_settings.length_budget_graphics:
                    country.budget.budget_history.pop(0)
                country.budget.budget_history.append(History(name='', value=country.budget.money, time=timezone.now()))

                country.budget.total_profit = 0
                country.budget.total_expenses = 0

                user = User.objects(country=country.id).first()
                if country.budget.money < global_settings.low_budget and global_settings.email_notification and user.settings['low budget'] and (datetime.utcnow() - country.budget.date_last_budget_notification).seconds/60 > global_settings.frequency_email_notification:
                    from polls.services.system_service import SystemService, EmailEvent
                    country.budget.date_last_budget_notification = datetime.utcnow()
                    SystemService().send_notification([user.email],EmailEvent.LOW_BUDGET,country.budget.money)

        country.save()

    def get_army_modifiers(self,country: Country,type_modifiers: str):
        if type_modifiers == 'attack' and country.army.attack_modifiers is not None:
            attack_modifiers = sum([mod.value for mod in country.army.attack_modifiers])
            return (attack_modifiers + 100) / 100

        if type_modifiers == 'defence' and country.army.defence_modifiers is not None:
            defence_modifiers = sum([mod.value for mod in country.army.defence_modifiers])
            return (defence_modifiers + 100) / 100

        return 1

    def get_population_modifiers(self,country: Country):
        if country.population.modifiers is not None:
            pop_modifiers = sum([mod.value for mod in country.population.modifiers])
            return (pop_modifiers + country.population.basic_percent_growth_rate + 100) / 100
        return (country.population.basic_percent_growth_rate + 100) / 100

    def get_industry_modifiers(self,country: Country,address_to: str):
        if country.industry_modifiers is not None:
            industry_modifiers = sum([mod.value for mod in country.industry_modifiers if mod.address_to == address_to or mod.address_to == 'industry'])
            return (industry_modifiers + 100) / 100 if industry_modifiers >= -100 else 0
        return 1

    def update_industry(self, country: Country):
        farms_modifiers = self.get_industry_modifiers(country, 'farms')
        mines_modifiers = self.get_industry_modifiers(country, 'mines')
        factories_modifiers = self.get_industry_modifiers(country, 'factories')

        for farm in country.farms:
            if farm.number != 0:
                time_sleep_sec = (datetime.utcnow() - farm.date_last_industry_update).seconds
                if time_sleep_sec > 1:
                    name_warehouse = self.get_name_goods_from_building(farm.name)
                    warehouse = [item for item in country.warehouses if item.goods.name == name_warehouse][0]
                    total_production = (farm.number * farm.production_speed * farms_modifiers) * time_sleep_sec / 3600

                    farm.date_last_industry_update = datetime.utcnow()
                    warehouse.goods.value += total_production
                    farm.active_number = farm.number

                    if warehouse.goods.value > warehouse.capacity:
                        warehouse.goods.value = warehouse.capacity

        for mine in country.mines:
            if mine.number != 0:
                time_sleep_sec = (datetime.utcnow() - mine.date_last_industry_update).seconds
                if time_sleep_sec > 1:
                    name_warehouse = self.get_name_goods_from_building(mine.name)
                    warehouse = [item for item in country.warehouses if item.goods.name == name_warehouse][0]
                    total_production = (mine.number * mine.production_speed * mines_modifiers) * time_sleep_sec / 3600

                    mine.date_last_industry_update = datetime.utcnow()
                    warehouse.goods.value += total_production
                    mine.active_number = mine.number

                    if warehouse.goods.value > warehouse.capacity:
                        warehouse.goods.value = warehouse.capacity

        for factory in country.factories + country.military_factories:
            if factory.number != 0:
                time_sleep_sec = (datetime.utcnow() - factory.date_last_industry_update).seconds
                if time_sleep_sec > 1:
                    resources_dict = {}
                    for need_goods in factory.need_goods:
                        warehouse = [item for item in country.warehouses if item.goods.name == need_goods.name][0]
                        need_resources = need_goods.value * factory.number * time_sleep_sec / 3600
                        if need_resources <= warehouse.goods.value:
                            resources_dict[need_goods.name] = need_resources
                        else:
                            resources_dict[need_goods.name] = warehouse.goods.value - need_resources  # value < 0

                    max_deficit_name_resource = min(resources_dict,key=resources_dict.get)
                    deficit_goods = next(filter(lambda x: x.name == max_deficit_name_resource, factory.need_goods), None)
                    active_factories = factory.number + (int(resources_dict[max_deficit_name_resource] / (deficit_goods.value * time_sleep_sec / 3600)) - 1)  # actually ...+(-value)
                    factory.active_number = active_factories

                    if factory.active_number > factory.number:
                        factory.active_number = factory.number

                    for need_goods in factory.need_goods:
                        warehouse = [item for item in country.warehouses if item.goods.name == need_goods.name][0]
                        warehouse.goods.value -= factory.active_number * need_goods.value * time_sleep_sec / 3600

                    product_name = self.get_name_goods_from_building(factory.name)
                    warehouse = [item for item in country.warehouses if item.goods.name == product_name][0]
                    total_production = (factories_modifiers * factory.active_number * factory.production_speed) * time_sleep_sec / 3600

                    factory.date_last_industry_update = datetime.utcnow()
                    warehouse.goods.value += total_production
                    if warehouse.goods.value > warehouse.capacity:
                        warehouse.goods.value = warehouse.capacity

        self.update_warehouses_filling_speed(country)
        country.save()

    def update_population(self, country: Country):
        pop_modifiers = self.get_population_modifiers(country)

        population_before_update = country.population.total_population
        time_sleep_sec = (datetime.utcnow() - country.population.date_last_population_update).seconds
        population_after_update = population_before_update * (pop_modifiers**(time_sleep_sec/3600))
        total_growth_people = (population_after_update - population_before_update)

        if total_growth_people >= 1:
            country.population.date_last_population_update = datetime.utcnow()
            country.population.total_population = population_after_update

            growth_others = (country.population.min_percent_others / 100) * total_growth_people
            country.population.others += growth_others
            country.population.free_people += (total_growth_people - growth_others)

            solders_before_update = country.population.solders
            country.population.solders = (country.population.free_people * (country.army.conscript_law_value / 100))

            country.population.free_people -= (country.population.solders - solders_before_update)
            country.army.reserve_military_manpower += (country.population.solders - solders_before_update)

            country.population.total_population = country.population.farmers + \
                                                  country.population.miners + country.population.factory_workers + \
                                                  country.population.solders + country.population.free_people + \
                                                  country.population.others

            global_settings = GlobalSettings.objects().first()

            if (datetime.utcnow() - country.population.date_last_population_chart_update).seconds > 30*60:
                country.population.date_last_population_chart_update = datetime.utcnow()
                if len(country.population.population_history) > global_settings.length_population_graphics:
                    country.population.population_history.pop(0)
                country.population.population_history.append(History(name='', value=pop_modifiers * 100 - 100, time=timezone.now()))

            user = User.objects(country=country.id).first()
            if country.population.total_population < global_settings.low_population and global_settings.email_notification and user.settings['low population'] and (datetime.utcnow() - country.population.date_last_population_notification).seconds/60 > global_settings.frequency_email_notification:
                from polls.services.system_service import SystemService, EmailEvent
                country.population.date_last_population_notification = datetime.utcnow()
                SystemService().send_email([user.email],EmailEvent.LOW_POPULATION,country.population.total_population)

            country.save()

    def update_price_goods(self):
        global_settings = GlobalSettings.objects().first()
        for goods in Trade.objects():
            new_price = round(random.uniform(-global_settings.goods_price_scatter*goods.default_price, global_settings.goods_price_scatter*goods.default_price),2)
            goods.price_now += new_price
            if goods.price_now < 0:
                goods.price_now = goods.default_price
            if len(goods.history_price) > global_settings.length_goods_price_graphics:
                goods.history_price.pop(0)
            goods.history_price.append(History(name='', value=goods.price_now, time=timezone.now()))
            goods.save()

    def set_taxes(self, country: Country, type_taxes: str, new_value: int):
        if type_taxes == 'population_taxes':
            if 100 >= new_value >= 0:
                country.budget.population_taxes = new_value
                existing_modifiers = country.population.modifiers.filter(address_from='population taxes')
                if new_value == 50 and existing_modifiers.count() != 0:
                    existing_modifiers.delete()
                elif existing_modifiers.count() == 0:
                    country.population.modifiers.append(Modifier(value=0.04 * new_value - 2, address_from='population taxes'))
                else:
                    existing_modifiers.update(value=-0.04 * new_value + 2)
            else: raise TaxValueNotInRangeError

        elif type_taxes == 'farms_taxes':
            if 100 >= new_value >= 0:
                country.budget.farms_taxes = new_value
                existing_modifiers = country.industry_modifiers.filter(address_from='farms taxes')
                if new_value == 50 and existing_modifiers.count() != 0:
                    existing_modifiers.delete()
                elif existing_modifiers.count() == 0:
                    country.industry_modifiers.append(Modifier(value=-0.6 * new_value + 30, address_from='farms taxes', address_to='farms'))
                else:
                    existing_modifiers.update(value=-0.6 * new_value + 30)
            else: raise TaxValueNotInRangeError

        elif type_taxes == 'mines_taxes':
            if 100 >= new_value >= 0:
                country.budget.mines_taxes = new_value
                existing_modifiers = country.industry_modifiers.filter(address_from='mines taxes')
                if new_value == 50 and existing_modifiers.count() != 0:
                    existing_modifiers.delete()
                elif existing_modifiers.count() == 0:
                    country.industry_modifiers.append(
                        Modifier(value=-0.6 * new_value + 30, address_from='mines taxes', address_to='mines'))
                else:
                    existing_modifiers.update(value=-0.6 * new_value + 30)
            else: raise TaxValueNotInRangeError

        elif type_taxes == 'factories_taxes' and 100 >= new_value >= 0:
            if 100 >= new_value >= 0:
                country.budget.factories_taxes = new_value
                existing_modifiers = country.industry_modifiers.filter(address_from='factories taxes')
                if new_value == 50 and existing_modifiers.count() != 0:
                    existing_modifiers.delete()
                elif existing_modifiers.count() == 0:
                    country.industry_modifiers.append(
                        Modifier(value=-0.6 * new_value + 30, address_from='factories taxes', address_to='factories'))
                else:
                    existing_modifiers.update(value=-0.6 * new_value + 30)
            else: raise TaxValueNotInRangeError

        elif type_taxes == 'military_taxes' and 100 >= new_value >= 0:
            if 100 >= new_value >= 0:
                country.budget.military_taxes = new_value
                existing_attack_modifiers = country.army.attack_modifiers.filter(address_from='army taxes')
                existing_defence_modifiers = country.army.defence_modifiers.filter(address_from='army taxes')
                if new_value == 50 and existing_attack_modifiers.count() != 0:
                    existing_attack_modifiers.delete()
                    if existing_defence_modifiers.count() != 0:
                        existing_defence_modifiers.delete()
                elif existing_attack_modifiers.count() == 0:
                    country.army.attack_modifiers.append(Modifier(value=-new_value + 50, address_from='army taxes'))
                    country.army.defence_modifiers.append(Modifier(value=-new_value + 50, address_from='army taxes'))
                else:
                    existing_attack_modifiers.update(value=-new_value + 50)
                    existing_defence_modifiers.update(value=-new_value + 50)
            else: raise TaxValueNotInRangeError

        else: raise UnknownNameTaxError(type_taxes)

        self.update_warehouses_filling_speed(country)
        country.save()

    def upgrade_technology(self, country: Country, technology_name: str):
        technology = country.technologies.filter(name=technology_name).first()
        if country.budget.money >= technology.price_upgrade:
            if technology.level < technology.max_level:
                country.budget.total_expenses += technology.price_upgrade
                country.budget.money -= technology.price_upgrade
                technology.price_upgrade *= technology.increase_price
                technology.level += 1

                if technology.name == 'Medicine technology':
                    existing_modifiers = country.population.modifiers.filter(address_from=technology.name)
                    if existing_modifiers.count() == 0:
                        country.population.modifiers.append(Modifier(value=technology.modifiers[0].value,
                                                                     address_from=technology.name))
                    else:
                        existing_modifiers.update(value=technology.modifiers[0].value * technology.level)

                elif technology.name == 'Computers technology':
                    existing_modifiers = country.industry_modifiers.filter(address_from=technology.name)
                    if existing_modifiers.count() == 0:
                        country.industry_modifiers.append(Modifier(value=technology.modifiers[0].value,
                                                                   address_from=technology.name))
                    else:
                        existing_modifiers.update(value=technology.modifiers[0].value * technology.level)
                    self.update_warehouses_filling_speed(country)

                elif technology.name == 'Upgrade weapons':
                    existing_modifiers = country.army.attack_modifiers.filter(address_from=technology.name)
                    if existing_modifiers.count() == 0:
                        country.army.attack_modifiers.append(Modifier(value=technology.modifiers[0].value,
                                                                      address_from=technology.name))
                    else:
                        existing_modifiers.update(value=technology.modifiers[0].value * technology.level)

                elif technology.name == 'Upgrade defence system':
                    existing_modifiers = country.army.defence_modifiers.filter(address_from=technology.name)
                    if existing_modifiers.count() == 0:
                        country.army.defence_modifiers.append(Modifier(value=technology.modifiers[0].value,
                                                                       address_from=technology.name))
                    else:
                        existing_modifiers.update(value=technology.modifiers[0].value * technology.level)

                else: raise UnknownNameTechnologyError(technology_name)
            else: raise MaxLevelError(technology.max_level)
        else: raise LowBudgetError
        country.save()

    def __calculate_build_of_industrial_building(self, country: Country, building: IndustrialBuilding, type_building: str):
        if country.budget.money >= building.price_build:
            if country.population.free_people >= building.workers:
                country.budget.total_expenses += building.price_build
                country.budget.money -= building.price_build
                country.population.free_people -= building.workers
                building.number += 1
                building.date_last_industry_update = datetime.utcnow()
                country.army.reserve_military_manpower = country.population.free_people * (country.army.conscript_law_value / 100)
                country.population.free_people *= (1 - country.army.conscript_law_value / 100)
                country.population.solders = country.army.reserve_military_manpower + self.get_number_soldiers_from_units(country)
                if type_building == 'farm': country.population.farmers += building.workers
                elif type_building == 'mine' or type_building == 'well': country.population.miners += building.workers
                elif type_building == 'factory': country.population.factory_workers += building.workers
                else: raise UnknownTypeBuildingError(type_building)
            else: raise FreePeopleError
        else: raise LowBudgetError

    def build_industry(self, country: Country, name_building: str):
        print(name_building)
        type_building = re.split(r' ', name_building)[-1]
        print(type_building)
        if type_building == 'farm':
            farm = country.farms.filter(name=name_building).first()
            self.__calculate_build_of_industrial_building(country, farm, type_building)

        elif type_building == 'mine' or type_building == 'well':
            mine = country.mines.filter(name=name_building).first()
            self.__calculate_build_of_industrial_building(country, mine, type_building)

        elif type_building == 'factory':
            factory = country.factories.filter(name=name_building).first()
            if factory is not None: # it's a civil factory
                self.__calculate_build_of_industrial_building(country, factory, type_building)
            else: # it's a military factory
                factory = country.military_factories.filter(name=name_building).first()
                self.__calculate_build_of_industrial_building(country, factory, type_building)

        else: raise UnknownTypeBuildingError(type_building)

        country.save()

    def __calculate_remove_of_industrial_building(self, country: Country, building: IndustrialBuilding, type_building: str):
        if building.number > 0:
            country.population.free_people += building.workers
            building.number -= 1
            if building.active_number > 0:
                building.active_number -=1
            country.army.reserve_military_manpower = country.population.free_people * (country.army.conscript_law_value / 100)
            country.population.free_people *= (1 - country.army.conscript_law_value / 100)
            country.population.solders = country.army.reserve_military_manpower + self.get_number_soldiers_from_units(country)
            if type_building == 'farm': country.population.farmers -= building.workers
            elif type_building == 'mine' or type_building == 'well': country.population.miners -= building.workers
            elif type_building == 'factory': country.population.factory_workers -= building.workers
            else: raise UnknownTypeBuildingError(type_building)

    def remove_industry(self, country: Country, name_building: str):
        type_building = re.split(r' ', name_building)[-1]

        if type_building == 'farm':
            farm = country.farms.filter(name=name_building).first()
            self.__calculate_remove_of_industrial_building(country, farm, type_building)

        elif type_building == 'mine' or type_building == 'well':
            mine = country.mines.filter(name=name_building).first()
            self.__calculate_remove_of_industrial_building(country, mine, type_building)

        elif type_building == 'factory':
            factory = country.factories.filter(name=name_building).first()
            if factory is not None:
                self.__calculate_remove_of_industrial_building(country, factory, type_building)
            else:
                factory = country.military_factories.filter(name=name_building).first()
                self.__calculate_remove_of_industrial_building(country, factory, type_building)

        else: raise UnknownTypeBuildingError(type_building)

        self.update_warehouses_filling_speed(country)
        country.save()

    def update_warehouses_filling_speed(self, country: Country):
        farms_modifiers = self.get_industry_modifiers(country, 'farms')
        mines_modifiers = self.get_industry_modifiers(country, 'mines')
        factories_modifiers = self.get_industry_modifiers(country, 'factories')

        need_resources = {}

        for warehouse in country.warehouses:
            warehouse.filling_speed = 0

        for farm in country.farms:
            product_name = self.get_name_goods_from_building(farm.name)
            need_resources[product_name] = 0
            if farm.number != 0:
                warehouse = [item for item in country.warehouses if item.goods.name == product_name][0]
                warehouse.filling_speed = farms_modifiers * farm.production_speed * farm.number

        for mine in country.mines:
            product_name = self.get_name_goods_from_building(mine.name)
            need_resources[product_name] = 0
            if mine.number != 0:
                warehouse = [item for item in country.warehouses if item.goods.name == product_name][0]
                warehouse.filling_speed = mines_modifiers * mine.production_speed * mine.number

        all_factories = country.factories + country.military_factories

        for factory in all_factories:
            product_name = self.get_name_goods_from_building(factory.name)
            need_resources[product_name] = 0

        for factory in all_factories:
            for goods in factory.need_goods:
                need_resources[goods.name] += goods.value * factory.active_number

        for factory in all_factories:
            if factory.number != 0 and factory.active_number != 0:
                product_name = self.get_name_goods_from_building(factory.name)
                warehouse = [item for item in country.warehouses if item.goods.name == product_name][0]
                warehouse.filling_speed = factories_modifiers * factory.production_speed * factory.active_number
                for goods in factory.need_goods:
                    warehouse = [item for item in country.warehouses if item.goods.name == goods.name][0]
                    warehouse.filling_speed -= need_resources[goods.name]

        country.save()

    def get_number_soldiers_from_units(self, country: Country):
        number, army_units, army = 0, ArmyUnit.objects(), country.army.units
        number = sum([army[unit] * army_units.filter(name=unit).first().need_peoples for unit in army])
        return number

    def upgrade_warehouse(self, country: Country, name_goods: str):
        warehouse = [item for item in country.warehouses if item.goods.name == name_goods][0]
        if country.budget.money >= warehouse.price_upgrade:
            if warehouse.level < warehouse.max_level:
                country.budget.total_expenses += warehouse.price_upgrade
                country.budget.money -= warehouse.price_upgrade
                warehouse.price_upgrade *= warehouse.increase_price
                warehouse.level += 1
                warehouse.capacity += warehouse.added_capacity
                country.save()
            else: raise MaxLevelError(warehouse.max_level)
        else: raise LowBudgetError

    def set_politics_law(self, country: Country, name_law: str):
        law = Law.objects(name=name_law).first()

        if country.budget.money >= law.price:

            if not name_law in country.adopted_laws:

                if name_law == 'Free medicine':
                    country.population.modifiers.append(Modifier(value=5, address_from=name_law))
                    country.industry_modifiers.append(Modifier(value=-10, address_from=name_law, address_to='industry'))

                elif name_law == 'Isolation':
                    country.population.modifiers.append(Modifier(value=-5, address_from=name_law))
                    country.industry_modifiers.append(Modifier(value=-5, address_from=name_law, address_to='industry'))
                    country.army.defence_modifiers.append(Modifier(value=15, address_from=name_law))

                elif name_law == 'Free housing':
                    country.population.modifiers.append(Modifier(value=5, address_from=name_law))
                    country.industry_modifiers.append(Modifier(value=-10, address_from=name_law, address_to='industry'))
                    country.army.attack_modifiers.append(Modifier(value=-10, address_from=name_law))
                    country.army.defence_modifiers.append(Modifier(value=10, address_from=name_law))

                elif name_law == 'Free education':
                    country.population.modifiers.append(Modifier(value=-2, address_from=name_law))
                    country.industry_modifiers.append(Modifier(value=15, address_from=name_law, address_to='industry'))
                    country.army.attack_modifiers.append(Modifier(value=-10, address_from=name_law))

                else: raise UnknownNameLawError(name_law)

                country.budget.total_expenses += law.price
                country.budget.money -= law.price
                country.adopted_laws.append(name_law)
                self.update_warehouses_filling_speed(country)
                country.save()

        else: raise LowBudgetError

    def __update_conscript_law(self, country: Country, name_law: str, law: Law, conscript_law_value: float,
                               pop_mod: Modifier=None, indus_mod: Modifier=None, attack_mod: Modifier=None, def_mod: Modifier=None):
        self.__cansel_conscript_law(country)

        country.adopted_laws.append(name_law)
        country.budget.total_expenses += law.price
        country.budget.money -= law.price
        country.army.conscript_law_value = conscript_law_value
        country.army.reserve_military_manpower = country.population.free_people \
                                                 * country.army.conscript_law_value // 100
        country.population.free_people *= (1 - country.army.conscript_law_value // 100)

        if pop_mod is not None:
            country.population.modifiers.append(pop_mod)
        if indus_mod is not None:
            country.industry_modifiers.append(indus_mod)
        if attack_mod is not None:
            country.army.attack_modifiers.append(attack_mod)
        if def_mod is not None:
            country.army.defence_modifiers.append(def_mod)

    def set_conscript_law(self, country: Country, name_law: str):
        law = Law.objects(name=name_law).first()

        if country.budget.money >= law.price:

            if name_law == 'Conscript law: Elite':
                self.__update_conscript_law(country, name_law, law, 0.5,
                                            pop_mod=Modifier(value=-10, address_from=name_law),
                                            indus_mod=Modifier(value=10, address_from=name_law, address_to='industry'),
                                            attack_mod=Modifier(value=10, address_from=name_law),
                                            def_mod=Modifier(value=10, address_from=name_law))

            elif name_law == 'Conscript law: Volunteer':
                self.__update_conscript_law(country, name_law, law, 1.5)

            elif name_law == 'Conscript law: Limited Conscription':
                self.__update_conscript_law(country, name_law, law, 2.5,
                                            indus_mod=Modifier(value=-5, address_from=name_law, address_to='industry'),
                                            attack_mod=Modifier(value=5, address_from=name_law),
                                            def_mod=Modifier(value=5, address_from=name_law))

            elif name_law == 'Conscript law: Extensive Conscription':
                self.__update_conscript_law(country, name_law, law, 5,
                                            indus_mod=Modifier(value=-5, address_from=name_law, address_to='industry'))

            elif name_law == 'Conscript law: Service by Requirement':
                self.__update_conscript_law(country, name_law, law, 10,
                                            pop_mod=Modifier(value=-5, address_from=name_law),
                                            indus_mod=Modifier(value=5, address_from=name_law, address_to='industry'),
                                            attack_mod=Modifier(value=-5, address_from=name_law),
                                            def_mod=Modifier(value=-5, address_from=name_law))

            elif name_law == 'Conscript law: All Adults Serve':
                self.__update_conscript_law(country, name_law, law, 20,
                                            pop_mod=Modifier(value=-10, address_from=name_law),
                                            indus_mod=Modifier(value=-15, address_from=name_law, address_to='industry'),
                                            attack_mod=Modifier(value=-5, address_from=name_law),
                                            def_mod=Modifier(value=-5, address_from=name_law))

            elif name_law == 'Conscript law: All with weapons':
                self.__update_conscript_law(country, name_law, law, 30,
                                            pop_mod=Modifier(value=-15, address_from=name_law),
                                            indus_mod=Modifier(value=-35, address_from=name_law, address_to='industry'),
                                            attack_mod=Modifier(value=-15, address_from=name_law),
                                            def_mod=Modifier(value=-10, address_from=name_law))

            else: raise UnknownNameConscriptLawError(name_law)

            self.update_warehouses_filling_speed(country)
            country.save()

        else: raise LowBudgetError

    def __cansel_conscript_law(self, country: Country):
        conscript_laws = ['Conscript law: Elite', 'Conscript law: Volunteer',
                          'Conscript law: Limited Conscription', 'Conscript law: Extensive Conscription',
                          'Conscript law: Service by Requirement', 'Conscript law: All Adults Serve',
                          'Conscript law: All with weapons']

        for str_law in conscript_laws:
            country.population.modifiers.filter(address_from=str_law).delete()
            country.industry_modifiers.filter(address_from=str_law).delete()
            country.army.attack_modifiers.filter(address_from=str_law).delete()
            country.army.defence_modifiers.filter(address_from=str_law).delete()
            if str_law in country.adopted_laws:
                country.adopted_laws.remove(str_law)

    def cancel_politics_law(self, country: Country, name_law: str):
        law = Law.objects(name=name_law).first()

        if country.budget.money >= law.price:

            if name_law in country.adopted_laws:

                country.budget.total_expenses += law.price
                country.budget.money -= law.price
                country.adopted_laws.remove(name_law)

                if name_law == 'Free medicine':
                    country.population.modifiers.remove(Modifier(value=5, address_from=name_law))
                    country.industry_modifiers.remove(Modifier(value=-10, address_from=name_law, address_to='industry'))

                elif name_law == 'Isolation':
                    country.population.modifiers.remove(Modifier(value=-5, address_from=name_law))
                    country.industry_modifiers.remove(Modifier(value=-5, address_from=name_law, address_to='industry'))
                    country.army.defence_modifiers.remove(Modifier(value=15, address_from=name_law))

                elif name_law == 'Free housing':
                    country.population.modifiers.remove(Modifier(value=5, address_from=name_law))
                    country.industry_modifiers.remove(Modifier(value=-10, address_from=name_law, address_to='industry'))
                    country.army.attack_modifiers.remove(Modifier(value=-10, address_from=name_law))
                    country.army.defence_modifiers.remove(Modifier(value=10, address_from=name_law))

                elif name_law == 'Free education':
                    country.population.modifiers.remove(Modifier(value=-2, address_from=name_law))
                    country.industry_modifiers.remove(Modifier(value=15, address_from=name_law, address_to='industry'))
                    country.army.attack_modifiers.remove(Modifier(value=-10, address_from=name_law))

                self.update_warehouses_filling_speed(country)
                country.save()
            else: raise UnknownNameLawError(name_law)
        else: raise LowBudgetError

    def buy_goods(self, country: Country, name_goods: str, number: int):
        warehouse = [item for item in country.warehouses if item.goods.name == name_goods][0]
        max_number_buy = warehouse.capacity - warehouse.goods.value
        if 0 < number <= max_number_buy:
            price_goods = Trade.objects(name=name_goods).first().price_now * number
            if country.budget.money >= price_goods:
                country.budget.total_expenses += price_goods
                country.budget.money -= price_goods
                warehouse.goods.value += number
                country.save()
            else: raise LowBudgetError
        else: raise GoodsValueNotInRangeError(max_number_buy)

    def sell_goods(self, country: Country, name_goods: str, number: int):
        warehouse = [item for item in country.warehouses if item.goods.name == name_goods][0]
        if 0 < number <= warehouse.goods.value:
            price_goods = Trade.objects(name=name_goods).first().price_now * number
            country.budget.total_profit += price_goods
            country.budget.money += price_goods
            warehouse.goods.value -= number
            country.save()
        else: raise GoodsValueNotInRangeError(warehouse.goods.value)

    def edit_army(self, country: Country, name_unit: str, new_number: int):
        difference = country.army.units[name_unit] - new_number
        unit = ArmyUnit.objects(name=name_unit).first()

        if name_unit == 'Infantry': # names not equals!
            warehouse = [item for item in country.warehouses if item.goods.name == 'Infantry equipment'][0]
        elif name_unit == 'Artillery':
            warehouse = [item for item in country.warehouses if item.goods.name == 'Artillery'][0]
        elif name_unit == 'Anti-tank gun':
            warehouse = [item for item in country.warehouses if item.goods.name == 'Anti-tank gun'][0]
        elif name_unit == 'Air defense':
            warehouse = [item for item in country.warehouses if item.goods.name == 'Air defense'][0]
        elif name_unit == 'Tank': # names not equals!
            warehouse = [item for item in country.warehouses if item.goods.name == 'Tanks'][0]
        elif name_unit == 'Aviation':
            warehouse = [item for item in country.warehouses if item.goods.name == 'Aviation'][0]
        else: raise UnknownNameUnitError(name_unit)

        if warehouse.goods.value + difference >= 0 and new_number > 0:

            if country.army.reserve_military_manpower + (difference * unit.need_peoples) >= 0:

                country.army.reserve_military_manpower += difference * unit.need_peoples
                country.budget.military_expenses -= difference * unit.maintenance_price
                warehouse.goods.value += difference

                if warehouse.goods.value > warehouse.capacity:
                    warehouse.goods.value = warehouse.capacity

                country.army.units[name_unit] -= difference
                country.population.solders = country.army.reserve_military_manpower + self.get_number_soldiers_from_units(country)
                country.save()

            else: raise MilitaryManpowerError
        else: raise UnitError

    def calculate_war(self, attacking_country_name: str, defending_country_name: str):
        attacking_country = Country.objects(name=attacking_country_name).first()
        defending_country = Country.objects(name=defending_country_name).first()
        army_units = ArmyUnit.objects()
        res_war_view = ResultWarView()
        unit_solders_attacking_country_before_war = self.get_number_soldiers_from_units(attacking_country)
        unit_solders_defending_country_before_war = self.get_number_soldiers_from_units(defending_country)
        attacking_army_before_battle = attacking_country.army.units.copy()

        for unit in army_units:
            sorted_units_by_attack = sorted(unit.unit_characteristic.items(), key=lambda x: x[1].attack_value,
                                            reverse=True)
            if attacking_country.army.units[unit.name] != 0:
                for item in sorted_units_by_attack:
                    if defending_country.army.units[item[1].unit_name] != 0:

                        sum_attack_modifiers = self.get_army_modifiers(attacking_country,'attack')
                        attack_power = attacking_country.army.units[unit.name] * item[1].attack_value * sum_attack_modifiers
                        sum_defence_modifiers = self.get_army_modifiers(defending_country,'defence')
                        defence_power = defending_country.army.units[item[1].unit_name] * item[1].defence_value * sum_defence_modifiers
                        difference_power = defence_power - attack_power

                        if difference_power > 0:
                            attacking_country.army.units[unit.name] = 0
                            defending_country.army.units[item[1].unit_name] = (difference_power / sum_defence_modifiers) // item[
                                1].defence_value

                        elif difference_power < 0:
                            attacking_country.army.units[unit.name] = (-difference_power / sum_attack_modifiers) // item[
                                1].attack_value
                            defending_country.army.units[item[1].unit_name] = 0

                        elif difference_power == 0:
                            attacking_country.army.units[unit.name] = 0
                            defending_country.army.units[item[1].unit_name] = 0

        if next(filter(lambda x: x[1] != 0, defending_country.army.units.items()), None) is None:
            defending_country.army.losses += 1
            attacking_country.army.victories += 1
            res_war_view.prey.append(ItemWarResult('Money',defending_country.budget.money))
            attacking_country.budget.money += defending_country.budget.money
            defending_country.budget.money = 0
            warehouses_victory_country = attacking_country.warehouses

            for warehouse in defending_country.warehouses:
                some_warehouse = next(
                    filter(lambda x: x.goods.name == warehouse.goods.name, warehouses_victory_country), None)
                some_warehouse.goods.value += warehouse.goods.value

                if warehouse.goods.value != 0:
                    res_war_view.prey.append(ItemWarResult(warehouse.goods.name, warehouse.goods.value))
                warehouse.goods.value = 0

                if some_warehouse.goods.value > warehouse.capacity:
                    some_warehouse.goods.value = warehouse.capacity
        else:
            defending_country.army.victories += 1
            attacking_country.army.losses += 1
            res_war_view.victory_flag = False

        losses_people_attacking_country = unit_solders_attacking_country_before_war - self.get_number_soldiers_from_units(
            attacking_country)
        losses_people_defending_country = unit_solders_defending_country_before_war - self.get_number_soldiers_from_units(
            defending_country)
        attacking_country.population.solders = attacking_country.army.reserve_military_manpower + self.get_number_soldiers_from_units(
            attacking_country)
        defending_country.population.solders = defending_country.army.reserve_military_manpower + self.get_number_soldiers_from_units(
            defending_country)
        attacking_country.population.total_population -= losses_people_attacking_country
        defending_country.population.total_population -= losses_people_defending_country

        for name, number in attacking_country.army.units.items():
            if attacking_army_before_battle[name] != number:
                res_war_view.losses.append(ItemWarResult(name, attacking_army_before_battle[name] - number))

        attacking_country.budget.military_expenses = self.get_military_expenses(attacking_country)
        defending_country.budget.military_expenses = self.get_military_expenses(defending_country)

        global_settings = GlobalSettings.objects().first()
        defending_user = User.objects(country=defending_country.id).first()
        attacking_user = User.objects(country=attacking_country.id).first()
        if global_settings.email_notification and defending_user.settings['attacks']:
            from polls.services.system_service import SystemService, EmailEvent
            SystemService().send_notification([defending_user.email],EmailEvent.ATTACK,attacking_user.username)

        attacking_country.save()
        defending_country.save()
        return res_war_view

    def get_military_expenses(self, country: Country):
        military_expenses, army_units, army = 0,ArmyUnit.objects(),country.army.units
        military_expenses = sum([army[unit] * army_units.filter(name=unit).first().maintenance_price for unit in army])
        return military_expenses


    def get_farms_production_profit(self, country: Country):
        goods = Trade.objects()
        industry_modifiers = self.get_industry_modifiers(country,'farms')
        total_production_profit = 0
        for farm in country.farms:
            production_profit = farm.production_speed * farm.number * industry_modifiers * goods.filter(
                name=self.get_name_goods_from_building(farm.name)).first().price_now
            total_production_profit += production_profit
        return total_production_profit

    def get_mines_production_profit(self, country: Country):
        goods = Trade.objects()
        industry_modifiers = self.get_industry_modifiers(country,'mines')
        total_production_profit = 0
        for mine in country.mines:
            production_profit = mine.production_speed * mine.number * industry_modifiers * goods.filter(
                name=self.get_name_goods_from_building(mine.name)).first().price_now
            total_production_profit += production_profit
        return total_production_profit

    def get_factories_production_profit(self, country: Country):
        goods = Trade.objects()
        industry_modifiers = self.get_industry_modifiers(country,'factories')
        total_production_profit = 0
        for factory in country.factories + country.military_factories:
            if factory.number > 0:
                name_goods = self.get_name_goods_from_building(factory.name)
                expenses = 0
                if factory.need_goods:
                    for item in factory.need_goods:
                        expenses += item.value * goods.filter(name=item.name).first().price_now
                production_profit = factory.production_speed * factory.active_number * industry_modifiers * goods.filter(
                    name=name_goods).first().price_now - expenses
                total_production_profit += production_profit
        return total_production_profit

    def get_factories_profit(self, country: Country):
        production_profit = self.get_factories_production_profit(country)
        total_factories_profit = production_profit + self.get_factories_taxes_profit(country,production_profit)
        return total_factories_profit

    def get_mines_profit(self, country: Country):
        production_profit = self.get_mines_production_profit(country)
        total_mines_profit = production_profit + self.get_mines_taxes_profit(country, production_profit)
        return total_mines_profit

    def get_farms_profit(self, country: Country):
        production_profit = self.get_farms_production_profit(country)
        total_farms_profit = production_profit + self.get_farms_taxes_profit(country, production_profit)
        return total_farms_profit

    def get_army_taxes_profit(self, country: Country):
        global_settings = GlobalSettings.objects().first()
        return global_settings.army_taxes_profit_k * country.population.solders * (country.budget.military_taxes / 100)

    def get_pop_taxes_profit(self, country: Country):
        global_settings = GlobalSettings.objects().first()
        return (global_settings.pop_taxes_profit_k * country.population.total_population * (country.budget.population_taxes / 100)) + self.get_army_taxes_profit(country)

    def get_farms_taxes_profit(self, country: Country, production_profit: int=None):
        global_settings = GlobalSettings.objects().first()
        if production_profit is None:
            production_profit = self.get_farms_production_profit(country)
        taxes_profit = production_profit + global_settings.farms_taxes_profit_k * production_profit * country.budget.farms_taxes
        return taxes_profit

    def get_mines_taxes_profit(self, country: Country, production_profit: int=None):
        global_settings = GlobalSettings.objects().first()
        if production_profit is None:
            production_profit = self.get_mines_production_profit(country)
        taxes_profit = production_profit + global_settings.mines_taxes_profit_k * production_profit * country.budget.mines_taxes
        return taxes_profit

    def get_factories_taxes_profit(self, country: Country, production_profit: int=None):
        global_settings = GlobalSettings.objects().first()
        if production_profit is None:
            production_profit = self.get_factories_production_profit(country)
        taxes_profit = production_profit + global_settings.factories_taxes_profit_k * production_profit * country.budget.factories_taxes
        return taxes_profit

    def get_total_profit(self, country: Country):
        total_profit = self.get_pop_taxes_profit(country) + self.get_farms_profit(country) + self.get_mines_profit(
            country) + self.get_factories_profit(country) - country.budget.military_expenses
        return total_profit

    def get_economic_place(self, country_name: str):
        countries = Country.objects()
        profit_target_country = 0
        economic_profit_dict = {}
        for country in countries:
            profit = self.get_total_profit(country)
            if country.name == country_name:
                profit_target_country = profit
            economic_profit_dict[country.name] = profit
        economic_rating = sorted(economic_profit_dict.items(), key=lambda x: x[1], reverse=True)
        return economic_rating.index((country_name, profit_target_country)) + 1

    def get_army_place(self, country_name: str):
        countries = Country.objects
        army_expenses_dict = {country.name: country.budget.military_expenses for country in countries}
        army_rating_dict = sorted(army_expenses_dict.items(), key=lambda x: x[1], reverse=True)
        target_country = next(filter(lambda x: x[0] == country_name, army_rating_dict))
        return army_rating_dict.index(target_country) + 1

    def get_goods_data(self, country: Country):
        farms_modifiers = self.get_industry_modifiers(country,'farms')
        mines_modifiers = self.get_industry_modifiers(country,'mines')
        factories_modifiers = self.get_industry_modifiers(country,'factories')

        names_farms = [farm.name for farm in country.farms]
        farms_production = [farm.number * farm.production_speed * farms_modifiers for farm in country.farms]

        names_mines = [mine.name for mine in country.mines]
        mines_production = [mine.number * mine.production_speed * mines_modifiers for mine in country.mines]

        names_factories = [factory.name for factory in country.factories]
        factories_production = [factory.active_number * factory.production_speed * factories_modifiers for factory in
                                country.factories]

        names_military_factories = [factory.name for factory in country.military_factories]
        military_factories_production = [factory.active_number * factory.production_speed * factories_modifiers for
                                         factory in country.military_factories]
        goods_data_dict = {
            'farms': {'names': names_farms, 'values': farms_production},
            'mines': {'names': names_mines, 'values': mines_production},
            'factories': {'names': names_factories, 'values': factories_production},
            'military factories': {'names': names_military_factories, 'values': military_factories_production}
        }
        return goods_data_dict

    def get_table_world_place_production(self):
        countries = Country.objects()
        data = {}
        is_first_iteration = True

        for country in countries:
            farms_modifiers = self.get_industry_modifiers(country, 'farms')
            mines_modifiers = self.get_industry_modifiers(country, 'mines')
            factories_modifiers = self.get_industry_modifiers(country, 'factories')

            for farm in country.farms:
                if is_first_iteration:
                    data[self.get_name_goods_from_building(farm.name)] = []
                data[self.get_name_goods_from_building(farm.name)].append(
                    (country.name, round(farm.number * farm.production_speed * farms_modifiers,2)))

            for mine in country.mines:
                if is_first_iteration:
                    data[self.get_name_goods_from_building(mine.name)] = []
                data[self.get_name_goods_from_building(mine.name)].append(
                    (country.name, round(mine.number * mine.production_speed * mines_modifiers,2)))

            for factory in country.factories:
                if is_first_iteration:
                    data[self.get_name_goods_from_building(factory.name)] = []
                data[self.get_name_goods_from_building(factory.name)].append(
                    (country.name, round(factory.active_number * factory.production_speed * factories_modifiers,2)))

            for military_factory in country.military_factories:
                if is_first_iteration:
                    data[self.get_name_goods_from_building(military_factory.name)] = []
                data[self.get_name_goods_from_building(military_factory.name)].append((country.name,
                                                                                       round(military_factory.active_number * military_factory.production_speed * factories_modifiers,2)))
            is_first_iteration = False

        for key in data:
            data[key] = sorted(data[key], key=lambda x: x[1], reverse=True)

        return data

    def get_name_goods_from_building(self, name_building: str):
        words = re.split(r' ', name_building)
        if 'factory' in words:
            words.remove('factory')
        elif 'farm' in words:
            words.remove('farm')
        elif 'mine' in words:
            words.remove('mine')
        elif 'well' in words:
            words.remove('well')
        return ' '.join(words)