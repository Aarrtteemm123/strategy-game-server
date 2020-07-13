from datetime import date, datetime

from django.utils import timezone
from mongoengine import *

connect('TestDb')

class News(Document):
    title = StringField(default='title news')
    date = DateTimeField(default=timezone.now)
    text = StringField(default='text news')

class Budget(EmbeddedDocument):
    money = IntField(default=10000)
    population_taxes = IntField(default=0)
    farms_taxes = IntField(default=0)
    mines_taxes = IntField(default=0)
    factories_taxes = IntField(default=0)
    military_taxes = IntField(default=0)
    military_expenses = IntField(default=0)

class Modifier(EmbeddedDocument):
    value = FloatField(default=0)
    address = StringField(default='From...')
    to = StringField(default='to...')

class Technology(EmbeddedDocument):
    name = StringField(default='name technology')
    price_upgrade = IntField(default=5000)
    level = IntField(default=1)
    max_level = IntField(default=100)
    total_result = FloatField(default=0)
    increasePrice = FloatField(default=1.5)
    modifiers = EmbeddedDocumentListField('Modifier',default=[Modifier(),Modifier()])

class Goods(EmbeddedDocument):
    name = StringField(default='Name goods...')
    value = IntField(default=0)
    link_img = StringField(default='Image link...')

class IndustrialBuildings(EmbeddedDocument):
    name = StringField(default='name...')
    link_img = StringField(default='None image')
    production_speed = FloatField(default=1)
    price_build = IntField(default=10000)
    workers = IntField(default=500)
    number = IntField(default=0)
    needGoods =  EmbeddedDocumentListField('Goods',default=[Goods()])

class Warehouse(EmbeddedDocument):
    name = StringField(default='name...')
    link_img = StringField(default='None image')
    value = FloatField(default=0)
    capacity = IntField(default=1000)
    filling_speed = FloatField(default=1)
    level = IntField(default=1)
    max_level = IntField(default=100)
    price_upgrade = IntField(default=10000)
    added_capacity = IntField(default=1000)
    increasePrice = FloatField(default=1.5)

class PoliticalLaw(EmbeddedDocument):
    name = StringField(default='name...')
    description = StringField(default='description law ...')
    price = IntField(default=1000)
    modifiers = EmbeddedDocumentListField('Modifier', default=[Modifier(), Modifier()])

class Population(EmbeddedDocument):
    total_population = IntField(default=100000)
    factory_workers = IntField(default=20000)
    miners = IntField(default=10000)
    farmers = IntField(default=30000)
    solders = IntField(default=15000)
    others = IntField(default=25000)
    min_percent_others = IntField(default=20)
    basic_percent_growth_rate = IntField(default=5)
    modifiers = EmbeddedDocumentListField('Modifier', default=[Modifier()])

class ArmyUnitCharacteristic(EmbeddedDocument):
    unit_name = StringField(default='unit name ...')
    attack_value = FloatField(default=10)
    defence_value = FloatField(default=10)

class ArmyUnit(EmbeddedDocument):
    name = StringField(default='type unit...')
    link_img = StringField(default='link on image...')
    number = IntField(default=1)
    need_peoples = IntField(default=1)
    maintenance_price = IntField(default=10)
    modifiers = EmbeddedDocumentListField('Modifier', default=[Modifier()])
    unit_characteristic = DictField(EmbeddedDocumentField('ArmyUnitCharacteristic'),default={'Infantry':ArmyUnitCharacteristic(),'Artillery':ArmyUnitCharacteristic()})

class Army(EmbeddedDocument):
    reserve_military_manpower = IntField(default=100000)
    victories = IntField(default=0)
    losses = IntField(default=0)
    units = DictField(EmbeddedDocumentField('ArmyUnit'),default={'Infantry':ArmyUnit(),'Artillery':ArmyUnit()})

class Country(EmbeddedDocument):
    link_img = StringField(default='None image')
    name = StringField(default='name country')
    budget = EmbeddedDocumentField('Budget')
    technologies = EmbeddedDocumentListField('Technology',default=[Technology(),Technology()])
    farms = EmbeddedDocumentListField('IndustrialBuildings',default=[IndustrialBuildings(),IndustrialBuildings()])
    mines = EmbeddedDocumentListField('IndustrialBuildings',default=[IndustrialBuildings(),IndustrialBuildings()])
    factories = EmbeddedDocumentListField('IndustrialBuildings',default=[IndustrialBuildings(),IndustrialBuildings()])
    military_factories = EmbeddedDocumentListField('IndustrialBuildings',default=[IndustrialBuildings(),IndustrialBuildings()])
    warehouses = EmbeddedDocumentListField('Warehouse',default=[Warehouse(),Warehouse(),Warehouse(),Warehouse(),Warehouse()])
    adopted_laws = EmbeddedDocumentListField('PoliticalLaw', default=[PoliticalLaw(),PoliticalLaw()])
    population = EmbeddedDocumentField('Population')
    army = EmbeddedDocumentField('Army')

class PersonalData(EmbeddedDocument):
    username = StringField(default='your name')
    password = StringField(default='your password')
    email = EmailField(default='test12@gmail.com')
    date_registration = DateTimeField(default=timezone.now)

class User(Document):
    _id = ObjectIdField()
    personal_data = EmbeddedDocumentField('PersonalData')
    settings = DictField(default={'set1':False,'set2':True,'set3':False})
    country = EmbeddedDocumentField('Country')
    date_last_send_feedback = DateTimeField()

budget = Budget()
pop = Population()
army = Army()
persData = PersonalData(username='David',password='45fg',email='dav34@gmail.com')
country = Country(link_img='link/on/img',name='Ukraine',budget=budget,population=pop,army=army)
user = User(personal_data=persData,country=country).save()

news = News().save()




