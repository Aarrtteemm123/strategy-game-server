from django.http import HttpResponse


from django.http.response import JsonResponse
from django.shortcuts import redirect
from rest_framework.parsers import JSONParser
from rest_framework import status

from polls.models import User, Trade, Country, News
from polls.serializers import UserSerializer, TradeSerializer, CountrySerializer, NewsSerializer
from rest_framework.decorators import api_view
from mongoengine import *

import pymongo,json

from polls.view_models.basic_statistic import BasicStatisticView

connect('TestDb')

def index(request):
    return redirect('/login')

@api_view(['POST'])
def login(request,username,password):
    if request.method == 'POST':
        # code...
        return JsonResponse({}, status=status.HTTP_202_ACCEPTED, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)

@api_view(['POST'])
def logout(request,user_id):
    if request.method == 'POST':
        # code...
        return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)

@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        # code...
        return JsonResponse({}, status=status.HTTP_201_CREATED, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)

@api_view(['DELETE'])
def delete_account(request,user_id):
    if request.method == 'DELETE':
        # code...
        print('user was deleted '+str(user_id))
        return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)

@api_view(['PUT'])
def change_user_data(request,user_id):
    if request.method == 'PUT':
        # code...
        print('user was deleted '+str(user_id))
        return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)

@api_view(['GET'])
def get_news(request,user_id):
    if request.method == 'GET':
        # code...
        return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)

@api_view(['POST'])
def redirect_feedback(request,user_id):
    if request.method == 'POST':
        # code...
        return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)

@api_view(['GET'])
def get_all(request,user_id):
    if request.method == 'GET':
        # code...
        return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)

@api_view(['PUT'])
def change_taxes(request,user_id):
    if request.method == 'PUT':
        # code...
        return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)

@api_view(['PUT'])
def upgrade_technology(request,user_id):
    if request.method == 'PUT':
        # code...
        return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)

@api_view(['PUT'])
def build_industry(request,user_id):
    if request.method == 'PUT':
        # code...
        return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)

@api_view(['PUT'])
def remove_industry(request,user_id):
    if request.method == 'PUT':
        # code...
        return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)

@api_view(['PUT'])
def upgrade_warehouse(request,user_id):
    if request.method == 'PUT':
        # code...
        return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)

@api_view(['PUT'])
def set_law(request,user_id):
    if request.method == 'PUT':
        # code...
        return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)

@api_view(['PUT'])
def cancel_law(request,user_id):
    if request.method == 'PUT':
        # code...
        return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)

@api_view(['POST'])
def buy_goods(request,user_id):
    if request.method == 'POST':
        # code...
        return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)

@api_view(['POST'])
def sell_goods(request,user_id):
    if request.method == 'POST':
        # code...
        return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)


@api_view(['PUT'])
def edit_army(request,user_id):
    if request.method == 'PUT':
        # code...
        return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)

@api_view(['POST'])
def calculate_war(request,user_id,defending_player_id):
    if request.method == 'POST':
        # code...
        return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
    else:
        return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False)







@api_view(['GET', 'POST', 'DELETE'])
def tutorial_list(request):
    if request.method == 'GET':
        users = News.objects
        serializer = NewsSerializer(users,many=True)
        print(serializer.data)
        bs = BasicStatisticView()

        return JsonResponse(serializer.data,safe=False)

    if request.method == 'POST':
        tutorial_data = JSONParser().parse(request)
        tutorial_serializer = UserSerializer(data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET list of tutorials, POST a new tutorial, DELETE all tutorials


@api_view(['GET', 'PUT', 'DELETE'])
def tutorial_detail(request, pk):
    # find tutorial by pk (id)
    try:
        tutorial = User.objects.get(pk=pk)
        if request.method == 'GET':
            tutorial_serializer = TutorialSerializer(tutorial)
            return JsonResponse(tutorial_serializer.data)
        elif request.method == 'PUT':
            tutorial_data = JSONParser().parse(request)
            tutorial_serializer = TutorialSerializer(tutorial, data=tutorial_data)
            if tutorial_serializer.is_valid():
                tutorial_serializer.save()
                return JsonResponse(tutorial_serializer.data)
            return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            tutorial.delete()
            return JsonResponse({'message': 'Tutorial was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return JsonResponse({'message': 'The tutorial does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # GET / PUT / DELETE tutorial