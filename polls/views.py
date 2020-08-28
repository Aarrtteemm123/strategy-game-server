import time

from django.contrib.auth.models import User
from django.http import HttpResponse

from django.http.response import JsonResponse
from django.shortcuts import redirect
from rest_framework.parsers import JSONParser
from rest_framework import status

from polls.models import User, Country
from polls.serializers import UserSerializer, CountrySerializer
from rest_framework.decorators import api_view
from mongoengine import *

import json

from polls.services.game_service import GameService
from polls.services.system_service import SystemService
from polls.services.user_service import UserService
from polls.services.view_service import CountryViewService, NewsViewService
from polls.view_models.basic_statistic import BasicStatisticView

connect('TestDb')

def index(request):
    return redirect('/login')

@api_view(['POST'])
def login(request,username,password):
    if request.method == 'POST':
        try:
            result_bool = UserService().login(username,password)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return HttpResponse({}, status=status.HTTP_202_ACCEPTED) if result_bool else HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def logout(request,user_id):
    if request.method == 'POST':
        try:
            result_bool = UserService().logout(user_id)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return HttpResponse({}, status=status.HTTP_200_OK) if result_bool else HttpResponse({},status=status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        try:
            request_data = JSONParser().parse(request)
            result_bool = UserService().register_new_user(request_data['username'],request_data['password'],request_data['email'],request_data['country_name'],request_data['link_on_flag'])
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return HttpResponse({}, status=status.HTTP_201_CREATED) if result_bool else HttpResponse({},status=status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['DELETE'])
def delete_account(request,user_id,password):
    if request.method == 'DELETE':
        try:
            result_bool = UserService().delete_user_account(user_id,password)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return HttpResponse({}, status=status.HTTP_204_NO_CONTENT) if result_bool else HttpResponse({},status=status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['PUT'])
def change_user_data(request,user_id):
    if request.method == 'PUT':
        try:
            request_data = JSONParser().parse(request)
            result_bool = UserService().change_user_data(user_id,request_data['username'],request_data['password'],request_data['country_name'],request_data['link_on_flag'])
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return HttpResponse({}, status=status.HTTP_200_OK) if result_bool else HttpResponse({},status=status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def redirect_feedback(request,user_id):
    if request.method == 'POST':
        try:
            user = User.objects(_id=user_id).first()
            request_data = JSONParser().parse(request)
            if user is not None:
                SystemService().get_feedback(request_data['username'],request_data['email'],request_data['rating'],request_data['msg'])
                return HttpResponse({}, status=status.HTTP_200_OK)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return HttpResponse({},status=status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def get_all(request,user_id):
    if request.method == 'GET':
        try:
            obj = {
                'basic statistic':CountryViewService().get_basic_statistic(user_id),
                'budget':CountryViewService().get_budget(user_id),
                'technologies':CountryViewService().get_technologies(user_id),
                'industry':CountryViewService().get_industry(user_id),
                'warehouses':CountryViewService().get_warehouses(user_id),
                'adopted politics laws':CountryViewService().get_politics_laws(user_id),
                'population':CountryViewService().get_population(user_id),
                'trade':CountryViewService().get_trade(user_id),
                'army':CountryViewService().get_army(user_id),
                'news':NewsViewService().get_news()
            }
            return HttpResponse(json.dumps(obj, default=lambda x: x.__dict__), status=status.HTTP_200_OK)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['PUT'])
def change_taxes(request,user_id):
    if request.method == 'PUT':
        try:
            user = User.objects(_id=user_id).first()
            country = Country.objects(_id=user.country._id).first()
            request_data = JSONParser().parse(request)
            GameService().set_taxes(country.name,request_data['name_tax'],request_data['new_value'])
            return HttpResponse({}, status=status.HTTP_200_OK)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['PUT'])
def upgrade_technology(request,user_id):
    if request.method == 'PUT':
        try:
            user = User.objects(_id=user_id).first()
            country = Country.objects(_id=user.country._id).first()
            request_data = JSONParser().parse(request)
            GameService().upgrade_technology(country.name, request_data['name_technology'])
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return HttpResponse({}, status=status.HTTP_200_OK)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['PUT'])
def build_industry(request,user_id):
    if request.method == 'PUT':
        try:
            user = User.objects(_id=user_id).first()
            country = Country.objects(_id=user.country._id).first()
            request_data = JSONParser().parse(request)
            GameService().build_industry(country.name,request_data['name_building'])
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return HttpResponse({}, status=status.HTTP_200_OK)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['PUT'])
def remove_industry(request,user_id):
    if request.method == 'PUT':
        try:
            user = User.objects(_id=user_id).first()
            country = Country.objects(_id=user.country._id).first()
            request_data = JSONParser().parse(request)
            GameService().remove_industry(country.name, request_data['name_building'])
            return HttpResponse({}, status=status.HTTP_200_OK)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['PUT'])
def upgrade_warehouse(request,user_id):
    if request.method == 'PUT':
        try:
            user = User.objects(_id=user_id).first()
            country = Country.objects(_id=user.country._id).first()
            request_data = JSONParser().parse(request)
            GameService().upgrade_warehouse(country.name, request_data['name_warehouse'])
            return HttpResponse({}, status=status.HTTP_200_OK)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['PUT'])
def set_law(request,user_id):
    if request.method == 'PUT':
        try:
            user = User.objects(_id=user_id).first()
            country = Country.objects(_id=user.country._id).first()
            request_data = JSONParser().parse(request)
            names_political_laws = ['Immigration','Isolation','Free housing','Free education']
            if remove_industry.name_law in names_political_laws:
                GameService().set_politics_law(country.name, request_data['name_law'])
            else:
                GameService().set_conscript_law(country.name, request_data['name_law'])
            return HttpResponse({}, status=status.HTTP_200_OK)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['PUT'])
def cancel_law(request,user_id):
    if request.method == 'PUT':
        try:
            user = User.objects(_id=user_id).first()
            country = Country.objects(_id=user.country._id).first()
            request_data = JSONParser().parse(request)
            GameService().cancel_politics_law(country.name, request_data['name_law'])
            return HttpResponse({}, status=status.HTTP_200_OK)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def buy_goods(request,user_id):
    if request.method == 'POST':
        try:
            user = User.objects(_id=user_id).first()
            country = Country.objects(_id=user.country._id).first()
            request_data = JSONParser().parse(request)
            GameService().buy_goods(country.name, request.request_data['name_goods'],request_data['number'])
            return HttpResponse({}, status=status.HTTP_200_OK)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def sell_goods(request,user_id):
    if request.method == 'POST':
        try:
            user = User.objects(_id=user_id).first()
            country = Country.objects(_id=user.country._id).first()
            request_data = JSONParser().parse(request)
            GameService().sell_goods(country.name, request.request_data['name_goods'],request_data['number'])
            return HttpResponse({}, status=status.HTTP_200_OK)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['PUT'])
def edit_army(request,user_id):
    if request.method == 'PUT':
        try:
            user = User.objects(_id=user_id).first()
            country = Country.objects(_id=user.country._id).first()
            request_data = JSONParser().parse(request)
            GameService().edit_army(country.name,request_data['name_unit'],request_data['new_number'])
            return HttpResponse({}, status=status.HTTP_200_OK)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def calculate_war(request,user_id,defending_player_name):
    if request.method == 'POST':
        try:
            user_1,user_2 = User.objects(_id=user_id).first(),User.objects(username=defending_player_name).first()
            country_1,country_2 = Country.objects(_id=user_1.country._id).first(),Country.objects(_id=user_2.country._id).first()
            GameService().calculate_war(country_1.name,country_2.username)
            return HttpResponse({}, status=status.HTTP_200_OK)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)







@api_view(['GET', 'POST', 'DELETE'])
def tutorial_list(request):
    if request.method == 'GET':
        #print(UserService().register_new_user('ar3', '123', 'test@gmail.com', 'c4', 'img'))

        news = Country.objects(id='5f1dc17211fc3660885d8d24').only('name')
        serializer = CountrySerializer(news,many=True)
        bs = BasicStatisticView()

        return JsonResponse(serializer.data,safe=False)

    if request.method == 'POST':
        tutorial_data = JSONParser().parse(request)
        tutorial_serializer = UserSerializer(data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


