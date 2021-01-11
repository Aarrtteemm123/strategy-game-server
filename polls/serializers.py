from bson import ObjectId
from bson.errors import InvalidId
from django.utils.encoding import smart_text
from rest_framework import serializers, fields
from rest_framework_mongoengine import serializers, fields as field

from polls.models import News


class NewsSerializer(serializers.DocumentSerializer):
    name = fields.CharField(required=True)
    class Meta:
        model = News
        fields = '__all__'
