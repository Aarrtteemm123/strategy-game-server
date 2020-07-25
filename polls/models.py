import mongoengine
from django.utils import timezone
from mongoengine import *

connect('TestDb')

class News(Document):
    _id = ObjectIdField()
    title = StringField(default='',max_length=200)
    date = DateTimeField(default=timezone.now)
    text = StringField(default='',max_length=1000)

class Budget(EmbeddedDocument):
    money = IntField(default=0,min_value=-10000)
    population_taxes = IntField(default=0,min_value=0,max_value=100)
    farms_taxes = IntField(default=0,min_value=0,max_value=100)
    mines_taxes = IntField(default=0,min_value=0,max_value=100)
    factories_taxes = IntField(default=0,min_value=0,max_value=100)
    military_taxes = IntField(default=0,min_value=0,max_value=100)
    military_expenses = IntField(default=0,min_value=0)

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
    needGoods =  EmbeddedDocumentListField('Goods',default=[])

class Warehouse(EmbeddedDocument):
    name = StringField(default='',max_length=100)
    link_img = StringField(default='',max_length=100)
    value = FloatField(default=0.0,min_value=0)
    capacity = IntField(default=0)
    filling_speed = FloatField(default=0.0)
    level = IntField(default=0,min_value=0,max_value=100)
    max_level = IntField(default=0,min_value=0)
    price_upgrade = IntField(default=0,min_value=0)
    added_capacity = IntField(default=0,min_value=0)
    increasePrice = FloatField(default=0,min_value=0)

class PoliticalLaw(EmbeddedDocument):
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
    others = IntField(default=0,min_value=0)
    min_percent_others = IntField(default=0,min_value=0)
    basic_percent_growth_rate = IntField(default=0,min_value=0)
    modifiers = EmbeddedDocumentListField('Modifier', default=[])

class ArmyUnitCharacteristic(EmbeddedDocument):
    unit_name = StringField(default='',max_length=100)
    attack_value = FloatField(default=0,min_value=0)
    defence_value = FloatField(default=0,min_value=0)

class ArmyUnit(EmbeddedDocument):
    name = StringField(default='',max_length=100)
    link_img = StringField(default='',max_length=200)
    number = IntField(default=0,min_value=0)
    need_peoples = IntField(default=0,min_value=1)
    maintenance_price = IntField(default=0,min_value=1)
    modifiers = EmbeddedDocumentListField('Modifier', default=[])
    unit_characteristic = DictField(EmbeddedDocumentField('ArmyUnitCharacteristic'),default={})

class Army(EmbeddedDocument):
    reserve_military_manpower = IntField(default=0,min_value=0)
    victories = IntField(default=0,min_value=0)
    losses = IntField(default=0,min_value=0)
    units = DictField(EmbeddedDocumentField('ArmyUnit'),default={})

class Country(Document):
    link_img = StringField(default='',max_length=100)
    name = StringField(default='',max_length=100,unique=True)# unique=True
    budget = EmbeddedDocumentField('Budget')
    technologies = EmbeddedDocumentListField('Technology',default=[])
    farms = EmbeddedDocumentListField('IndustrialBuildings',default=[])
    mines = EmbeddedDocumentListField('IndustrialBuildings',default=[])
    factories = EmbeddedDocumentListField('IndustrialBuildings',default=[])
    military_factories = EmbeddedDocumentListField('IndustrialBuildings',default=[])
    warehouses = EmbeddedDocumentListField('Warehouse',default=[])
    adopted_laws = EmbeddedDocumentListField('PoliticalLaw', default=[])
    population = EmbeddedDocumentField('Population')
    army = EmbeddedDocumentField('Army')

class User(Document):
    _id = ObjectIdField() # unique=True
    isAuth = BooleanField(default=False)
    username = StringField(default='', max_length=100,unique=True)  # unique=True
    password = StringField(default='', max_length=100)
    email = EmailField(default='user_email@gmail.com')
    date_registration = DateTimeField(default=timezone.now)
    settings = DictField(default={})
    country = ReferenceField('Country',reverse_delete_rule=mongoengine.CASCADE)
    date_last_send_feedback = DateTimeField(default=timezone.now)

class HistoryPrice(EmbeddedDocument):
    value = FloatField(default=1.0,min_value=0)
    time = DateTimeField(default=timezone.now)

class Trade(Document):
    _id = ObjectIdField()
    name = StringField(default='',max_length=100)
    price_now = FloatField(default=0.0,min_value=0)
    history_price = EmbeddedDocumentListField('HistoryPrice',default=[])





