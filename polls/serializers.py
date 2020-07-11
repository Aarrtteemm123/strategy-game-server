from abc import ABC

from bson import ObjectId
from bson.errors import InvalidId
from django.utils.encoding import smart_text
from rest_framework import serializers

class ObjectIdField(serializers.Field):
    """ Serializer field for Djongo ObjectID fields """
    def to_internal_value(self, data):
        # Serialized value -> Database value
        try:
            return ObjectId(str(data))  # Get the ID, then build an ObjectID instance using it
        except InvalidId:
            raise serializers.ValidationError('`{}` is not a valid ObjectID'.format(data))

    def to_representation(self, value):
        # Database value -> Serialized value
        if not ObjectId.is_valid(value):  # User submitted ID's might not be properly structured
            raise InvalidId
        return smart_text(value)

class ModifierSerializer(serializers.Serializer):
    value = serializers.FloatField()
    address = serializers.CharField()
    to = serializers.CharField()

class BudgetSerializer(serializers.Serializer):
    money = serializers.IntegerField()
    population_taxes = serializers.IntegerField()
    farms_taxes = serializers.IntegerField()
    mines_taxes = serializers.IntegerField()
    factories_taxes = serializers.IntegerField()
    military_taxes = serializers.IntegerField()
    military_expenses = serializers.IntegerField()

class TechnologiesSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    price_upgrade = serializers.IntegerField()
    level = serializers.IntegerField()
    max_level = serializers.IntegerField()
    total_result = serializers.FloatField()
    increasePrice = serializers.FloatField()
    modifiers = ModifierSerializer(required=False,many=True)

class GoodsSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    value = serializers.IntegerField()
    link_img = serializers.CharField()

class IndustrialBuildingsSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    link_img = serializers.CharField(max_length=200)
    production_speed = serializers.FloatField()
    price_build =  serializers.IntegerField()
    workers =  serializers.IntegerField()
    number =  serializers.IntegerField()
    needGoods = GoodsSerializer(required=False,many=True)

class WarehouseSerializer(serializers.Serializer):
    name = serializers.CharField()
    link_img = serializers.CharField()
    value = serializers.FloatField()
    capacity = serializers.IntegerField()
    filling_speed =serializers.FloatField()
    level = serializers.IntegerField()
    max_level = serializers.IntegerField()
    price_upgrade = serializers.IntegerField()
    added_capacity = serializers.IntegerField()
    increasePrice = serializers.FloatField()

class PoliticalLawSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    price = serializers.IntegerField()
    modifiers = ModifierSerializer(required=False,many=True)

class PopulationSerializer(serializers.Serializer):
    total_population = serializers.IntegerField()
    factory_workers = serializers.IntegerField()
    miners = serializers.IntegerField()
    farmers = serializers.IntegerField()
    solders = serializers.IntegerField()
    others = serializers.IntegerField()
    min_percent_others = serializers.IntegerField()
    basic_percent_growth_rate = serializers.IntegerField()
    modifiers = ModifierSerializer(required=False,many=True)

class ArmyUnitCharacteristicSerializer(serializers.Serializer):
    unit_name = serializers.CharField()
    attack_value = serializers.FloatField()
    defence_value = serializers.FloatField()

class ArmyUnitSerializer(serializers.Serializer):
    name = serializers.CharField()
    link_img = serializers.CharField()
    number = serializers.IntegerField()
    need_peoples = serializers.IntegerField()
    maintenance_price = serializers.IntegerField()
    modifiers = ModifierSerializer(required=False,many=True)
    unit_characteristic = serializers.DictField(child=ArmyUnitCharacteristicSerializer())

class ArmySerializer(serializers.Serializer):
    reserve_military_manpower = serializers.IntegerField()
    units = serializers.DictField(child=ArmyUnitSerializer())

class CountrySerializer(serializers.Serializer):
    link_img = serializers.URLField()
    name = serializers.CharField(max_length=100)
    budget = BudgetSerializer(required=False)
    technologies = TechnologiesSerializer(required=False,many=True)
    farms = IndustrialBuildingsSerializer(required=False,many=True)
    mines = IndustrialBuildingsSerializer(required=False,many=True)
    factories = IndustrialBuildingsSerializer(required=False,many=True)
    military_factories = IndustrialBuildingsSerializer(required=False,many=True)
    warehouses = WarehouseSerializer(required=False,many=True)
    adopted_laws = PoliticalLawSerializer(required=False,many=True)
    population = PopulationSerializer(required=False)
    army = ArmySerializer(required=False)

class PersonalDataSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    dateRegistration = serializers.DateTimeField()

class UserSerializer(serializers.Serializer):
    _id = ObjectIdField(read_only=True)
    personalData = PersonalDataSerializer(required=False)
    settings = serializers.DictField()
    country = CountrySerializer(required=False)
