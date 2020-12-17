from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from polls.models import Trade, History, Modifier, ArmyUnitCharacteristic, ArmyUnit, Population, \
    Army, Goods, Warehouse, IndustrialBuildings, Technology, Budget, Country, Law, User
from polls.services.game_service import GameService
from serverDjango.settings import ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD


class SystemService:
    def update_system(self):
        game_service = GameService()
        for country in Country.objects():
            game_service.update_population(country)
            game_service.update_warehouses(country)
            game_service.update_budget(country)
        game_service.update_price_goods()


    def get_user_settings(self,user_id):
        user = User.objects(_id=user_id).first()
        return user.settings

    def set_user_settings(self,user,settings):
        for setting in user.settings:
            user.settings[setting] = setting in settings
        user.save()

    def send_email(self, from_email, to_email, password, message, title):
        msg = MIMEMultipart()  # create msg object
        msg['Subject'] = title  # title
        msg.attach(MIMEText(message, 'html'))  # attach text to msg as html
        server = smtplib.SMTP('smtp.gmail.com: 587')  # create server
        server.starttls()  # always use TLS protocol
        server.login(from_email, password)  # login
        server.sendmail(from_email, to_email, msg.as_string())  # send msg
        server.quit()  # destroy connection

    def get_feedback(self, username, user_email, rating, msg):
        msg_html = EmailTemplate().get_html_feedback(username, msg, user_email, rating)
        self.send_email(ADMIN_EMAIL, ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD,
                        msg_html, EmailTemplate.FEEDBACK_TITLE)

    def create_default_country(self,name,link_img):
        return Country(
            link_img=link_img,
            name=name,
            budget=Budget(money=100000, population_taxes=50, farms_taxes=50, mines_taxes=50,
                          factories_taxes=50, military_taxes=50, military_expenses=1000,
                          profit_history = [History(value=5), History(value=-2), History(value=8)],
                          expenses_history = [History(value=5), History(value=-2), History(value=8)],
                          ),
            technologies=[
                Technology(name='Medicine technology', price_upgrade=5000, level=0, max_level=100, total_result=0.0,
                           increasePrice=1.3,
                           modifiers=[
                               Modifier(value=0.5, address_from='Medicine technology',
                                        address_to='basic_percent_growth_rate')
                           ]),
                Technology(name='Computers technology', price_upgrade=10000, level=0, max_level=100, total_result=0.0,
                           increasePrice=1.3,
                           modifiers=[
                               Modifier(value=1, address_from='Computers technology', address_to='production_speed')
                           ]),
                Technology(name='Upgrade weapons', price_upgrade=10000, level=0, max_level=100, total_result=0.0,
                           increasePrice=1.3,
                           modifiers=[
                               Modifier(value=2, address_from='Upgrade weapons', address_to='attack_value')
                           ]),
                Technology(name='Upgrade defence system', price_upgrade=10000, level=0, max_level=100, total_result=0.0,
                           increasePrice=1.3,
                           modifiers=[
                               Modifier(value=2, address_from='Upgrade defence system', address_to='defence_value')
                           ]),
            ],
            farms=[
                IndustrialBuildings(name='Seed farm', link_img='farms_goods/seed.jpg', production_speed=10,
                                    price_build=10000, workers=1000, number=0, needGoods=[]),
                IndustrialBuildings(name='Meat farm', link_img='farms_goods/meat.jpg', production_speed=10,
                                    price_build=10000, workers=1000, number=0, needGoods=[]),
                IndustrialBuildings(name='Milk farm', link_img='farms_goods/milk.jpg', production_speed=10,
                                    price_build=10000, workers=1000, number=0, needGoods=[]),
                IndustrialBuildings(name='Fish farm', link_img='farms_goods/fish.jpg', production_speed=10,
                                    price_build=10000, workers=1000, number=0, needGoods=[]),
                IndustrialBuildings(name='Fruits farm', link_img='farms_goods/fruits.jpg', production_speed=10,
                                    price_build=10000, workers=1000, number=0, needGoods=[]),
                IndustrialBuildings(name='Vegetables farm', link_img='farms_goods/vegetables.jpg', production_speed=10,
                                    price_build=10000, workers=1000, number=0, needGoods=[]),
            ],
            mines=[
                IndustrialBuildings(name='Iron mine', link_img='mine_goods/iron.jpg', production_speed=10,
                                    price_build=10000, workers=2500, number=0, needGoods=[]),
                IndustrialBuildings(name='Aluminum mine', link_img='mine_goods/aluminum.jpg', production_speed=10,
                                    price_build=10000, workers=2500, number=0, needGoods=[]),
                IndustrialBuildings(name='Coal mine', link_img='mine_goods/coal.jpg', production_speed=10,
                                    price_build=10000, workers=2500, number=0, needGoods=[]),
                IndustrialBuildings(name='Oil well', link_img='mine_goods/oil.jpg', production_speed=10,
                                    price_build=10000, workers=2500, number=0, needGoods=[]),
                IndustrialBuildings(name='Silicon mine', link_img='mine_goods/silicon.jpg', production_speed=10,
                                    price_build=10000, workers=2500, number=0, needGoods=[]),
                IndustrialBuildings(name='Salt mine', link_img='mine_goods/salt.jpg', production_speed=10,
                                    price_build=10000, workers=2500, number=0, needGoods=[]),
                IndustrialBuildings(name='Minerals mine', link_img='mine_goods/minerals.jpg', production_speed=10,
                                    price_build=10000, workers=2500, number=0, needGoods=[]),
                IndustrialBuildings(name='Gold mine', link_img='mine_goods/gold.jpg', production_speed=10,
                                    price_build=10000, workers=2500, number=0, needGoods=[]),
                IndustrialBuildings(name='Diamond mine', link_img='mine_goods/diamond.jpg', production_speed=10,
                                    price_build=10000, workers=2500, number=0, needGoods=[]),
            ],
            factories=[
                IndustrialBuildings(name='Bakery factory', link_img='industry_goods/bakery.jpg', production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Seed', value=5, link_img='farms_goods/seed.jpg')
                                    ]),
                IndustrialBuildings(name='Canned food factory', link_img='industry_goods/canned_food.jpg',
                                    production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Seed', value=5, link_img='farms_goods/seed.jpg'),
                                        Goods(name='Meat', value=5, link_img='farms_goods/meat.jpg'),
                                        Goods(name='Aluminum', value=5, link_img='mine_goods/aluminum.jpg'),
                                    ]),
                IndustrialBuildings(name='Cheese factory', link_img='industry_goods/cheese.jpg', production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Milk', value=5, link_img='farms_goods/milk.jpg'),
                                    ]),
                IndustrialBuildings(name='Salt fish factory', link_img='industry_goods/salt_fish.jpg',
                                    production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Fish', value=5, link_img='farms_goods/fish.jpg'),
                                        Goods(name='Salt', value=5, link_img='mine_goods/salt.jpg'),
                                    ]),
                IndustrialBuildings(name='Juice factory', link_img='industry_goods/juice.jpg', production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Fruits', value=5, link_img='farms_goods/fruits.jpg'),
                                        Goods(name='Glass', value=5, link_img='industry_goods/glass.jpg'),
                                    ]),
                IndustrialBuildings(name='Fuel factory', link_img='industry_goods/fuel.jpg', production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Oil', value=5, link_img='mine_goods/oil.jpg'),
                                    ]),
                IndustrialBuildings(name='Electronics factory', link_img='industry_goods/electronics.jpg',
                                    production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Silicon', value=5, link_img='mine_goods/silicon.jpg'),
                                        Goods(name='Gold', value=5, link_img='mine_goods/gold.jpg'),
                                    ]),
                IndustrialBuildings(name='Chemicals factory', link_img='industry_goods/chemicals.jpg',
                                    production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Silicon', value=5, link_img='mine_goods/minerals.jpg'),
                                    ]),
                IndustrialBuildings(name='Computers factory', link_img='industry_goods/computers.jpg',
                                    production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Electronics', value=5, link_img='industry_goods/electronics.jpg'),
                                        Goods(name='Plastic', value=5, link_img='industry_goods/plastic.jpg'),
                                    ]),
                IndustrialBuildings(name='Steel factory', link_img='industry_goods/steel.jpg', production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Iron', value=5, link_img='mine_goods/iron.jpg'),
                                        Goods(name='Coal', value=5, link_img='mine_goods/coal.jpg'),
                                    ]),
                IndustrialBuildings(name='Rubber factory', link_img='industry_goods/rubber.jpg', production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Oil', value=5, link_img='mine_goods/oil.jpg'),
                                    ]),
                IndustrialBuildings(name='Plastic factory', link_img='industry_goods/plastic.jpg', production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Oil', value=5, link_img='mine_goods/oil.jpg'),
                                    ]),
                IndustrialBuildings(name='Glass factory', link_img='industry_goods/glass.jpg', production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Silicon', value=5, link_img='mine_goods/minerals.jpg'),
                                        Goods(name='Coal', value=5, link_img='mine_goods/coal.jpg'),
                                    ]),
                IndustrialBuildings(name='Fertilizer factory', link_img='industry_goods/fertilizer.jpg',
                                    production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Salt', value=5, link_img='mine_goods/salt.jpg'),
                                        Goods(name='Minerals', value=5, link_img='mine_goods/minerals.jpg'),
                                    ]),
                IndustrialBuildings(name='Medicine factory', link_img='industry_goods/medicine.png',
                                    production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Chemicals', value=5, link_img='industry_goods/chemicals.jpg'),
                                    ]),
                IndustrialBuildings(name='Solar panel factory', link_img='industry_goods/solar_panel.jpg',
                                    production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Silicon', value=5, link_img='mine_goods/silicon.jpg'),
                                        Goods(name='Glass', value=5, link_img='industry_goods/glass.jpg'),
                                    ]),
                IndustrialBuildings(name='Battery factory', link_img='industry_goods/battery.jpg', production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Chemicals', value=5, link_img='industry_goods/chemicals.jpg'),
                                        Goods(name='Aluminum', value=5, link_img='mine_goods/aluminum.jpg'),
                                    ]),
                IndustrialBuildings(name='Jewelry factory', link_img='industry_goods/jewelry.jpg', production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Gold', value=5, link_img='mine_goods/gold.jpg'),
                                        Goods(name='Diamond', value=5, link_img='mine_goods/diamond.jpg'),
                                    ]),
            ],
            military_factories=[
                IndustrialBuildings(name='Infantry equipment factory', link_img='army/infantry_equipment.jpg',
                                    production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Steel', value=5, link_img='industry_goods/steel.jpg'),
                                        Goods(name='Aluminum', value=5, link_img='mine_goods/aluminum.jpg'),
                                        Goods(name='Canned food', value=5, link_img='industry_goods/canned_food.jpg'),
                                        Goods(name='Medicine', value=5, link_img='industry_goods/medicine.png'),
                                    ]),
                IndustrialBuildings(name='Artillery factory', link_img='army/artillery.jpg', production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Steel', value=5, link_img='industry_goods/steel.jpg'),
                                        Goods(name='Rubber', value=5, link_img='industry_goods/rubber.jpg'),
                                    ]),
                IndustrialBuildings(name='PTO factory', link_img='army/pto.jpg', production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Steel', value=5, link_img='industry_goods/steel.jpg'),
                                        Goods(name='Rubber', value=5, link_img='industry_goods/rubber.jpg'),
                                    ]),
                IndustrialBuildings(name='PVO factory', link_img='army/pvo.jpg', production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Steel', value=5, link_img='industry_goods/steel.jpg'),
                                        Goods(name='Rubber', value=5, link_img='industry_goods/rubber.jpg'),
                                    ]),
                IndustrialBuildings(name='Tanks factory', link_img='army/tank.jpg', production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Steel', value=5, link_img='industry_goods/steel.jpg'),
                                        Goods(name='Rubber', value=5, link_img='industry_goods/rubber.jpg'),
                                    ]),
                IndustrialBuildings(name='Aviation factory', link_img='army/aviation.jpg', production_speed=10,
                                    price_build=10000, workers=5000, number=0,
                                    needGoods=[
                                        Goods(name='Aluminum', value=5, link_img='mine_goods/aluminum.jpg'),
                                        Goods(name='Rubber', value=5, link_img='industry_goods/rubber.jpg'),
                                    ]),
            ],
            warehouses=[
                Warehouse(goods=Goods(name='Seed', value=0, link_img='farms_goods/seed.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Meat', value=0, link_img='farms_goods/meat.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Milk', value=0, link_img='farms_goods/milk.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Fish', value=0, link_img='farms_goods/fish.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Fruits', value=0, link_img='farms_goods/fruits.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Vegetables', value=0, link_img='farms_goods/vegetables.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Iron', value=0, link_img='mine_goods/iron.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Aluminum', value=0, link_img='mine_goods/aluminum.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Coal', value=0, link_img='mine_goods/coal.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Oil', value=0, link_img='mine_goods/oil.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Silicon', value=0, link_img='mine_goods/silicon.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Salt', value=0, link_img='mine_goods/salt.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Minerals', value=0, link_img='mine_goods/minerals.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Gold', value=0, link_img='mine_goods/gold.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Diamond', value=0, link_img='mine_goods/diamond.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Bakery', value=0, link_img='industry_goods/bakery.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Canned food', value=0, link_img='industry_goods/canned_food.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Cheese', value=0, link_img='industry_goods/cheese.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Salt fish', value=0, link_img='industry_goods/salt_fish.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Juice', value=0, link_img='industry_goods/juice.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Fuel', value=0, link_img='industry_goods/fuel.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Electronics', value=0, link_img='industry_goods/electronics.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Chemicals', value=0, link_img='industry_goods/chemicals.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Computers', value=0, link_img='industry_goods/computers.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Steel', value=0, link_img='industry_goods/steel.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Rubber', value=0, link_img='industry_goods/rubber.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Plastic', value=0, link_img='industry_goods/plastic.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Glass', value=0, link_img='industry_goods/glass.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Fertilizer', value=0, link_img='industry_goods/fertilizer.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Medicine', value=0, link_img='industry_goods/medicine.png'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Solar panel', value=0, link_img='industry_goods/solar_panel.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Battery', value=0, link_img='industry_goods/battery.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Jewelry', value=0, link_img='industry_goods/jewelry.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Infantry equipment', value=0, link_img='army/infantry_equipment.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Artillery', value=0, link_img='army/artillery.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='PTO', value=0, link_img='army/pto.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='PVO', value=0, link_img='army/pvo.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Tanks', value=0, link_img='army/tank.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
                Warehouse(goods=Goods(name='Aviation', value=0, link_img='army/aviation.jpg'),
                          capacity=1000, filling_speed=0, level=0, max_level=100,
                          price_upgrade=10000, added_capacity=1000, increasePrice=1.3),
            ],
            adopted_laws=['Conscript law: Volunteer'],
            population=Population(total_population=50000, factory_workers=0, miners=0,
                                  farmers=0, solders=600, free_people=39400, others=10000, min_percent_others=20,
                                  basic_percent_growth_rate=5,
                                  population_history=[History(value=5),History(value=-2),History(value=8)],
                                  modifiers=[]),
            army=Army(reserve_military_manpower=500, victories=0, losses=0,conscript_law_value = 1.5,
                      units={
                          'Infantry': 100, 'Artillery': 0, 'PTO': 0, 'PVO': 0, 'Tank': 0, 'Aviation': 0
                      })
        )

    def create_default_table_laws(self):
        Law.objects().delete()

        Law(
            name='Isolation', description='Close border for all', price=20000,
            modifiers=[
                Modifier(value=-5, address_from='Isolation', address_to='basic_percent_growth_rate'),
                Modifier(value=-5, address_from='Isolation', address_to='production_speed'),
                Modifier(value=15, address_from='Isolation', address_to='defence_value'),
            ]
        ).save()

        Law(
            name='Free medicine', description='Medicine is free for everyone', price=20000,
            modifiers=[
                Modifier(value=5, address_from='Free medicine', address_to='basic_percent_growth_rate'),
                Modifier(value=-10, address_from='Free medicine', address_to='production_speed'),
            ]
        ).save()

        Law(
            name='Free housing', description='Gift flat for every family', price=20000,
            modifiers=[
                Modifier(value=5, address_from='Free housing', address_to='basic_percent_growth_rate'),
                Modifier(value=-10, address_from='Free housing', address_to='production_speed'),
                Modifier(value=-10, address_from='Free housing', address_to='attack_value'),
                Modifier(value=10, address_from='Free housing', address_to='defence_value'),
            ]
        ).save()

        Law(
            name='Free education', description='Education is free for everyone', price=20000,
            modifiers=[
                Modifier(value=-2, address_from='Free education', address_to='basic_percent_growth_rate'),
                Modifier(value=15, address_from='Free education', address_to='production_speed'),
                Modifier(value=-10, address_from='Free education', address_to='attack_value'),
            ]
        ).save()

        Law(
            name='Conscript law: Elite', description='Percent of the total population 0.5%', price=20000,
            modifiers=[
                Modifier(value=-10, address_from='Conscript law: Elite', address_to='basic_percent_growth_rate'),
                Modifier(value=10, address_from='Conscript law: Elite', address_to='production_speed'),
                Modifier(value=10, address_from='Conscript law: Elite', address_to='attack_value'),
                Modifier(value=10, address_from='Conscript law: Elite', address_to='defence_value'),
            ]
        ).save()

        Law(
            name='Conscript law: Volunteer', description='Percent of the total population 1.5%', price=20000,
            modifiers=[

            ]
        ).save()

        Law(
            name='Conscript law: Limited Conscription', description='Percent of the total population 2.5%', price=20000,
            modifiers=[
                Modifier(value=-5, address_from='Conscript law: Limited Conscription', address_to='production_speed'),
                Modifier(value=5, address_from='Conscript law: Limited Conscription', address_to='attack_value'),
                Modifier(value=5, address_from='Conscript law: Limited Conscription', address_to='defence_value'),
            ]
        ).save()

        Law(
            name='Conscript law: Extensive Conscription', description='Percent of the total population 5%', price=20000,
            modifiers=[
                Modifier(value=-5, address_from='Conscript law: Extensive Conscription', address_to='production_speed'),
            ]
        ).save()

        Law(
            name='Conscript law: Service by Requirement', description='Percent of the total population 10%',
            price=20000,
            modifiers=[
                Modifier(value=-5, address_from='Conscript law: Service by Requirement',
                         address_to='basic_percent_growth_rate'),
                Modifier(value=-5, address_from='Conscript law: Service by Requirement', address_to='production_speed'),
                Modifier(value=-5, address_from='Conscript law: Service by Requirement', address_to='attack_value'),
                Modifier(value=-5, address_from='Conscript law: Service by Requirement', address_to='defence_value'),
            ]
        ).save()

        Law(
            name='Conscript law: All Adults Serve', description='Percent of the total population 20%', price=20000,
            modifiers=[
                Modifier(value=-10, address_from='Conscript law: All Adults Serve',
                         address_to='basic_percent_growth_rate'),
                Modifier(value=-15, address_from='Conscript law: All Adults Serve', address_to='production_speed'),
                Modifier(value=-5, address_from='Conscript law: All Adults Serve', address_to='attack_value'),
                Modifier(value=-5, address_from='Conscript law: All Adults Serve', address_to='defence_value'),
            ]
        ).save()

        Law(
            name='Conscript law: All with weapons', description='Percent of the total population 30%', price=20000,
            modifiers=[
                Modifier(value=-15, address_from='Conscript law: All with weapons',
                         address_to='basic_percent_growth_rate'),
                Modifier(value=-35, address_from='Conscript law: All with weapons', address_to='production_speed'),
                Modifier(value=-15, address_from='Conscript law: All with weapons', address_to='attack_value'),
                Modifier(value=-10, address_from='Conscript law: All with weapons', address_to='defence_value'),
            ]
        ).save()

    def create_default_table_goods(self):
        Trade.objects().delete()
        Trade(name='Seed', price_now=10, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Meat', price_now=15, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Milk', price_now=20, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Fish', price_now=10, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Fruits', price_now=15, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Vegetables', price_now=20, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Iron', price_now=10, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Aluminum', price_now=15, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Coal', price_now=20, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Oil', price_now=10, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Silicon', price_now=15, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Salt', price_now=20, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Minerals', price_now=10, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Gold', price_now=15, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Diamond', price_now=20, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Bakery', price_now=10, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Canned food', price_now=15, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Cheese', price_now=20, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Salt fish', price_now=10, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Juice', price_now=15, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Fuel', price_now=20, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Electronics', price_now=10, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Chemicals', price_now=15, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Computers', price_now=20, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Steel', price_now=10, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Rubber', price_now=15, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Plastic', price_now=20, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Glass', price_now=10, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Fertilizer', price_now=15, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Medicine', price_now=20, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Solar panel', price_now=10, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Battery', price_now=15, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Jewelry', price_now=20, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Infantry equipment', price_now=10, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Artillery', price_now=15, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='PTO', price_now=20, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='PVO', price_now=10, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Tanks', price_now=15, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
        ]
              ).save()

        Trade(name='Aviation', price_now=20, history_price=[
            History(value=10), History(value=20), History(value=30),
            History(value=25), History(value=40), History(value=15),
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
                'PTO': ArmyUnitCharacteristic(unit_name='PTO',
                                              attack_value=25, defence_value=40),
                'PVO': ArmyUnitCharacteristic(unit_name='PVO', attack_value=50,
                                              defence_value=90),
                'Tank': ArmyUnitCharacteristic(unit_name='Tank', attack_value=5,
                                               defence_value=5),
                'Aviation': ArmyUnitCharacteristic(unit_name='Aviation', attack_value=1,
                                                   defence_value=15),
            }
        ).save()

        ArmyUnit(
            name='Artillery', link_img='army/artillery.jpg', need_peoples=4, maintenance_price=20,
            unit_characteristic={
                'Infantry': ArmyUnitCharacteristic(unit_name='Infantry',
                                                   attack_value=60, defence_value=10),
                'Artillery': ArmyUnitCharacteristic(unit_name='Artillery', attack_value=30,
                                                    defence_value=5),
                'PTO': ArmyUnitCharacteristic(unit_name='PTO',
                                              attack_value=25, defence_value=20),
                'PVO': ArmyUnitCharacteristic(unit_name='PVO', attack_value=25,
                                              defence_value=15),
                'Tank': ArmyUnitCharacteristic(unit_name='Tank', attack_value=10,
                                               defence_value=15),
                'Aviation': ArmyUnitCharacteristic(unit_name='Aviation', attack_value=5,
                                                   defence_value=10),
            }
        ).save()

        ArmyUnit(
            name='PTO', link_img='army/pto.jpg', need_peoples=4, maintenance_price=30,
            unit_characteristic={
                'Infantry': ArmyUnitCharacteristic(unit_name='Infantry',
                                                   attack_value=30, defence_value=10),
                'Artillery': ArmyUnitCharacteristic(unit_name='Artillery', attack_value=20,
                                                    defence_value=10),
                'PTO': ArmyUnitCharacteristic(unit_name='PTO',
                                              attack_value=20, defence_value=15),
                'PVO': ArmyUnitCharacteristic(unit_name='PVO', attack_value=25,
                                              defence_value=15),
                'Tank': ArmyUnitCharacteristic(unit_name='Tank', attack_value=70,
                                               defence_value=20),
                'Aviation': ArmyUnitCharacteristic(unit_name='Aviation', attack_value=1,
                                                   defence_value=10),
            }
        ).save()

        ArmyUnit(
            name='PVO', link_img='army/pvo.jpg', need_peoples=6, maintenance_price=60,
            unit_characteristic={
                'Infantry': ArmyUnitCharacteristic(unit_name='Infantry',
                                                   attack_value=25, defence_value=10),
                'Artillery': ArmyUnitCharacteristic(unit_name='Artillery', attack_value=5,
                                                    defence_value=15),
                'PTO': ArmyUnitCharacteristic(unit_name='PTO',
                                              attack_value=20, defence_value=5),
                'PVO': ArmyUnitCharacteristic(unit_name='PVO', attack_value=5,
                                              defence_value=40),
                'Tank': ArmyUnitCharacteristic(unit_name='Tank', attack_value=10,
                                               defence_value=20),
                'Aviation': ArmyUnitCharacteristic(unit_name='Aviation', attack_value=80,
                                                   defence_value=40),
            }
        ).save()

        ArmyUnit(
            name='Tank', link_img='army/tank.jpg', need_peoples=4, maintenance_price=100,
            unit_characteristic={
                'Infantry': ArmyUnitCharacteristic(unit_name='Infantry',
                                                   attack_value=100, defence_value=200),
                'Artillery': ArmyUnitCharacteristic(unit_name='Artillery', attack_value=30,
                                                    defence_value=30),
                'PTO': ArmyUnitCharacteristic(unit_name='PTO',
                                              attack_value=20, defence_value=5),
                'PVO': ArmyUnitCharacteristic(unit_name='PVO', attack_value=10,
                                              defence_value=20),
                'Tank': ArmyUnitCharacteristic(unit_name='Tank', attack_value=60,
                                               defence_value=45),
                'Aviation': ArmyUnitCharacteristic(unit_name='Aviation', attack_value=5,
                                                   defence_value=25),
            }
        ).save()

        ArmyUnit(
            name='Aviation', link_img='army/aviation.jpg', need_peoples=3, maintenance_price=250,
            unit_characteristic={
                'Infantry': ArmyUnitCharacteristic(unit_name='Infantry',
                                                   attack_value=40, defence_value=500),
                'Artillery': ArmyUnitCharacteristic(unit_name='Artillery', attack_value=25,
                                                    defence_value=50),
                'PTO': ArmyUnitCharacteristic(unit_name='PTO',
                                              attack_value=25, defence_value=150),
                'PVO': ArmyUnitCharacteristic(unit_name='PVO', attack_value=10,
                                              defence_value=10),
                'Tank': ArmyUnitCharacteristic(unit_name='Tank', attack_value=35,
                                               defence_value=90),
                'Aviation': ArmyUnitCharacteristic(unit_name='Aviation', attack_value=100,
                                                   defence_value=80),
            }
        ).save()


class EmailTemplate:
    REGISTRATION_TITLE = 'Register in strategy - Your country'
    DELETE_TITLE = 'Delete account in strategy - Your country'
    CHANGE_TITLE = 'Account data was changed in strategy - Your country'
    FEEDBACK_TITLE = 'New feedback from strategy - Your country'

    def get_html_registration(self, username, password, country_name, user_id, flag_link):
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

    def get_html_delete_account(self, username):
        html = """<html><body><h1 style="font-weight: bolder">
        """ + username + """!
        <hr><p><h2 style="color:red">Your account was deleted</h2>
        <p><strong style="color:orange">If you have any question or problems, write on this email testtset1009@gmail.com</strong>
        </body></html>"""
        return html

    def get_html_edit_account(self, username, password, country_name, flag_link):
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

    def get_html_feedback(self, username, msg, player_email, rating):
        html = """<html><body><h1 style="font-weight: bolder">
                        Player """ + username + """ write feedback!</h1><hr>
                        <h3>Message:</h3>
                        <p>Rating: """ + str(rating) + """/6
                        <p>""" + msg + """
                        <p><strong>Player email """ + player_email + """</strong>
                        </body></html>"""
        return html
