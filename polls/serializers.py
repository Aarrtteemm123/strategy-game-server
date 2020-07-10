
from rest_framework import serializers

class CountrySerializer(serializers.Serializer):
    linkImg = serializers.URLField()
    name = serializers.CharField(max_length=100)

class PersonalDataSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    dateRegistration = serializers.DateTimeField()

class UserSerializer(serializers.Serializer):
    personalData = PersonalDataSerializer(required=False)
    country = CountrySerializer(required=False)
