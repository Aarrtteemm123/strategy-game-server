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
    address_from = serializers.CharField()
    address_to = serializers.CharField()

class HistorySerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.FloatField()
    time = serializers.DateTimeField()

class BudgetSerializer(serializers.Serializer):
    money = serializers.IntegerField()
    population_taxes = serializers.IntegerField()
    farms_taxes = serializers.IntegerField()
    mines_taxes = serializers.IntegerField()
    factories_taxes = serializers.IntegerField()
    military_taxes = serializers.IntegerField()
    military_expenses = serializers.IntegerField()
    profit_history = HistorySerializer(required=False,many=True)
    expenses_history = HistorySerializer(required=False,many=True)

class TechnologiesSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    price_upgrade = serializers.IntegerField()
    level = serializers.IntegerField()
    max_level = serializers.IntegerField(read_only=True)
    total_result = serializers.FloatField()
    increasePrice = serializers.FloatField(read_only=True)
    modifiers = ModifierSerializer(required=False,many=True)

class GoodsSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    value = serializers.IntegerField()
    link_img = serializers.CharField(read_only=True)

class IndustrialBuildingsSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    link_img = serializers.CharField(read_only=True)
    production_speed = serializers.FloatField()
    price_build =  serializers.IntegerField()
    workers =  serializers.IntegerField()
    number =  serializers.IntegerField()
    needGoods = GoodsSerializer(required=False,many=True)
    isWorking = serializers.BooleanField()

class WarehouseSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    link_img = serializers.CharField(read_only=True)
    value = serializers.FloatField()
    capacity = serializers.IntegerField()
    filling_speed =serializers.FloatField()
    level = serializers.IntegerField()
    max_level = serializers.IntegerField(read_only=True)
    price_upgrade = serializers.IntegerField()
    added_capacity = serializers.IntegerField()
    increasePrice = serializers.FloatField(read_only=True)

class LawSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    price = serializers.IntegerField()
    modifiers = ModifierSerializer(required=False,many=True)

class PopulationSerializer(serializers.Serializer):
    total_population = serializers.IntegerField()
    factory_workers = serializers.IntegerField()
    miners = serializers.IntegerField()
    farmers = serializers.IntegerField()
    solders = serializers.IntegerField()
    free_people = serializers.IntegerField()
    others = serializers.IntegerField()
    min_percent_others = serializers.IntegerField()
    basic_percent_growth_rate = serializers.IntegerField()
    modifiers = ModifierSerializer(required=False,many=True)
    population_history = HistorySerializer(required=False,many=True)

class ArmyUnitCharacteristicSerializer(serializers.Serializer):
    unit_name = serializers.CharField(read_only=True)
    attack_value = serializers.FloatField()
    defence_value = serializers.FloatField()

class ArmyUnitSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    link_img = serializers.CharField(read_only=True)
    need_peoples = serializers.IntegerField(read_only=True)
    maintenance_price = serializers.IntegerField()
    unit_characteristic = serializers.DictField(child=ArmyUnitCharacteristicSerializer())

class ArmySerializer(serializers.Serializer):
    conscript_law_value = serializers.FloatField()
    reserve_military_manpower = serializers.IntegerField()
    victories = serializers.IntegerField()
    losses = serializers.IntegerField()
    attack_modifiers = ModifierSerializer(required=False,many=True)
    defence_modifiers = ModifierSerializer(required=False,many=True)
    units = serializers.DictField(default={})

class CountrySerializer(serializers.Serializer):
    link_img = serializers.CharField()
    name = serializers.CharField()
    budget = BudgetSerializer(required=False)
    technologies = TechnologiesSerializer(required=False,many=True)
    farms = IndustrialBuildingsSerializer(required=False,many=True)
    mines = IndustrialBuildingsSerializer(required=False,many=True)
    factories = IndustrialBuildingsSerializer(required=False,many=True)
    military_factories = IndustrialBuildingsSerializer(required=False,many=True)
    industry_modifiers = ModifierSerializer(required=False,many=True)
    warehouses = WarehouseSerializer(required=False,many=True)
    adopted_laws = LawSerializer(required=False,many=True)
    population = PopulationSerializer(required=False)
    army = ArmySerializer(required=False)

class UserSerializer(serializers.Serializer):
    _id = ObjectIdField(read_only=True)
    isAuth = serializers.BooleanField()
    username = serializers.CharField()
    password = serializers.CharField()
    email = serializers.EmailField()
    dateRegistration = serializers.DateTimeField(read_only=True)
    settings = serializers.DictField()
    country = CountrySerializer(required=False)
    date_last_send_feedback = serializers.DateTimeField()

class NewsSerializer(serializers.Serializer):
    _id = ObjectIdField(read_only=True)
    title = serializers.CharField()
    date = serializers.DateTimeField()
    text = serializers.CharField()

class TradeSerializer(serializers.Serializer):
    _id = ObjectIdField(read_only=True)
    name = serializers.CharField(read_only=True)
    price_now = serializers.FloatField()
    history_price = HistorySerializer(required=False,many=True)
