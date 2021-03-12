import mongoengine
from django.utils import timezone
from mongoengine import *

connect('TestDb')

class News(Document):
    title = StringField(default='',max_length=200)
    date = DateTimeField(default=timezone.now)
    text = StringField(default='',max_length=1000)

class History(EmbeddedDocument):
    name = StringField(max_length=100,default='')
    value = FloatField(default=0.0)
    time = DateTimeField(default=timezone.now)

class Budget(EmbeddedDocument):
    money = IntField(default=0)
    population_taxes = IntField(default=0,min_value=0,max_value=100)
    farms_taxes = IntField(default=0,min_value=0,max_value=100)
    mines_taxes = IntField(default=0,min_value=0,max_value=100)
    factories_taxes = IntField(default=0,min_value=0,max_value=100)
    military_taxes = IntField(default=0,min_value=0,max_value=100)
    military_expenses = FloatField(default=0,min_value=0)
    total_profit = FloatField(default=0)
    total_expenses = FloatField(default=0)
    profit_history = EmbeddedDocumentListField('History',default=[])
    expenses_history = EmbeddedDocumentListField('History',default=[])
    budget_history = EmbeddedDocumentListField('History',default=[])
    date_last_budget_notification = DateTimeField(default=timezone.now)
    date_last_budget_chart_update = DateTimeField(default=timezone.now)
    date_last_budget_update = DateTimeField(default=timezone.now)

class Modifier(EmbeddedDocument):
    value = FloatField(default=0.0)
    address_from = StringField(default='',max_length=100)
    address_to = StringField(default='',max_length=100)

class Technology(EmbeddedDocument):
    name = StringField(default='',max_length=100)
    price_upgrade = IntField(default=0,min_value=0)
    level = IntField(default=0,min_value=0,max_value=100)
    max_level = IntField(default=0)
    total_result = FloatField(default=0)
    increase_price = FloatField(default=0, min_value=0)
    modifiers = EmbeddedDocumentListField('Modifier',default=[])

class Goods(EmbeddedDocument):
    name = StringField(default='',max_length=100)
    value = FloatField(default=0,min_value=0)
    link_img = StringField(default='',max_length=100)

class IndustrialBuilding(EmbeddedDocument):
    name = StringField(default='',max_length=100)
    link_img = StringField(default='',max_length=100)
    production_speed = FloatField(default=0,min_value=0)
    price_build = IntField(default=0,min_value=0)
    workers = IntField(default=0,min_value=0)
    number = IntField(default=0,min_value=0)
    need_goods = EmbeddedDocumentListField('Goods', default=[])
    active_number = IntField(default=0,min_value=0)
    date_last_industry_update = DateTimeField(default=timezone.now)

class Warehouse(EmbeddedDocument):
    goods = EmbeddedDocumentField('Goods')
    capacity = IntField(default=0)
    filling_speed = FloatField(default=0.0)
    level = IntField(default=0,min_value=0,max_value=100)
    max_level = IntField(default=0,min_value=0)
    price_upgrade = IntField(default=0,min_value=0)
    added_capacity = IntField(default=0,min_value=0)
    increase_price = FloatField(default=0, min_value=0)

class Law(Document):
    name = StringField(default='',max_length=100)
    description = StringField(default='',max_length=200)
    price = IntField(default=0,min_value=0)
    modifiers = EmbeddedDocumentListField('Modifier', default=[])

class Population(EmbeddedDocument):
    total_population = IntField(default=0,min_value=0)
    factory_workers = IntField(default=0,min_value=0)
    miners = IntField(default=0,min_value=0)
    farmers = IntField(default=0,min_value=0)
    solders = IntField(default=0,min_value=0)
    free_people = IntField(default=0,min_value=0)
    others = IntField(default=0,min_value=0)
    min_percent_others = IntField(default=0,min_value=0)
    basic_percent_growth_rate = IntField(default=0,min_value=0)
    modifiers = EmbeddedDocumentListField('Modifier', default=[])
    population_history = EmbeddedDocumentListField('History',default=[])
    date_last_population_notification = DateTimeField(default=timezone.now)
    date_last_population_update = DateTimeField(default=timezone.now)
    date_last_population_chart_update = DateTimeField(default=timezone.now)

class ArmyUnitCharacteristic(EmbeddedDocument):
    unit_name = StringField(default='',max_length=100)
    attack_value = FloatField(default=0,min_value=0)
    defence_value = FloatField(default=0,min_value=0)

class ArmyUnit(Document):
    name = StringField(default='',max_length=100)
    link_img = StringField(default='',max_length=200)
    need_peoples = IntField(default=0,min_value=1)
    maintenance_price = IntField(default=0,min_value=1)
    unit_characteristic = DictField(EmbeddedDocumentField('ArmyUnitCharacteristic'),default={})

class Army(EmbeddedDocument):
    conscript_law_value = FloatField(default=0, min_value=0)
    reserve_military_manpower = IntField(default=0)
    victories = IntField(default=0,min_value=0)
    losses = IntField(default=0,min_value=0)
    attack_modifiers = EmbeddedDocumentListField('Modifier', default=[])
    defence_modifiers = EmbeddedDocumentListField('Modifier', default=[])
    units = DictField(default={})

class Country(Document):
    link_img = StringField(default='',max_length=1000)
    name = StringField(default='',max_length=100,unique=True)
    budget = EmbeddedDocumentField('Budget')
    technologies = EmbeddedDocumentListField('Technology',default=[])
    farms = EmbeddedDocumentListField('IndustrialBuilding',default=[])
    mines = EmbeddedDocumentListField('IndustrialBuilding',default=[])
    factories = EmbeddedDocumentListField('IndustrialBuilding',default=[])
    military_factories = EmbeddedDocumentListField('IndustrialBuilding',default=[])
    industry_modifiers = EmbeddedDocumentListField('Modifier',default=[])
    warehouses = EmbeddedDocumentListField('Warehouse',default=[])
    adopted_laws = ListField(default=[])
    population = EmbeddedDocumentField('Population')
    army = EmbeddedDocumentField('Army')
    date_last_warehouse_notification = DateTimeField(default=timezone.now)

class User(Document):
    isAuth = BooleanField(default=False)
    token = StringField(default='')
    date_last_login = DateTimeField(default=timezone.now)
    username = StringField(default='', max_length=100,unique=True)
    password = StringField(default='', max_length=100)
    email = EmailField(default='user_email@gmail.com')
    date_registration = DateTimeField(default=timezone.now)
    settings = DictField(default={
        'news':False,'low population':True,
        'attacks':True,'warehouse overflow or empty':False,'low budget':False
    })
    country = ReferenceField('Country',reverse_delete_rule=mongoengine.CASCADE)
    date_last_feedback = DateTimeField(default=timezone.now)

class Trade(Document):
    name = StringField(default='',max_length=100)
    default_price = FloatField(default=0.0,min_value=0)
    price_now = FloatField(default=0.0,min_value=0)
    history_price = EmbeddedDocumentListField('History',default=[])

class Cache(Document):
    top_players = StringField(default='')
    trade = StringField(default='')

class GlobalSettings(Document):
    # time in minutes
    feedback_pause = IntField(default=1440,min_value=1) # +
    email_notification = BooleanField(default=False) # +
    low_budget = IntField(default=1000,min_value=0) # +
    low_population = IntField(default=1000,min_value=0) # +
    frequency_email_notification = IntField(default=720,min_value=1)
    frequency_update_trade = IntField(default=10,min_value=0) # +
    frequency_update_top_players = IntField(default=5,min_value=0) # +
    frequency_check_warehouses = IntField(default=10,min_value=0) # +
    frequency_check_news = IntField(default=30,min_value=0) # +
    number_top_players = IntField(default=5,min_value=1) # +
    length_budget_graphics = IntField(default=10,min_value=1) # +
    length_population_graphics = IntField(default=10,min_value=1) # +
    length_goods_price_graphics = IntField(default=6,min_value=1) # +
    start_budget_k = FloatField(default=1.0,min_value=0.0) # +
    goods_price_scatter = FloatField(default=0.1,min_value=0.0) # +
    farm_workers_k = FloatField(default=1.0,min_value=0.0) # +
    mine_workers_k = FloatField(default=1.0,min_value=0.0) # +
    factory_workers_k = FloatField(default=1.0,min_value=0.0) # +
    farms_price_k = FloatField(default=1.0,min_value=0.1) # +
    mines_price_k = FloatField(default=1.0,min_value=0.1) # +
    factories_price_k = FloatField(default=1.0,min_value=0.1) # +
    warehouses_price_k = FloatField(default=1.0,min_value=0.1) # +
    technology_price_k = FloatField(default=1.0,min_value=0.1) # +
    laws_price_k = FloatField(default=1.0,min_value=0.1) # +
    farms_production_k = FloatField(default=1.0,min_value=0.1) # +
    mines_production_k = FloatField(default=1.0,min_value=0.1) # +
    factories_production_k = FloatField(default=1.0,min_value=0.1) # +
    army_taxes_profit_k = FloatField(default=2.0,min_value=0.1) # +
    pop_taxes_profit_k = FloatField(default=0.05,min_value=0.1) # +
    farms_taxes_profit_k = FloatField(default=0.1,min_value=0.1) # +
    mines_taxes_profit_k = FloatField(default=0.1,min_value=0.1) # +
    factories_taxes_profit_k = FloatField(default=0.1,min_value=0.1) # +