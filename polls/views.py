from django.contrib.auth.models import User
from django.http import HttpResponse

from django.shortcuts import redirect
from django.utils import timezone
from rest_framework.parsers import JSONParser
from rest_framework import status

from polls.models import User, Country
from rest_framework.decorators import api_view
from mongoengine import *

import json

from polls.services.game_service import GameService
from polls.services.system_service import SystemService
from polls.services.user_service import UserService
from polls.services.view_service import CountryViewService, NewsViewService, PlayerViewService

connect('TestDb')

def index(request):
    return redirect('/login')

@api_view(['POST'])
def login(request,username,password):
    if request.method == 'POST':
        try:
            user = User.objects(username=username).first()
            result_bool = UserService().login(username,password)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return HttpResponse(user._id, status=status.HTTP_202_ACCEPTED) if result_bool else HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
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
            if result_bool:
                UserService().login(request_data['username'],request_data['password'])
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return HttpResponse(User.objects(username=request_data['username']).first()._id, status=status.HTTP_201_CREATED) if result_bool else HttpResponse({},status=status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['DELETE'])
def delete_account(request,user_id,password):
    if request.method == 'DELETE':
        try:
            if not User.objects(_id=user_id).first().isAuth:
                return HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
            result_bool = UserService().delete_user_account(user_id,password)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return HttpResponse({}, status=status.HTTP_200_OK) if result_bool else HttpResponse({},status=status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['PUT'])
def change_user_data(request,user_id):
    if request.method == 'PUT':
        try:
            if not User.objects(_id=user_id).first().isAuth:
                return HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
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
            if not user.isAuth:
                return HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
            request_data = JSONParser().parse(request)
            if user is not None:
                SystemService().get_feedback(user.username,user.email,request_data['rating'],request_data['msg'])
                return HttpResponse({}, status=status.HTTP_200_OK)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return HttpResponse({},status=status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def find_player(request, user_id, player_name):
    if request.method == 'POST':
        try:
            user = User.objects(_id=user_id).first()
            if not user.isAuth:
                return HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
            request_users = list(filter(lambda x: player_name in x.username,User.objects()))
            if request_users:
                view_list = [PlayerViewService().get_player(user.username) for user in request_users]
                return HttpResponse(json.dumps(view_list, default=lambda x: x.__dict__), status=status.HTTP_200_OK)
            return HttpResponse({}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def get_view(request,user_id,name_view):
    if request.method == 'GET':
        try:
            if not User.objects(_id=user_id).first().isAuth:
                return HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
            view_obj = None
            if name_view == 'BasicStatistic':
                view_obj = CountryViewService().get_basic_statistic(user_id)
            elif name_view == 'Budget':
                view_obj = CountryViewService().get_budget(user_id)
            elif name_view == 'Technologies':
                view_obj = CountryViewService().get_technologies(user_id)
            elif name_view == 'Industry':
                view_obj = CountryViewService().get_industry(user_id)
            elif name_view == 'Warehouses':
                view_obj = CountryViewService().get_warehouses(user_id)
            elif name_view == 'Politics':
                view_obj = CountryViewService().get_politics_laws(user_id)
            elif name_view == 'Population':
                view_obj = CountryViewService().get_population(user_id)
            elif name_view == 'Trade':
                view_obj = CountryViewService().get_trade(user_id)
            elif name_view == 'Army':
                view_obj = CountryViewService().get_army(user_id)
            elif name_view == 'News':
                view_obj = NewsViewService().get_news()
            elif name_view == 'Settings':
                view_obj = SystemService().get_user_settings(user_id)
            elif name_view == 'Account':
                view_obj = PlayerViewService().get_account(user_id)
            elif name_view == 'TopPlayers':
                view_obj = PlayerViewService().get_view_page(user_id)

            return HttpResponse(json.dumps(view_obj, default=lambda x: x.__dict__), status=status.HTTP_200_OK)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['PUT'])
def change_taxes(request,user_id):
    if request.method == 'PUT':
        try:
            user = User.objects(_id=user_id).first()
            if not user.isAuth:
                return HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
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
            if not user.isAuth:
                return HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
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
            if not user.isAuth:
                return HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
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
            if not user.isAuth:
                return HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
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
            if not user.isAuth:
                return HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
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
            if not user.isAuth:
                return HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
            country = Country.objects(_id=user.country._id).first()
            request_data = JSONParser().parse(request)
            names_political_laws = ['Isolation','Free medicine','Free housing','Free education']
            if request_data['name_law'] in names_political_laws:
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
            if not user.isAuth:
                return HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
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
            if not user.isAuth:
                return HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
            country = Country.objects(_id=user.country._id).first()
            request_data = JSONParser().parse(request)
            GameService().buy_goods(country.name, request_data['name_goods'],int(request_data['number']))
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
            if not user.isAuth:
                return HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
            country = Country.objects(_id=user.country._id).first()
            request_data = JSONParser().parse(request)
            GameService().sell_goods(country.name, request_data['name_goods'],int(request_data['number']))
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
            if not user.isAuth:
                return HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
            country = Country.objects(_id=user.country._id).first()
            request_data = JSONParser().parse(request)
            GameService().edit_army(country.name,request_data['name_unit'],int(request_data['new_number']))
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
            if not user_1.isAuth:
                return HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
            if user_1.username != user_2.username:
                country_1,country_2 = Country.objects(_id=user_1.country._id).first(),Country.objects(_id=user_2.country._id).first()
                view_obj = GameService().calculate_war(country_1.name,country_2.name)
                # send email to attacked player
                return HttpResponse(json.dumps(view_obj, default=lambda x: x.__dict__), status=status.HTTP_200_OK)
            return HttpResponse({}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['PUT'])
def set_settings(request,user_id):
    if request.method == 'PUT':
        try:
            user = User.objects(_id=user_id).first()
            if not user.isAuth:
                return HttpResponse({}, status=status.HTTP_401_UNAUTHORIZED)
            request_data = JSONParser().parse(request)
            SystemService().set_user_settings(user,request_data['setting_list'])
            return HttpResponse({}, status=status.HTTP_200_OK)
        except Exception as error:
            return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return HttpResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
