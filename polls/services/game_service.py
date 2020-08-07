from polls.models import Country, Modifier, Goods, Trade, Law, ArmyUnit
import re

class GameService:
    def set_taxes(self,country_name,type_taxes,new_value):
        if type_taxes == 'population_taxes':
            obj = Country.objects(name=country_name).only('budget','population').first()
            obj.update(budget__population_taxes=new_value)
            existing = obj.population.modifiers.filter(address_from='population taxes')
            if existing.count() == 0:
                obj.update(push__population__modifiers=Modifier(value=-0.2*new_value+10, address_from='population taxes'))
            else:
                existing.update(value=-0.2*new_value+10)
                obj.save()


        elif type_taxes == 'farms_taxes':
            obj = Country.objects(name=country_name).only('budget', 'industry_modifiers').first()
            obj.update(budget__farms_taxes=new_value)
            existing = obj.industry_modifiers.filter(address_from='farms taxes')
            if existing.count() == 0:
                obj.update(
                    push__industry_modifiers=Modifier(value=-0.6 * new_value + 30, address_from='farms taxes'))
            else:
                existing.update(value=-0.6 * new_value + 30)
                obj.save()

        elif type_taxes == 'mines_taxes':
            obj = Country.objects(name=country_name).only('budget', 'industry_modifiers').first()
            obj.update(budget__mines_taxes=new_value)
            existing = obj.industry_modifiers.filter(address_from='mines taxes')
            if existing.count() == 0:
                obj.update(
                    push__industry_modifiers=Modifier(value=-0.6 * new_value + 30, address_from='mines taxes'))
            else:
                existing.update(value=-0.6 * new_value + 30)
                obj.save()

        elif type_taxes == 'factories_taxes':
            obj = Country.objects(name=country_name).only('budget', 'industry_modifiers').first()
            obj.update(budget__factories_taxes=new_value)
            existing = obj.industry_modifiers.filter(address_from='factories taxes')
            if existing.count() == 0:
                obj.update(
                    push__industry_modifiers=Modifier(value=-0.6 * new_value + 30, address_from='factories taxes'))
            else:
                existing.update(value=-0.6 * new_value + 30)
                obj.save()

        elif type_taxes == 'military_taxes':
            obj = Country.objects(name=country_name).only('budget', 'army').first()
            obj.update(budget__military_taxes=new_value)
            existing = obj.army.attack_modifiers.filter(address_from='army taxes')
            existing2 = obj.army.defence_modifiers.filter(address_from='army taxes')
            if existing.count() == 0:
                obj.update(
                    push__army__attack_modifiers=Modifier(value=-new_value + 50, address_from='army taxes'))
                obj.update(
                    push__army__defence_modifiers=Modifier(value=-new_value + 50, address_from='army taxes'))
            else:
                existing.update(value=-new_value + 50)
                existing2.update(value=-new_value + 50)
                obj.save()

    def upgrade_technology(self,country_name,technology_name):
        if technology_name == 'Medicine technology':
            obj = Country.objects(name=country_name).only('budget', 'population','technologies').first()
            technology = obj.technologies.filter(name='Medicine technology').first()
            if obj.budget.money >= technology.price_upgrade:
                obj.budget.money -= technology.price_upgrade
                technology.price_upgrade*=technology.increasePrice
                technology.level +=1
                existing = obj.population.modifiers.filter(address_from='Medicine technology')
                if existing.count() == 0:
                    obj.update(push__population__modifiers=Modifier(value=technology.modifiers[0].value,
                                                                    address_from='Medicine technology'))
                else:
                    existing.update(value=technology.modifiers[0].value * technology.level)
                obj.save()

        elif technology_name == 'Computers technology':
            obj = Country.objects(name=country_name).only('budget','technologies','industry_modifiers').first()
            technology = obj.technologies.filter(name='Computers technology').first()
            if obj.budget.money >= technology.price_upgrade:
                obj.budget.money -= technology.price_upgrade
                technology.price_upgrade*=technology.increasePrice
                technology.level +=1
                existing = obj.industry_modifiers.filter(address_from='Computers technology')
                if existing.count() == 0:
                    obj.update(push__industry_modifiers=Modifier(value=technology.modifiers[0].value,
                                                                    address_from='Computers technology'))
                else:
                    existing.update(value=technology.modifiers[0].value * technology.level)
                obj.save()

        elif technology_name == 'Upgrade weapons':
            obj = Country.objects(name=country_name).only('budget','technologies','army').first()
            technology = obj.technologies.filter(name='Upgrade weapons').first()
            if obj.budget.money >= technology.price_upgrade:
                obj.budget.money -= technology.price_upgrade
                technology.price_upgrade*=technology.increasePrice
                technology.level +=1
                existing = obj.army.attack_modifiers.filter(address_from='Upgrade weapons')
                if existing.count() == 0:
                    obj.update(push__army__attack_modifiers=Modifier(value=technology.modifiers[0].value,
                                                                    address_from='Upgrade weapons'))
                else:
                    existing.update(value=technology.modifiers[0].value * technology.level)
                obj.save()

        if technology_name == 'Upgrade defence system':
            obj = Country.objects(name=country_name).only('budget','technologies','army').first()
            technology = obj.technologies.filter(name='Upgrade defence system').first()
            if obj.budget.money >= technology.price_upgrade:
                obj.budget.money -= technology.price_upgrade
                technology.price_upgrade *= technology.increasePrice
                technology.level += 1
                existing = obj.army.defence_modifiers.filter(address_from='Upgrade defence system')
                if existing.count() == 0:
                    obj.update(push__army__defence_modifiers=Modifier(value=technology.modifiers[0].value,
                                                              address_from='Upgrade defence system'))
                else:
                    existing.update(value=technology.modifiers[0].value * technology.level)
                obj.save()

    def build_industry(self,country_name,name_building):
        obj = Country.objects(name=country_name).only('budget', 'population',
            'farms','mines','factories','military_factories').first()
        type_building = re.split(r' ',name_building)[-1]
        if type_building == 'farm':
            farm = obj.farms.filter(name=name_building).first()
            if obj.budget.money >= farm.price_build and \
                    obj.population.free_people >= farm.workers:
                obj.budget.money -= farm.price_build
                obj.population.free_people -= farm.workers
                obj.population.farmers +=farm.workers
                farm.number +=1
        elif type_building == 'mines':
            mine = obj.mines.filter(name=name_building).first()
            if obj.budget.money >= mine.price_build and \
                    obj.population.free_people >= mine.workers:
                obj.budget.money -= mine.price_build
                obj.population.free_people -= mine.workers
                obj.population.miners += mine.workers
                mine.number += 1
        elif type_building == 'factory':
            factory = obj.factories.filter(name=name_building).first()
            if factory is not None and obj.budget.money >= factory.price_build and \
                    obj.population.free_people >= factory.workers:
                obj.budget.money -= factory.price_build
                obj.population.free_people -= factory.workers
                obj.population.factory_workers += factory.workers
                factory.number += 1
            else:
                factory = obj.military_factories.filter(name=name_building).first()
                if obj.budget.money >= factory.price_build and \
                        obj.population.free_people >= factory.workers:
                    obj.budget.money -= factory.price_build
                    obj.population.free_people -= factory.workers
                    obj.population.factory_workers += factory.workers
                    factory.number += 1
        obj.save()

    def remove_industry(self,country_name,name_building):
        obj = Country.objects(name=country_name).only('population',
                'farms', 'mines', 'factories', 'military_factories').first()
        type_building = re.split(r' ', name_building)[-1]
        if type_building == 'farm':
            farm = obj.farms.filter(name=name_building).first()
            if farm.number > 0:
                obj.population.free_people += farm.workers
                obj.population.farmers -= farm.workers
                farm.number -= 1

        elif type_building == 'mines':
            mine = obj.mines.filter(name=name_building).first()
            if mine.number > 0:
                obj.population.free_people += mine.workers
                obj.population.miners -= mine.workers
                mine.number -= 1

        elif type_building == 'factory':
            factory = obj.factories.filter(name=name_building).first()
            if factory is not None and factory.number > 0:
                obj.population.free_people += factory.workers
                obj.population.factory_workers -= factory.workers
                factory.number -= 1
            else:
                factory = obj.military_factories.filter(name=name_building).first()
                if factory.number > 0:
                    obj.population.free_people += factory.workers
                    obj.population.factory_workers -= factory.workers
                    factory.number -= 1
        obj.save()

    def upgrade_warehouse(self, country_name, name_goods):
        obj = Country.objects(name=country_name).only('budget', 'warehouses').first()
        warehouse = [item for item in obj.warehouses if item.goods.name == name_goods][0]
        if obj.budget.money >= warehouse.price_upgrade:
            obj.budget.money -= warehouse.price_upgrade
            warehouse.price_upgrade *= warehouse.increasePrice
            warehouse.level += 1
            warehouse.capacity+=warehouse.added_capacity
            obj.save()

    def set_politics_law(self,country_name,name_law):
        obj = Country.objects(name=country_name).first()
        law = Law.objects(name=name_law).first()
        if name_law == 'Immigration' and obj.budget.money >= law.price and \
                not name_law in obj.adopted_laws:
            obj.budget.money -=law.price
            obj.adopted_laws.append(name_law)
            obj.population.modifiers.append(Modifier(value=2,address_from=name_law))
            obj.industry_modifiers.append(Modifier(value=5,address_from=name_law))
            obj.army.attack_modifiers.append(Modifier(value=-8,address_from=name_law))
            obj.army.defence_modifiers.append(Modifier(value=-8,address_from=name_law))
        elif name_law == 'Isolation' and obj.budget.money >= law.price and \
                not name_law in obj.adopted_laws:
            obj.budget.money -=law.price
            obj.adopted_laws.append(name_law)
            obj.population.modifiers.append(Modifier(value=-5,address_from=name_law))
            obj.industry_modifiers.append(Modifier(value=-5,address_from=name_law))
            obj.army.defence_modifiers.append(Modifier(value=15,address_from=name_law))
        elif name_law == 'Free housing' and obj.budget.money >= law.price and \
                not name_law in obj.adopted_laws:
            obj.budget.money -=law.price
            obj.adopted_laws.append(name_law)
            obj.population.modifiers.append(Modifier(value=5,address_from=name_law))
            obj.industry_modifiers.append(Modifier(value=-10,address_from=name_law))
            obj.army.attack_modifiers.append(Modifier(value=-10,address_from=name_law))
            obj.army.defence_modifiers.append(Modifier(value=10,address_from=name_law))
        elif name_law == 'Free education' and obj.budget.money >= law.price and \
                not name_law in obj.adopted_laws:
            obj.budget.money -=law.price
            obj.adopted_laws.append(name_law)
            obj.population.modifiers.append(Modifier(value=-2,address_from=name_law))
            obj.industry_modifiers.append(Modifier(value=15,address_from=name_law))
            obj.army.attack_modifiers.append(Modifier(value=-10,address_from=name_law))
        obj.save()

    def set_conscript_law(self,country_name,name_law):
        obj = Country.objects(name=country_name).first()
        law = Law.objects(name=name_law).first()
        if name_law == 'Conscript law: Elite' and obj.budget.money >= law.price:
            self.cansel_conscript_law(obj)
            obj.adopted_laws.append(name_law)
            obj.budget.money -= law.price
            obj.army.conscript_law_value = 0.5
            obj.army.reserve_military_manpower = obj.population.total_population * obj.army.conscript_law_value // 100
            obj.population.modifiers.append(Modifier(value=-10, address_from=name_law))
            obj.industry_modifiers.append(Modifier(value=10, address_from=name_law))
            obj.army.attack_modifiers.append(Modifier(value=10, address_from=name_law))
            obj.army.defence_modifiers.append(Modifier(value=10, address_from=name_law))
        elif name_law == 'Conscript law: Volunteer' and obj.budget.money >= law.price:
            self.cansel_conscript_law(obj)
            obj.adopted_laws.append(name_law)
            obj.budget.money -= law.price
            obj.army.conscript_law_value = 1.5
            obj.army.reserve_military_manpower = obj.population.total_population * obj.army.conscript_law_value // 100
        elif name_law == 'Conscript law: Limited Conscription' and obj.budget.money >= law.price:
            self.cansel_conscript_law(obj)
            obj.adopted_laws.append(name_law)
            obj.budget.money -= law.price
            obj.army.conscript_law_value = 2.5
            obj.army.reserve_military_manpower = obj.population.total_population * obj.army.conscript_law_value // 100
            obj.industry_modifiers.append(Modifier(value=-5, address_from=name_law))
            obj.army.attack_modifiers.append(Modifier(value=5, address_from=name_law))
            obj.army.defence_modifiers.append(Modifier(value=5, address_from=name_law))
        elif name_law == 'Conscript law: Extensive Conscription' and obj.budget.money >= law.price:
            self.cansel_conscript_law(obj)
            obj.adopted_laws.append(name_law)
            obj.budget.money -= law.price
            obj.army.conscript_law_value = 5
            obj.army.reserve_military_manpower = obj.population.total_population * obj.army.conscript_law_value // 100
            obj.industry_modifiers.append(Modifier(value=-5, address_from=name_law))
        elif name_law == 'Conscript law: Service by Requirement' and obj.budget.money >= law.price:
            self.cansel_conscript_law(obj)
            obj.adopted_laws.append(name_law)
            obj.budget.money -= law.price
            obj.army.conscript_law_value = 10
            obj.army.reserve_military_manpower = obj.population.total_population * obj.army.conscript_law_value // 100
            obj.population.modifiers.append(Modifier(value=-5, address_from=name_law))
            obj.industry_modifiers.append(Modifier(value=-5, address_from=name_law))
            obj.army.attack_modifiers.append(Modifier(value=-5, address_from=name_law))
            obj.army.defence_modifiers.append(Modifier(value=-5, address_from=name_law))
        elif name_law == 'Conscript law: All Adults Serve' and obj.budget.money >= law.price:
            self.cansel_conscript_law(obj)
            obj.adopted_laws.append(name_law)
            obj.budget.money -= law.price
            obj.army.conscript_law_value = 20
            obj.army.reserve_military_manpower = obj.population.total_population * obj.army.conscript_law_value // 100
            obj.population.modifiers.append(Modifier(value=-10, address_from=name_law))
            obj.industry_modifiers.append(Modifier(value=-15, address_from=name_law))
            obj.army.attack_modifiers.append(Modifier(value=-5, address_from=name_law))
            obj.army.defence_modifiers.append(Modifier(value=-5, address_from=name_law))
        elif name_law == 'Conscript law: All with weapons' and obj.budget.money >= law.price:
            self.cansel_conscript_law(obj)
            obj.adopted_laws.append(name_law)
            obj.budget.money -= law.price
            obj.army.conscript_law_value = 30
            obj.army.reserve_military_manpower = obj.population.total_population * obj.army.conscript_law_value // 100
            obj.population.modifiers.append(Modifier(value=-15, address_from=name_law))
            obj.industry_modifiers.append(Modifier(value=-35, address_from=name_law))
            obj.army.attack_modifiers.append(Modifier(value=-15, address_from=name_law))
            obj.army.defence_modifiers.append(Modifier(value=-10, address_from=name_law))
        obj.save()

    def cansel_conscript_law(self,country):
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

    def cancel_politics_law(self,country_name,name_law):
        obj = Country.objects(name=country_name).first()
        law = Law.objects(name=name_law).first()
        if name_law == 'Immigration' and obj.budget.money >= law.price and \
                name_law in obj.adopted_laws:
            obj.budget.money -= law.price
            obj.adopted_laws.remove(name_law)
            obj.population.modifiers.remove(Modifier(value=2, address_from=name_law))
            obj.industry_modifiers.remove(Modifier(value=5, address_from=name_law))
            obj.army.attack_modifiers.remove(Modifier(value=-8, address_from=name_law))
            obj.army.defence_modifiers.remove(Modifier(value=-8, address_from=name_law))
        elif name_law == 'Isolation' and obj.budget.money >= law.price and \
                name_law in obj.adopted_laws:
            obj.budget.money -=law.price
            obj.adopted_laws.remove(name_law)
            obj.population.modifiers.remove(Modifier(value=-5,address_from=name_law))
            obj.industry_modifiers.remove(Modifier(value=-5,address_from=name_law))
            obj.army.defence_modifiers.remove(Modifier(value=15,address_from=name_law))
        elif name_law == 'Free housing' and obj.budget.money >= law.price and \
                name_law in obj.adopted_laws:
            obj.budget.money -=law.price
            obj.adopted_laws.remove(name_law)
            obj.population.modifiers.remove(Modifier(value=5,address_from=name_law))
            obj.industry_modifiers.remove(Modifier(value=-10,address_from=name_law))
            obj.army.attack_modifiers.remove(Modifier(value=-10,address_from=name_law))
            obj.army.defence_modifiers.remove(Modifier(value=10,address_from=name_law))
        elif name_law == 'Free education' and obj.budget.money >= law.price and \
                name_law in obj.adopted_laws:
            obj.budget.money -=law.price
            obj.adopted_laws.remove(name_law)
            obj.population.modifiers.remove(Modifier(value=-2,address_from=name_law))
            obj.industry_modifiers.remove(Modifier(value=15,address_from=name_law))
            obj.army.attack_modifiers.remove(Modifier(value=-10,address_from=name_law))
        obj.save()

    def buy_goods(self,country_name,name_goods,number):
        obj = Country.objects(name=country_name).only('budget', 'warehouses').first()
        warehouse = [item for item in obj.warehouses if item.goods.name == name_goods][0]
        if number <= warehouse.capacity - warehouse.goods.value:
            price_goods = Trade.objects(name=name_goods).first().price_now * number
            if obj.budget.money >= price_goods:
                obj.budget.money -= price_goods
                warehouse.goods.value += number
                obj.save()

    def sell_goods(self,country_name,name_goods,number):
        obj = Country.objects(name=country_name).only('budget', 'warehouses').first()
        warehouse = [item for item in obj.warehouses if item.goods.name == name_goods][0]
        if number <= warehouse.goods.value:
            price_goods = Trade.objects(name=name_goods).first().price_now * number
            obj.budget.money += price_goods
            warehouse.goods.value -= number
            obj.save()

    def edit_army(self,country_name,name_unit,new_number):
        obj = Country.objects(name=country_name).first()
        dif = obj.army.units[name_unit] - new_number
        unit = ArmyUnit.objects(name=name_unit).first()
        if obj.army.reserve_military_manpower + dif >= 0:
            obj.army.reserve_military_manpower += dif * unit.need_peoples
            obj.budget.military_expenses -= dif * unit.maintenance_price
            if name_unit == 'Infantry':
                warehouse = [item for item in obj.warehouses if item.goods.name == 'Infantry equipment'][0]
            else:
                warehouse = [item for item in obj.warehouses if item.goods.name == name_unit][0]
            if warehouse.goods.value + dif >= 0:
                warehouse.goods.value += dif
        obj.save()

    def calculate_war(self,attacking_country_name,defending_country_name):
        attacking_country = Country.objects(name=attacking_country_name).first()
        defending_country = Country.objects(name=defending_country_name).first()
        army_units = ArmyUnit.objects()
        for unit in army_units:
            sorted_units_by_attack = sorted(unit.unit_characteristic.items(), key=lambda x: x[1].attack_value, reverse=True)
            if attacking_country.army.units[unit.name] !=0:
                for item in sorted_units_by_attack:
                    if defending_country.army.units[item[1].unit_name] !=0:
                        sum_attack_modifiers = sum(mod.value for mod in attacking_country.army.attack_modifiers)/100+1
                        attack_power = attacking_country.army.units[unit.name]*item[1].attack_value*sum_attack_modifiers
                        sum_defence_modifiers = sum(mod.value for mod in defending_country.army.defence_modifiers)/100+1
                        defence_power = defending_country.army.units[item[1].unit_name]*item[1].defence_value*sum_defence_modifiers
                        dif = defence_power - attack_power
                        if dif > 0:
                            attacking_country.army.units[unit.name] = 0
                            defending_country.army.units[item[1].unit_name] =  dif // item[1].defence_value
                        elif dif < 0:
                            attacking_country.army.units[unit.name] = -dif // item[1].attack_value
                            defending_country.army.units[item[1].unit_name] = 0
                        elif dif == 0:
                            attacking_country.army.units[unit.name] = 0
                            defending_country.army.units[item[1].unit_name] = 0