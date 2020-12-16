import mongoengine
from django.utils import timezone
from mongoengine import *

connect('TestDb')

class News(Document):
    _id = ObjectIdField()
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
    military_expenses = IntField(default=0,min_value=0)
    profit_history = EmbeddedDocumentListField('History',default=[])
    expenses_history = EmbeddedDocumentListField('History',default=[])

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
    increasePrice = FloatField(default=0,min_value=0)
    modifiers = EmbeddedDocumentListField('Modifier',default=[])

class Goods(EmbeddedDocument):
    name = StringField(default='',max_length=100)
    value = IntField(default=0,min_value=0)
    link_img = StringField(default='',max_length=100)

class IndustrialBuildings(EmbeddedDocument):
    name = StringField(default='',max_length=100)
    link_img = StringField(default='',max_length=100)
    production_speed = FloatField(default=0,min_value=0)
    price_build = IntField(default=0,min_value=0)
    workers = IntField(default=0,min_value=0)
    number = IntField(default=0,min_value=0)
    needGoods = EmbeddedDocumentListField('Goods',default=[])
    isWorking = BooleanField(default=True)

class Warehouse(EmbeddedDocument):
    goods = EmbeddedDocumentField('Goods')
    capacity = IntField(default=0)
    filling_speed = FloatField(default=0.0)
    level = IntField(default=0,min_value=0,max_value=100)
    max_level = IntField(default=0,min_value=0)
    price_upgrade = IntField(default=0,min_value=0)
    added_capacity = IntField(default=0,min_value=0)
    increasePrice = FloatField(default=0,min_value=0)

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
    _id = ObjectIdField()
    link_img = StringField(default='',max_length=1000)
    name = StringField(default='',max_length=100,unique=True)
    budget = EmbeddedDocumentField('Budget')
    technologies = EmbeddedDocumentListField('Technology',default=[])
    farms = EmbeddedDocumentListField('IndustrialBuildings',default=[])
    mines = EmbeddedDocumentListField('IndustrialBuildings',default=[])
    factories = EmbeddedDocumentListField('IndustrialBuildings',default=[])
    military_factories = EmbeddedDocumentListField('IndustrialBuildings',default=[])
    industry_modifiers = EmbeddedDocumentListField('Modifier',default=[])
    warehouses = EmbeddedDocumentListField('Warehouse',default=[])
    adopted_laws = ListField(default=[])
    population = EmbeddedDocumentField('Population')
    army = EmbeddedDocumentField('Army')

class User(Document):
    _id = ObjectIdField()
    isAuth = BooleanField(default=False)
    username = StringField(default='', max_length=100,unique=True)
    password = StringField(default='', max_length=100)
    email = EmailField(default='user_email@gmail.com')
    date_registration = DateTimeField(default=timezone.now)
    settings = DictField(default={
        'news':False,'updates':True,
        'attacks':True,'warehouse overflow':False,'low budget':False
    })
    country = ReferenceField('Country',reverse_delete_rule=mongoengine.CASCADE)
    date_last_send_feedback = DateTimeField(default=timezone.now)

class Trade(Document):
    _id = ObjectIdField()
    name = StringField(default='',max_length=100)
    price_now = FloatField(default=0.0,min_value=0)
    history_price = EmbeddedDocumentListField('History',default=[])