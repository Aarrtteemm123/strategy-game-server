import pymongo
from mongoengine import *

from polls.models import User
from polls.serializers import UserSerializer

connect('TestDb')
users = User.objects.find_one()
serializer = UserSerializer(users, many=True)
print(serializer.data)