from datetime import datetime
import json

from sendgrid import SendGridAPIClient, Mail
from typing import Dict, List

from polls.exceptions import UnknownUserError
from lib.tokenlib.errors import ExpiredTokenError
from tokenlib.errors import InvalidSignatureError

from polls.models import Trade, History, Modifier, ArmyUnitCharacteristic, ArmyUnit, Population, \
    Army, Goods, Warehouse, IndustrialBuilding, Technology, Budget, Country, Law, User, GlobalSettings, Cache
from polls.services.view_service import PlayerViewService, CountryViewService, NewsViewService
from serverDjango.settings import ADMIN_EMAIL, EMAIL_API_KEY

from polls.services.game_service import GameService


class SystemService:

    def create_default_global_settings(self):
        GlobalSettings.objects().delete()
        GlobalSettings().save()

    def update_top_players_cache(self,number: int):
        top_players_lst = PlayerViewService().get_top_players(number)
        json_top_players_lst = json.dumps(top_players_lst,default=lambda x:x.__dict__)
        cache = Cache.objects().first()
        cache.top_players = json_top_players_lst
        cache.save()

    def update_trade_cache(self):
        user = User.objects().first()
        if user:
            trade_view = CountryViewService().get_trade(user.id)
            cache = Cache.objects().first()
            cache.trade = json.dumps(trade_view,default=lambda x:x.__dict__)
            cache.save()

    @staticmethod
    def verify_token(user_id: str,token:str):
        user = User.objects(id=user_id).first()
        if user:
            if user.token == token:
                if (datetime.utcnow() - user.date_last_login).days < 1:
                    return True
                else:
                    raise ExpiredTokenError
            else:
                raise InvalidSignatureError
        else:
            raise UnknownUserError(user_id)

    def update_players(self):
        game_service = GameService()
        for country in Country.objects():
            game_service.update_population(country) # +
            game_service.update_industry(country) # +
            game_service.update_budget(country) # +


    def get_user_settings(self,user_id: str):
        user = User.objects(id=user_id).first()
        return user.settings

    def set_user_settings(self, user: User, settings: Dict[str, bool]):
        for setting in user.settings:
            user.settings[setting] = setting in settings
        user.save()

    def send_notification(self, to_emails: List[str], type_notification: str, *args):
        if type_notification == EmailEvent.REGISTRATION:
            html_msg = EmailTemplate().get_html_registration(*args)
            SystemService().send_email(to_emails, html_msg, EmailTemplate.REGISTRATION_TITLE)
        elif type_notification == EmailEvent.DELETE:
            html_msg = EmailTemplate().get_html_delete_account(*args)
            SystemService().send_email(to_emails, html_msg, EmailTemplate.DELETE_TITLE)
        elif type_notification == EmailEvent.CHANGE_DATA:
            html_msg = EmailTemplate().get_html_edit_account(*args)
            SystemService().send_email(to_emails, html_msg, EmailTemplate.CHANGE_TITLE)
        elif type_notification == EmailEvent.FEEDBACK:
            msg_html = EmailTemplate().get_html_feedback(*args)
            SystemService().send_email(to_emails, msg_html, EmailTemplate.FEEDBACK_TITLE)
        elif type_notification == EmailEvent.LOW_BUDGET:
            msg_html = EmailTemplate().get_html_low_budget(*args)
            SystemService().send_email(to_emails, msg_html, EmailTemplate.LOW_BUDGET_TITLE)
        elif type_notification == EmailEvent.LOW_POPULATION:
            msg_html = EmailTemplate().get_html_low_population(*args)
            SystemService().send_email(to_emails, msg_html, EmailTemplate.LOW_POPULATION_TITLE)
        elif type_notification == EmailEvent.ATTACK:
            msg_html = EmailTemplate().get_html_attack(*args)
            SystemService().send_email(to_emails, msg_html, EmailTemplate.ATTACK)
        elif type_notification == EmailEvent.WAREHOUSE:
            msg_html = EmailTemplate().get_html_warehouse()
            SystemService().send_email(to_emails, msg_html, EmailTemplate.WAREHOUSE)
        elif type_notification == EmailEvent.NEWS:
            news_view_obj = NewsViewService().get_news()[-1]
            msg_html = EmailTemplate().get_html_news(news_view_obj.title,news_view_obj.date,news_view_obj.rows)
            SystemService().send_email(to_emails, msg_html, EmailTemplate.NEWS)



    def send_email(self, to_emails: List[str], html_content: str, title: str):
        print('sending email...')
        message = Mail(
            from_email=ADMIN_EMAIL,
            to_emails=to_emails,
            subject=title,
            html_content=html_content
        )
        sg = SendGridAPIClient(api_key=EMAIL_API_KEY)
        response = sg.send(message)
        print(response.status_code, response.body, response.headers)

    def create_default_country(self,name: str,link_img: str):
        global_settings = GlobalSettings.objects().first()
        return Country(
            link_img=link_img,
            name=name,
            budget=Budget(money=int(global_settings.start_budget_k*50000), population_taxes=50, farms_taxes=50, mines_taxes=50,
                          factories_taxes=50, military_taxes=50, military_expenses=1000,
                          profit_history = [],
                          expenses_history = [],
                          budget_history = [History(value=int(global_settings.start_budget_k*50000))],
                          ),
            technologies=[
                Technology(name='Medicine technology', price_upgrade=int(global_settings.technology_price_k*10000), level=0, max_level=100, total_result=0.0,
                           increase_price=1.3,
                           modifiers=[
                               Modifier(value=0.1, address_from='Medicine technology',
                                        address_to='basic percent growth rate population')
                           ]),
                Technology(name='Computers technology', price_upgrade=int(global_settings.technology_price_k*10000), level=0, max_level=100, total_result=0.0,
                           increase_price=1.3,
                           modifiers=[
                               Modifier(value=1, address_from='Computers technology', address_to='production speed')
                           ]),
                Technology(name='Upgrade weapons', price_upgrade=int(global_settings.technology_price_k*10000), level=0, max_level=100, total_result=0.0,
                           increase_price=1.3,
                           modifiers=[
                               Modifier(value=2, address_from='Upgrade weapons', address_to='attack value')
                           ]),
                Technology(name='Upgrade defence system', price_upgrade=int(global_settings.technology_price_k*10000), level=0, max_level=100, total_result=0.0,
                           increase_price=1.3,
                           modifiers=[
                               Modifier(value=2, address_from='Upgrade defence system', address_to='defence value')
                           ]),
            ],
            farms=[
                IndustrialBuilding(name='Seed farm', link_img='farms_goods/seed.jpg', production_speed=global_settings.farms_production_k * 5,
                                   price_build=int(global_settings.farms_price_k*10000), workers=int(global_settings.farm_workers_k*1000), number=0, need_goods=[]),
                IndustrialBuilding(name='Meat farm', link_img='farms_goods/meat.jpg', production_speed=global_settings.farms_production_k * 5,
                                   price_build=int(global_settings.farms_price_k*10000), workers=int(global_settings.farm_workers_k*1000), number=0, need_goods=[]),
                IndustrialBuilding(name='Milk farm', link_img='farms_goods/milk.jpg', production_speed=global_settings.farms_production_k * 5,
                                   price_build=int(global_settings.farms_price_k*10000), workers=int(global_settings.farm_workers_k*1000), number=0, need_goods=[]),
                IndustrialBuilding(name='Fish farm', link_img='farms_goods/fish.jpg', production_speed=global_settings.farms_production_k * 5,
                                   price_build=int(global_settings.farms_price_k*10000), workers=int(global_settings.farm_workers_k*1000), number=0, need_goods=[]),
                IndustrialBuilding(name='Fruits farm', link_img='farms_goods/fruits.jpg', production_speed=global_settings.farms_production_k * 5,
                                   price_build=int(global_settings.farms_price_k*10000), workers=int(global_settings.farm_workers_k*1000), number=0, need_goods=[]),
                IndustrialBuilding(name='Vegetables farm', link_img='farms_goods/vegetables.jpg', production_speed=global_settings.farms_production_k * 5,
                                   price_build=int(global_settings.farms_price_k*10000), workers=int(global_settings.farm_workers_k*1000), number=0, need_goods=[]),
            ],
            mines=[
                IndustrialBuilding(name='Iron mine', link_img='mine_goods/iron.jpg', production_speed=global_settings.mines_production_k * 5,
                                   price_build=int(global_settings.mines_price_k*10000), workers=int(global_settings.mine_workers_k*5000), number=0, need_goods=[]),
                IndustrialBuilding(name='Aluminum mine', link_img='mine_goods/aluminum.jpg', production_speed=global_settings.mines_production_k * 5,
                                   price_build=int(global_settings.mines_price_k*10000), workers=int(global_settings.mine_workers_k*5000), number=0, need_goods=[]),
                IndustrialBuilding(name='Coal mine', link_img='mine_goods/coal.jpg', production_speed=global_settings.mines_production_k * 5,
                                   price_build=int(global_settings.mines_price_k*10000), workers=int(global_settings.mine_workers_k*5000), number=0, need_goods=[]),
                IndustrialBuilding(name='Oil well', link_img='mine_goods/oil.jpg', production_speed=global_settings.mines_production_k * 5,
                                   price_build=int(global_settings.mines_price_k*12000), workers=int(global_settings.mine_workers_k*5000), number=0, need_goods=[]),
                IndustrialBuilding(name='Silicon mine', link_img='mine_goods/silicon.jpg', production_speed=global_settings.mines_production_k * 5,
                                   price_build=int(global_settings.mines_price_k*11000), workers=int(global_settings.mine_workers_k*5000), number=0, need_goods=[]),
                IndustrialBuilding(name='Salt mine', link_img='mine_goods/salt.jpg', production_speed=global_settings.mines_production_k * 5,
                                   price_build=int(global_settings.mines_price_k*8000), workers=int(global_settings.mine_workers_k*5000), number=0, need_goods=[]),
                IndustrialBuilding(name='Minerals mine', link_img='mine_goods/minerals.jpg', production_speed=global_settings.mines_production_k * 5,
                                   price_build=int(global_settings.mines_price_k*15000), workers=int(global_settings.mine_workers_k*5000), number=0, need_goods=[]),
                IndustrialBuilding(name='Gold mine', link_img='mine_goods/gold.jpg', production_speed=global_settings.mines_production_k * 5,
                                   price_build=int(global_settings.mines_price_k*30000), workers=int(global_settings.mine_workers_k*5000), number=0, need_goods=[]),
                IndustrialBuilding(name='Diamond mine', link_img='mine_goods/diamond.jpg', production_speed=global_settings.mines_production_k * 5,
                                   price_build=int(global_settings.mines_price_k*50000), workers=int(global_settings.mine_workers_k*5000), number=0, need_goods=[]),
            ],
            factories=[
                IndustrialBuilding(name='Bakery factory', link_img='industry_goods/bakery.jpg', production_speed=global_settings.factories_production_k * 20,
                                   price_build=int(global_settings.factories_price_k*10000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Seed', value=5, link_img='farms_goods/seed.jpg')
                                    ]),
                IndustrialBuilding(name='Canned food factory', link_img='industry_goods/canned_food.jpg',
                                   production_speed=global_settings.factories_production_k*20,
                                   price_build=int(global_settings.factories_price_k*10000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Seed', value=5, link_img='farms_goods/seed.jpg'),
                                        Goods(name='Meat', value=5, link_img='farms_goods/meat.jpg'),
                                        Goods(name='Aluminum', value=5, link_img='mine_goods/aluminum.jpg'),
                                    ]),
                IndustrialBuilding(name='Cheese factory', link_img='industry_goods/cheese.jpg', production_speed=global_settings.factories_production_k * 20,
                                   price_build=int(global_settings.factories_price_k*12000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Milk', value=5, link_img='farms_goods/milk.jpg'),
                                    ]),
                IndustrialBuilding(name='Salt fish factory', link_img='industry_goods/salt_fish.jpg',
                                   production_speed=global_settings.factories_production_k*15,
                                   price_build=int(global_settings.factories_price_k*10000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Fish', value=5, link_img='farms_goods/fish.jpg'),
                                        Goods(name='Salt', value=5, link_img='mine_goods/salt.jpg'),
                                    ]),
                IndustrialBuilding(name='Juice factory', link_img='industry_goods/juice.jpg', production_speed=global_settings.factories_production_k * 10,
                                   price_build=int(global_settings.factories_price_k*15000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Fruits', value=5, link_img='farms_goods/fruits.jpg'),
                                        Goods(name='Glass', value=5, link_img='industry_goods/glass.jpg'),
                                    ]),
                IndustrialBuilding(name='Fuel factory', link_img='industry_goods/fuel.jpg', production_speed=global_settings.factories_production_k * 25,
                                   price_build=int(global_settings.factories_price_k*20000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Oil', value=5, link_img='mine_goods/oil.jpg'),
                                    ]),
                IndustrialBuilding(name='Electronics factory', link_img='industry_goods/electronics.jpg',
                                   production_speed=global_settings.factories_production_k*20,
                                   price_build=int(global_settings.factories_price_k*15000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Silicon', value=5, link_img='mine_goods/silicon.jpg'),
                                        Goods(name='Gold', value=5, link_img='mine_goods/gold.jpg'),
                                    ]),
                IndustrialBuilding(name='Chemicals factory', link_img='industry_goods/chemicals.jpg',
                                   production_speed=global_settings.factories_production_k*25,
                                   price_build=int(global_settings.factories_price_k*18000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Silicon', value=5, link_img='mine_goods/minerals.jpg'),
                                    ]),
                IndustrialBuilding(name='Computers factory', link_img='industry_goods/computers.jpg',
                                   production_speed=global_settings.factories_production_k*10,
                                   price_build=int(global_settings.factories_price_k*25000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Electronics', value=5, link_img='industry_goods/electronics.jpg'),
                                        Goods(name='Plastic', value=5, link_img='industry_goods/plastic.jpg'),
                                    ]),
                IndustrialBuilding(name='Steel factory', link_img='industry_goods/steel.jpg', production_speed=global_settings.factories_production_k * 20,
                                   price_build=int(global_settings.factories_price_k*10000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Iron', value=5, link_img='mine_goods/iron.jpg'),
                                        Goods(name='Coal', value=5, link_img='mine_goods/coal.jpg'),
                                    ]),
                IndustrialBuilding(name='Rubber factory', link_img='industry_goods/rubber.jpg', production_speed=global_settings.factories_production_k * 15,
                                   price_build=int(global_settings.factories_price_k*13000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Oil', value=5, link_img='mine_goods/oil.jpg'),
                                    ]),
                IndustrialBuilding(name='Plastic factory', link_img='industry_goods/plastic.jpg', production_speed=global_settings.factories_production_k * 10,
                                   price_build=int(global_settings.factories_price_k*10000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Oil', value=5, link_img='mine_goods/oil.jpg'),
                                    ]),
                IndustrialBuilding(name='Glass factory', link_img='industry_goods/glass.jpg', production_speed=global_settings.factories_production_k * 20,
                                   price_build=int(global_settings.factories_price_k*15000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Silicon', value=5, link_img='mine_goods/minerals.jpg'),
                                        Goods(name='Coal', value=5, link_img='mine_goods/coal.jpg'),
                                    ]),
                IndustrialBuilding(name='Fertilizer factory', link_img='industry_goods/fertilizer.jpg',
                                   production_speed=global_settings.factories_production_k*10,
                                   price_build=int(global_settings.factories_price_k*11000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Salt', value=5, link_img='mine_goods/salt.jpg'),
                                        Goods(name='Minerals', value=5, link_img='mine_goods/minerals.jpg'),
                                    ]),
                IndustrialBuilding(name='Medicine factory', link_img='industry_goods/medicine.png',
                                   production_speed=global_settings.factories_production_k*10,
                                   price_build=int(global_settings.factories_price_k*10000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Chemicals', value=5, link_img='industry_goods/chemicals.jpg'),
                                    ]),
                IndustrialBuilding(name='Solar panel factory', link_img='industry_goods/solar_panel.jpg',
                                   production_speed=global_settings.factories_production_k*10,
                                   price_build=int(global_settings.factories_price_k*10000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Silicon', value=3, link_img='mine_goods/silicon.jpg'),
                                        Goods(name='Glass', value=3, link_img='industry_goods/glass.jpg'),
                                    ]),
                IndustrialBuilding(name='Battery factory', link_img='industry_goods/battery.jpg', production_speed=global_settings.factories_production_k * 12,
                                   price_build=int(global_settings.factories_price_k*10000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Chemicals', value=4, link_img='industry_goods/chemicals.jpg'),
                                        Goods(name='Aluminum', value=4, link_img='mine_goods/aluminum.jpg'),
                                    ]),
                IndustrialBuilding(name='Jewelry factory', link_img='industry_goods/jewelry.jpg', production_speed=global_settings.factories_production_k * 5,
                                   price_build=int(global_settings.factories_price_k*60000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Gold', value=2, link_img='mine_goods/gold.jpg'),
                                        Goods(name='Diamond', value=2, link_img='mine_goods/diamond.jpg'),
                                    ]),
            ],
            military_factories=[
                IndustrialBuilding(name='Infantry equipment factory', link_img='army/infantry_equipment.jpg',
                                   production_speed=global_settings.factories_production_k*5,
                                   price_build=int(global_settings.factories_price_k*30000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Steel', value=5, link_img='industry_goods/steel.jpg'),
                                        Goods(name='Aluminum', value=5, link_img='mine_goods/aluminum.jpg'),
                                        Goods(name='Canned food', value=5, link_img='industry_goods/canned_food.jpg'),
                                        Goods(name='Medicine', value=5, link_img='industry_goods/medicine.png'),
                                    ]),
                IndustrialBuilding(name='Artillery factory', link_img='army/artillery.jpg', production_speed=global_settings.factories_production_k * 3,
                                   price_build=int(global_settings.factories_price_k*40000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Steel', value=5, link_img='industry_goods/steel.jpg'),
                                        Goods(name='Rubber', value=4, link_img='industry_goods/rubber.jpg'),
                                    ]),
                IndustrialBuilding(name='Anti-tank gun factory', link_img='army/pto.jpg', production_speed=global_settings.factories_production_k * 2,
                                   price_build=int(global_settings.factories_price_k*45000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Steel', value=4, link_img='industry_goods/steel.jpg'),
                                        Goods(name='Rubber', value=2, link_img='industry_goods/rubber.jpg'),
                                    ]),
                IndustrialBuilding(name='Air defense factory', link_img='army/pvo.jpg', production_speed=global_settings.factories_production_k * 2,
                                   price_build=int(global_settings.factories_price_k*50000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Steel', value=6, link_img='industry_goods/steel.jpg'),
                                        Goods(name='Rubber', value=4, link_img='industry_goods/rubber.jpg'),
                                    ]),
                IndustrialBuilding(name='Tanks factory', link_img='army/tank.jpg', production_speed=global_settings.factories_production_k * 0.5,
                                   price_build=int(global_settings.factories_price_k*70000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Steel', value=10, link_img='industry_goods/steel.jpg'),
                                        Goods(name='Rubber', value=5, link_img='industry_goods/rubber.jpg'),
                                    ]),
                IndustrialBuilding(name='Aviation factory', link_img='army/aviation.jpg', production_speed=global_settings.factories_production_k * 0.25,
                                   price_build=int(global_settings.factories_price_k*80000), workers=int(global_settings.factory_workers_k*10000), number=0,
                                   need_goods=[
                                        Goods(name='Aluminum', value=15, link_img='mine_goods/aluminum.jpg'),
                                        Goods(name='Rubber', value=5, link_img='industry_goods/rubber.jpg'),
                                    ]),
            ],
            warehouses=[
                Warehouse(goods=Goods(name='Seed', value=0, link_img='farms_goods/seed.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Meat', value=0, link_img='farms_goods/meat.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Milk', value=0, link_img='farms_goods/milk.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Fish', value=0, link_img='farms_goods/fish.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Fruits', value=0, link_img='farms_goods/fruits.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Vegetables', value=0, link_img='farms_goods/vegetables.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Iron', value=0, link_img='mine_goods/iron.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Aluminum', value=0, link_img='mine_goods/aluminum.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Coal', value=0, link_img='mine_goods/coal.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Oil', value=0, link_img='mine_goods/oil.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Silicon', value=0, link_img='mine_goods/silicon.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Salt', value=0, link_img='mine_goods/salt.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Minerals', value=0, link_img='mine_goods/minerals.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Gold', value=0, link_img='mine_goods/gold.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Diamond', value=0, link_img='mine_goods/diamond.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Bakery', value=0, link_img='industry_goods/bakery.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Canned food', value=0, link_img='industry_goods/canned_food.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Cheese', value=0, link_img='industry_goods/cheese.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Salt fish', value=0, link_img='industry_goods/salt_fish.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Juice', value=0, link_img='industry_goods/juice.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Fuel', value=0, link_img='industry_goods/fuel.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Electronics', value=0, link_img='industry_goods/electronics.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Chemicals', value=0, link_img='industry_goods/chemicals.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Computers', value=0, link_img='industry_goods/computers.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Steel', value=0, link_img='industry_goods/steel.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Rubber', value=0, link_img='industry_goods/rubber.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Plastic', value=0, link_img='industry_goods/plastic.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Glass', value=0, link_img='industry_goods/glass.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Fertilizer', value=0, link_img='industry_goods/fertilizer.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Medicine', value=0, link_img='industry_goods/medicine.png'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Solar panel', value=0, link_img='industry_goods/solar_panel.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Battery', value=0, link_img='industry_goods/battery.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Jewelry', value=0, link_img='industry_goods/jewelry.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Infantry equipment', value=0, link_img='army/infantry_equipment.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Artillery', value=0, link_img='army/artillery.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Anti-tank gun', value=0, link_img='army/pto.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Air defense', value=0, link_img='army/pvo.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Tanks', value=0, link_img='army/tank.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
                Warehouse(goods=Goods(name='Aviation', value=0, link_img='army/aviation.jpg'),
                          capacity=500, filling_speed=0, level=0, max_level=100,
                          price_upgrade=global_settings.warehouses_price_k*10000, added_capacity=500, increase_price=1.3),
            ],
            adopted_laws=['Conscript law: Volunteer'],
            population=Population(total_population=50000, factory_workers=0, miners=0,
                                  farmers=0, solders=600, free_people=39400, others=10000, min_percent_others=20,
                                  basic_percent_growth_rate=1,
                                  population_history=[History(value=1)],
                                  modifiers=[]),
            army=Army(reserve_military_manpower=500, victories=0, losses=0,conscript_law_value = 1.5,
                      units={
                          'Infantry': 100, 'Artillery': 0, 'Anti-tank gun': 0, 'Air defense': 0, 'Tank': 0, 'Aviation': 0
                      })
        )

    def create_default_table_laws(self):
        Law.objects().delete()
        global_settings = GlobalSettings.objects().first()
        Law(
            name='Isolation', description='Close border for all', price=global_settings.laws_price_k*20000,
            modifiers=[
                Modifier(value=-1, address_from='Isolation', address_to='basic_percent_growth_rate'),
                Modifier(value=-5, address_from='Isolation', address_to='production_speed'),
                Modifier(value=15, address_from='Isolation', address_to='defence_value'),
            ]
        ).save()

        Law(
            name='Free medicine', description='Medicine is free for everyone', price=global_settings.laws_price_k*20000,
            modifiers=[
                Modifier(value=0.5, address_from='Free medicine', address_to='basic_percent_growth_rate'),
                Modifier(value=-25, address_from='Free medicine', address_to='production_speed'),
            ]
        ).save()

        Law(
            name='Free housing', description='Gift flat for every family', price=global_settings.laws_price_k*20000,
            modifiers=[
                Modifier(value=1, address_from='Free housing', address_to='basic_percent_growth_rate'),
                Modifier(value=-25, address_from='Free housing', address_to='production_speed'),
                Modifier(value=-25, address_from='Free housing', address_to='attack_value'),
                Modifier(value=10, address_from='Free housing', address_to='defence_value'),
            ]
        ).save()

        Law(
            name='Free education', description='Education is free for everyone', price=global_settings.laws_price_k*20000,
            modifiers=[
                Modifier(value=-0.2, address_from='Free education', address_to='basic_percent_growth_rate'),
                Modifier(value=20, address_from='Free education', address_to='production_speed'),
                Modifier(value=-10, address_from='Free education', address_to='attack_value'),
            ]
        ).save()

        Law(
            name='Conscript law: Elite', description='Percent of the total population 0.5%', price=global_settings.laws_price_k*20000,
            modifiers=[
                Modifier(value=-0.1, address_from='Conscript law: Elite', address_to='basic_percent_growth_rate'),
                Modifier(value=10, address_from='Conscript law: Elite', address_to='production_speed'),
                Modifier(value=10, address_from='Conscript law: Elite', address_to='attack_value'),
                Modifier(value=10, address_from='Conscript law: Elite', address_to='defence_value'),
            ]
        ).save()

        Law(
            name='Conscript law: Volunteer', description='Percent of the total population 1.5%', price=global_settings.laws_price_k*20000,
            modifiers=[

            ]
        ).save()

        Law(
            name='Conscript law: Limited Conscription', description='Percent of the total population 2.5%', price=global_settings.laws_price_k*20000,
            modifiers=[
                Modifier(value=-0.2, address_from='Conscript law: Limited Conscription', address_to='production_speed'),
                Modifier(value=5, address_from='Conscript law: Limited Conscription', address_to='attack_value'),
                Modifier(value=5, address_from='Conscript law: Limited Conscription', address_to='defence_value'),
            ]
        ).save()

        Law(
            name='Conscript law: Extensive Conscription', description='Percent of the total population 5%', price=global_settings.laws_price_k*20000,
            modifiers=[
                Modifier(value=-5, address_from='Conscript law: Extensive Conscription', address_to='production_speed'),
            ]
        ).save()

        Law(
            name='Conscript law: Service by Requirement', description='Percent of the total population 10%',
            price=global_settings.laws_price_k*20000,
            modifiers=[
                Modifier(value=-0.5, address_from='Conscript law: Service by Requirement',
                         address_to='basic_percent_growth_rate'),
                Modifier(value=-5, address_from='Conscript law: Service by Requirement', address_to='production_speed'),
                Modifier(value=-5, address_from='Conscript law: Service by Requirement', address_to='attack_value'),
                Modifier(value=-5, address_from='Conscript law: Service by Requirement', address_to='defence_value'),
            ]
        ).save()

        Law(
            name='Conscript law: All Adults Serve', description='Percent of the total population 20%', price=global_settings.laws_price_k*20000,
            modifiers=[
                Modifier(value=-1.5, address_from='Conscript law: All Adults Serve',
                         address_to='basic_percent_growth_rate'),
                Modifier(value=-15, address_from='Conscript law: All Adults Serve', address_to='production_speed'),
                Modifier(value=-5, address_from='Conscript law: All Adults Serve', address_to='attack_value'),
                Modifier(value=-5, address_from='Conscript law: All Adults Serve', address_to='defence_value'),
            ]
        ).save()

        Law(
            name='Conscript law: All with weapons', description='Percent of the total population 30%', price=global_settings.laws_price_k*20000,
            modifiers=[
                Modifier(value=-4, address_from='Conscript law: All with weapons',
                         address_to='basic_percent_growth_rate'),
                Modifier(value=-35, address_from='Conscript law: All with weapons', address_to='production_speed'),
                Modifier(value=-15, address_from='Conscript law: All with weapons', address_to='attack_value'),
                Modifier(value=-10, address_from='Conscript law: All with weapons', address_to='defence_value'),
            ]
        ).save()

    def create_default_table_goods(self):
        Trade.objects().delete()
        Trade(name='Seed', default_price=2, price_now=2, history_price=[
        ]
              ).save()

        Trade(name='Meat', default_price=5, price_now=5, history_price=[
        ]
              ).save()

        Trade(name='Milk', default_price=10, price_now=10, history_price=[
        ]
              ).save()

        Trade(name='Fish', default_price=15, price_now=15, history_price=[
        ]
              ).save()

        Trade(name='Fruits', default_price=20, price_now=20, history_price=[
        ]
              ).save()

        Trade(name='Vegetables',default_price=25, price_now=25, history_price=[
        ]
              ).save()

        Trade(name='Iron',default_price=60, price_now=60, history_price=[
        ]
              ).save()

        Trade(name='Aluminum',default_price=70, price_now=70, history_price=[
        ]
              ).save()

        Trade(name='Coal',default_price=45, price_now=45, history_price=[
        ]
              ).save()

        Trade(name='Oil',default_price=70, price_now=70, history_price=[
        ]
              ).save()

        Trade(name='Silicon',default_price=35, price_now=35, history_price=[
        ]
              ).save()

        Trade(name='Salt',default_price=15, price_now=15, history_price=[
        ]
              ).save()

        Trade(name='Minerals',default_price=80, price_now=80, history_price=[
        ]
              ).save()

        Trade(name='Gold',default_price=340, price_now=340, history_price=[
        ]
              ).save()

        Trade(name='Diamond',default_price=500, price_now=500, history_price=[
        ]
              ).save()

        Trade(name='Bakery',default_price=40, price_now=40, history_price=[
        ]
              ).save()

        Trade(name='Canned food',default_price=45, price_now=45, history_price=[
        ]
              ).save()

        Trade(name='Cheese',default_price=35, price_now=35, history_price=[
        ]
              ).save()

        Trade(name='Salt fish',default_price=20, price_now=20, history_price=[
        ]
              ).save()

        Trade(name='Juice',default_price=45, price_now=45, history_price=[
        ]
              ).save()

        Trade(name='Fuel',default_price=80, price_now=80, history_price=[
        ]
              ).save()

        Trade(name='Electronics',default_price=80, price_now=80, history_price=[
        ]
              ).save()

        Trade(name='Chemicals',default_price=70, price_now=70, history_price=[
        ]
              ).save()

        Trade(name='Computers',default_price=90, price_now=90, history_price=[
        ]
              ).save()

        Trade(name='Steel',default_price=120, price_now=120, history_price=[
        ]
              ).save()

        Trade(name='Rubber',default_price=90, price_now=90, history_price=[
        ]
              ).save()

        Trade(name='Plastic',default_price=65, price_now=65, history_price=[
        ]
              ).save()

        Trade(name='Glass',default_price=80, price_now=80, history_price=[
        ]
              ).save()

        Trade(name='Fertilizer',default_price=70, price_now=70, history_price=[
        ]
              ).save()

        Trade(name='Medicine',default_price=110, price_now=110, history_price=[
        ]
              ).save()

        Trade(name='Solar panel',default_price=150, price_now=150, history_price=[
        ]
              ).save()

        Trade(name='Battery',default_price=150, price_now=150, history_price=[
        ]
              ).save()

        Trade(name='Jewelry',default_price=1200, price_now=1200, history_price=[
        ]
              ).save()

        Trade(name='Infantry equipment',default_price=250, price_now=250, history_price=[
        ]
              ).save()

        Trade(name='Artillery',default_price=500, price_now=500, history_price=[
        ]
              ).save()

        Trade(name='Anti-tank gun',default_price=2000, price_now=2000, history_price=[
        ]
              ).save()

        Trade(name='Air defense',default_price=4000, price_now=4000, history_price=[
        ]
              ).save()

        Trade(name='Tanks',default_price=8000, price_now=8000, history_price=[
        ]
              ).save()

        Trade(name='Aviation',default_price=12000, price_now=12000, history_price=[
        ]
              ).save()

    def create_default_table_army_units(self):
        ArmyUnit.objects().delete()
        ArmyUnit(
            name='Infantry', link_img='army/infantry.jpg', need_peoples=1, maintenance_price=10,
            unit_characteristic={
                'Infantry': ArmyUnitCharacteristic(unit_name='Infantry',
                                                   attack_value=10, defence_value=30),
                'Artillery': ArmyUnitCharacteristic(unit_name='Artillery', attack_value=15,
                                                    defence_value=5),
                'Anti-tank gun': ArmyUnitCharacteristic(unit_name='Anti-tank gun',
                                              attack_value=25, defence_value=40),
                'Air defense': ArmyUnitCharacteristic(unit_name='Air defense', attack_value=50,
                                              defence_value=90),
                'Tank': ArmyUnitCharacteristic(unit_name='Tank', attack_value=5,
                                               defence_value=5),
                'Aviation': ArmyUnitCharacteristic(unit_name='Aviation', attack_value=1,
                                                   defence_value=13),
            }
        ).save()

        ArmyUnit(
            name='Artillery', link_img='army/artillery.jpg', need_peoples=8, maintenance_price=20,
            unit_characteristic={
                'Infantry': ArmyUnitCharacteristic(unit_name='Infantry',
                                                   attack_value=60, defence_value=10),
                'Artillery': ArmyUnitCharacteristic(unit_name='Artillery', attack_value=30,
                                                    defence_value=5),
                'Anti-tank gun': ArmyUnitCharacteristic(unit_name='Anti-tank gun',
                                              attack_value=25, defence_value=20),
                'Air defense': ArmyUnitCharacteristic(unit_name='Air defense', attack_value=25,
                                              defence_value=15),
                'Tank': ArmyUnitCharacteristic(unit_name='Tank', attack_value=10,
                                               defence_value=15),
                'Aviation': ArmyUnitCharacteristic(unit_name='Aviation', attack_value=20,
                                                   defence_value=5),
            }
        ).save()

        ArmyUnit(
            name='Anti-tank gun', link_img='army/pto.jpg', need_peoples=10, maintenance_price=30,
            unit_characteristic={
                'Infantry': ArmyUnitCharacteristic(unit_name='Infantry',
                                                   attack_value=30, defence_value=10),
                'Artillery': ArmyUnitCharacteristic(unit_name='Artillery', attack_value=20,
                                                    defence_value=10),
                'Anti-tank gun': ArmyUnitCharacteristic(unit_name='Anti-tank gun',
                                              attack_value=20, defence_value=15),
                'Air defense': ArmyUnitCharacteristic(unit_name='Air defense', attack_value=25,
                                              defence_value=15),
                'Tank': ArmyUnitCharacteristic(unit_name='Tank', attack_value=70,
                                               defence_value=20),
                'Aviation': ArmyUnitCharacteristic(unit_name='Aviation', attack_value=5,
                                                   defence_value=10),
            }
        ).save()

        ArmyUnit(
            name='Air defense', link_img='army/pvo.jpg', need_peoples=10, maintenance_price=60,
            unit_characteristic={
                'Infantry': ArmyUnitCharacteristic(unit_name='Infantry',
                                                   attack_value=25, defence_value=10),
                'Artillery': ArmyUnitCharacteristic(unit_name='Artillery', attack_value=5,
                                                    defence_value=15),
                'Anti-tank gun': ArmyUnitCharacteristic(unit_name='Anti-tank gun',
                                              attack_value=20, defence_value=5),
                'Air defense': ArmyUnitCharacteristic(unit_name='Air defense', attack_value=5,
                                              defence_value=40),
                'Tank': ArmyUnitCharacteristic(unit_name='Tank', attack_value=10,
                                               defence_value=20),
                'Aviation': ArmyUnitCharacteristic(unit_name='Aviation', attack_value=80,
                                                   defence_value=40),
            }
        ).save()

        ArmyUnit(
            name='Tank', link_img='army/tank.jpg', need_peoples=20, maintenance_price=100,
            unit_characteristic={
                'Infantry': ArmyUnitCharacteristic(unit_name='Infantry',
                                                   attack_value=150, defence_value=200),
                'Artillery': ArmyUnitCharacteristic(unit_name='Artillery', attack_value=35,
                                                    defence_value=30),
                'Anti-tank gun': ArmyUnitCharacteristic(unit_name='Anti-tank gun',
                                              attack_value=20, defence_value=5),
                'Air defense': ArmyUnitCharacteristic(unit_name='Air defense', attack_value=10,
                                              defence_value=20),
                'Tank': ArmyUnitCharacteristic(unit_name='Tank', attack_value=60,
                                               defence_value=45),
                'Aviation': ArmyUnitCharacteristic(unit_name='Aviation', attack_value=5,
                                                   defence_value=25),
            }
        ).save()

        ArmyUnit(
            name='Aviation', link_img='army/aviation.jpg', need_peoples=30, maintenance_price=250,
            unit_characteristic={
                'Infantry': ArmyUnitCharacteristic(unit_name='Infantry',
                                                   attack_value=90, defence_value=500),
                'Artillery': ArmyUnitCharacteristic(unit_name='Artillery', attack_value=35,
                                                    defence_value=50),
                'Anti-tank gun': ArmyUnitCharacteristic(unit_name='Anti-tank gun',
                                              attack_value=25, defence_value=150),
                'Air defense': ArmyUnitCharacteristic(unit_name='Air defense', attack_value=10,
                                              defence_value=10),
                'Tank': ArmyUnitCharacteristic(unit_name='Tank', attack_value=35,
                                               defence_value=90),
                'Aviation': ArmyUnitCharacteristic(unit_name='Aviation', attack_value=100,
                                                   defence_value=80),
            }
        ).save()

class EmailEvent:
    REGISTRATION = 'REGISTRATION'
    DELETE = 'DELETE'
    CHANGE_DATA = 'CHANGE DATA'
    FEEDBACK = 'FEEDBACK'
    LOW_BUDGET = 'LOW BUDGET'
    LOW_POPULATION = 'LOW POPULATION'
    WAREHOUSE = 'WAREHOUSE'
    NEWS = 'NEWS'
    ATTACK = 'ATTACK'

class EmailTemplate:
    REGISTRATION_TITLE = 'Register in strategy - Your country'
    DELETE_TITLE = 'Delete account in strategy - Your country'
    CHANGE_TITLE = 'Account data was changed in strategy - Your country'
    FEEDBACK_TITLE = 'New feedback from strategy - Your country'
    LOW_BUDGET_TITLE = 'Low budget - Your country'
    LOW_POPULATION_TITLE = 'Low population - Your country'
    WAREHOUSE = 'Warehouse problem - Your country'
    NEWS = 'Something new - Your country'
    ATTACK = 'Someone attacked you - Your country'

    def get_html_news(self,title: str,date: str,rows: List[str]):
        html = """
            <h3>News</h3>
            <strong>"""+title+""" ("""+date+""")</strong>
        """
        for row in rows:
            html += f"- {row} <br>\n"
        return html

    def get_html_attack(self,player_name: str):
        html = """
            <h3>Important information!</h3>
            <strong>Player """+player_name+""" attacked your country</strong>
        """
        return html

    def get_html_warehouse(self):
        html = """
            <h3>Important information!</h3>
            <strong>The warehouse(s) has a problem</strong>
        """
        return html

    def get_html_low_budget(self,budget: int):
        html = """
            <h3>Important information!</h3>
            <strong>The budget is low, your country have only """+str(budget)+"""$</strong>
        """
        return html

    def get_html_low_population(self,population: int):
        html = """
            <h3>Important information!</h3>
            <strong>The number of inhabitants is low, in country living only """+str(population)+""" people</strong>
        """
        return html

    def get_html_registration(self, username: str, password: str, country_name: str, user_id: str, flag_link: str):
        html = """<html><body><h1 style="font-weight: bolder">
        Dear """ + username + """
        <p>Welcome to online strategy - 'Your country'</h1>
        <hr><p><h2 style="color:green">Account was registered successfully:</h2>
        <h3>Player data:</h3>
        <p>ID: """ + user_id + """
        <p>Login: """ + username + """
        <p>Password: """ + password + """
        <p>Country: """ + country_name + """
        <p>Flag: """ + flag_link + """
        <p><a href="http://htmlbook.ru/html/a/href">Click on this link and start play now!</a>
        <p><strong style="color:orange">If you have any question or problems, write on this email testtset1009@gmail.com</strong>
        </body></html>"""
        return html

    def get_html_delete_account(self, username: str):
        html = """<html><body><h1 style="font-weight: bolder">
        """ + username + """!
        <hr><p><h2 style="color:red">Your account was deleted</h2>
        <p><strong style="color:orange">If you have any question or problems, write on this email testtset1009@gmail.com</strong>
        </body></html>"""
        return html

    def get_html_edit_account(self, username: str, password: str, country_name: str, flag_link: str):
        html = """<html><body><h1 style="font-weight: bolder">
                """ + username + """ attention!
                <hr><p><h2 style="color:red">Account data was changed:</h2>
                <h3>New player data:</h3>
                <p>Username: """ + username + """
                <p>Password: """ + password + """
                <p>Country: """ + country_name + """
                <p>Flag: """ + flag_link + """
                <p><a href="http://htmlbook.ru/html/a/href">Click on this link and start play now!</a>
                <p><strong style="color:orange">If you have any question or problems, write on this email testtset1009@gmail.com</strong>
                </body></html>"""
        return html

    def get_html_feedback(self, username: str, msg: str, player_email: str, rating: float):
        html = """<html><body><h1 style="font-weight: bolder">
                        Player """ + username + """ write feedback!</h1><hr>
                        <h3>Message:</h3>
                        <p>Rating: """ + str(rating) + """/6
                        <p>""" + msg + """
                        <p><strong>Player email """ + player_email + """</strong>
                        </body></html>"""
        return html
