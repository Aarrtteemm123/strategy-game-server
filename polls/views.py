import json
from datetime import datetime

from django.contrib.auth.models import User
from django.http import HttpResponse

from django.shortcuts import redirect
from rest_framework.parsers import JSONParser
from rest_framework import status

from polls.models import User, Country, GlobalSettings
from rest_framework.decorators import api_view
from mongoengine import *
from polls.exceptions import *
from polls.services.game_service import GameService
from polls.services.system_service import SystemService, EmailEvent
from polls.services.user_service import UserService
from polls.services.view_service import CountryViewService, NewsViewService, PlayerViewService, FQAViewService
from serverDjango.settings import ADMIN_EMAIL

connect('TestDb')


def index(request):
    return redirect('/login')


@api_view(['POST'])
def login(request, username, password):
    try:
        token = UserService().login(username, password)
        user_id = User.objects(username=username, password=password).first().id
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HttpResponse(json.dumps({'token': token, 'user_id': str(user_id)}), status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
def logout(request, user_id):
    try:
        request_data = JSONParser().parse(request)
        if SystemService.verify_token(user_id, request_data['token']):
            UserService().logout(user_id)
        return HttpResponse({}, status=status.HTTP_200_OK)
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def register(request):
    try:
        request_data = JSONParser().parse(request)
        result_bool = UserService().register_new_user(request_data['username'], request_data['password'],
                                                      request_data['email'], request_data['country_name'],
                                                      request_data['link_on_flag'])
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HttpResponse({}, status=status.HTTP_201_CREATED) if result_bool else HttpResponse({},
                                                                                             status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_account(request, user_id, password):
    try:
        request_data = JSONParser().parse(request)
        if SystemService.verify_token(user_id, request_data['token']):
            UserService().delete_user_account(user_id, password)
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HttpResponse({}, status=status.HTTP_200_OK)


@api_view(['PUT'])
def change_user_data(request, user_id):
    try:
        request_data = JSONParser().parse(request)
        if SystemService.verify_token(user_id, request_data['token']):
            UserService().change_user_data(user_id, request_data['password'],
                                           request_data['country_name'], request_data['link_on_flag'])
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HttpResponse({}, status=status.HTTP_200_OK)


@api_view(['POST'])
def redirect_feedback(request, user_id):
    try:
        user = User.objects(id=user_id).first()
        request_data = JSONParser().parse(request)
        global_settings = GlobalSettings.objects().first()
        if SystemService.verify_token(user_id, request_data['token']):
            if (datetime.utcnow() - user.date_last_feedback).total_seconds()/60 >= global_settings.feedback_pause:
                user.date_last_feedback = datetime.utcnow()
                SystemService().send_notification([ADMIN_EMAIL],EmailEvent.FEEDBACK, user.username, request_data['msg'], request_data['rating'], user.email)
                user.save()
            else:
                return HttpResponse('You can send only 1 feedback in 24 hours',
                                    status=status.HTTP_208_ALREADY_REPORTED)
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HttpResponse({}, status=status.HTTP_200_OK)


@api_view(['POST'])
def find_player(request, user_id, player_name):
    try:
        request_data = JSONParser().parse(request)
        if SystemService.verify_token(user_id, request_data['token']):
            request_users = list(filter(lambda x: player_name in x.username, User.objects()))
            if request_users:
                view_list = [PlayerViewService().get_player(user.username) for user in request_users]
                return HttpResponse(json.dumps(view_list, default=lambda x: x.__dict__), status=status.HTTP_200_OK)
            return HttpResponse({}, status=status.HTTP_404_NOT_FOUND)
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def get_view(request, user_id, name_view):
    try:
        request_data = JSONParser().parse(request)
        if SystemService.verify_token(user_id, request_data['token']):
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
                view_obj = CountryViewService().get_cache_politics_laws(user_id)
            elif name_view == 'Population':
                view_obj = CountryViewService().get_population(user_id)
            elif name_view == 'Trade':
                view_obj = CountryViewService().get_cache_trade(user_id)
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
            elif name_view == 'FQA':
                view_obj = FQAViewService().get_FQA()
            return HttpResponse(json.dumps(view_obj, default=lambda x: x.__dict__), status=status.HTTP_200_OK)
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def change_taxes(request, user_id):
    try:
        user = User.objects(id=user_id).first()
        request_data = JSONParser().parse(request)
        if SystemService.verify_token(user_id,request_data['token']):
            country = Country.objects(id=user.country.id).first()
            GameService().set_taxes(country, request_data['name_tax'], request_data['new_value'])
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HttpResponse({}, status=status.HTTP_200_OK)


@api_view(['PUT'])
def upgrade_technology(request, user_id):
    try:
        user = User.objects(id=user_id).first()
        request_data = JSONParser().parse(request)
        if SystemService.verify_token(user_id,request_data['token']):
            country = Country.objects(id=user.country.id).first()
            GameService().upgrade_technology(country, request_data['name_technology'])
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HttpResponse({}, status=status.HTTP_200_OK)


@api_view(['PUT'])
def build_industry(request, user_id):
    try:
        user = User.objects(id=user_id).first()
        request_data = JSONParser().parse(request)
        if SystemService.verify_token(user_id,request_data['token']):
            country = Country.objects(id=user.country.id).first()
            GameService().build_industry(country, request_data['name_building'])
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HttpResponse({}, status=status.HTTP_200_OK)


@api_view(['PUT'])
def remove_industry(request, user_id):
    try:
        user = User.objects(id=user_id).first()
        request_data = JSONParser().parse(request)
        if SystemService.verify_token(user_id,request_data['token']):
            country = Country.objects(id=user.country.id).first()
            GameService().remove_industry(country, request_data['name_building'])
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HttpResponse({}, status=status.HTTP_200_OK)


@api_view(['PUT'])
def upgrade_warehouse(request, user_id):
    try:
        user = User.objects(id=user_id).first()
        request_data = JSONParser().parse(request)
        if SystemService.verify_token(user_id,request_data['token']):
            country = Country.objects(id=user.country.id).first()
            GameService().upgrade_warehouse(country, request_data['name_warehouse'])
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HttpResponse({}, status=status.HTTP_200_OK)


@api_view(['PUT'])
def set_law(request, user_id):
    try:
        user = User.objects(id=user_id).first()
        request_data = JSONParser().parse(request)
        if SystemService.verify_token(user_id,request_data['token']):
            country = Country.objects(id=user.country.id).first()
            names_political_laws = ['Isolation', 'Free medicine', 'Free housing', 'Free education']
            if request_data['name_law'] in names_political_laws:
                GameService().set_politics_law(country, request_data['name_law'])
            else:
                GameService().set_conscript_law(country, request_data['name_law'])
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HttpResponse({}, status=status.HTTP_200_OK)


@api_view(['PUT'])
def cancel_law(request, user_id):
    try:
        user = User.objects(id=user_id).first()
        request_data = JSONParser().parse(request)
        if SystemService.verify_token(user_id,request_data['token']):
            country = Country.objects(id=user.country.id).first()
            GameService().cancel_politics_law(country, request_data['name_law'])
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HttpResponse({}, status=status.HTTP_200_OK)


@api_view(['POST'])
def buy_goods(request, user_id):
    try:
        user = User.objects(id=user_id).first()
        request_data = JSONParser().parse(request)
        if SystemService.verify_token(user_id,request_data['token']):
            country = Country.objects(id=user.country.id).first()
            GameService().buy_goods(country, request_data['name_goods'], int(request_data['number']))
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HttpResponse({}, status=status.HTTP_200_OK)


@api_view(['POST'])
def sell_goods(request, user_id):
    try:
        user = User.objects(id=user_id).first()
        request_data = JSONParser().parse(request)
        if SystemService.verify_token(user_id,request_data['token']):
            country = Country.objects(id=user.country.id).first()
            GameService().sell_goods(country, request_data['name_goods'], int(request_data['number']))
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HttpResponse({}, status=status.HTTP_200_OK)


@api_view(['PUT'])
def edit_army(request, user_id):
    try:
        user = User.objects(id=user_id).first()
        request_data = JSONParser().parse(request)
        if SystemService.verify_token(user_id,request_data['token']):
            country = Country.objects(id=user.country.id).first()
            GameService().edit_army(country, request_data['name_unit'], int(request_data['new_number']))
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HttpResponse({}, status=status.HTTP_200_OK)


@api_view(['POST'])
def calculate_war(request, user_id, defending_player_name):
    try:
        user_1, user_2 = User.objects(id=user_id).first(), User.objects(username=defending_player_name).first()
        request_data = JSONParser().parse(request)
        if SystemService.verify_token(user_id,request_data['token']):
            country_1, country_2 = Country.objects(id=user_1.country.id).first(), Country.objects(id=user_2.country.id).first()
            view_obj = GameService().calculate_war(country_1.name, country_2.name)
            if SystemService().get_user_settings(user_id)['attacks']:
                pass  # send email to attacked player
            return HttpResponse(json.dumps(view_obj, default=lambda x: x.__dict__), status=status.HTTP_200_OK)
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def set_settings(request, user_id):
    try:
        user = User.objects(id=user_id).first()
        request_data = JSONParser().parse(request)
        if SystemService.verify_token(user_id,request_data['token']):
            SystemService().set_user_settings(user, request_data['setting_list'])
    except Exception as error:
        return HttpResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HttpResponse({}, status=status.HTTP_200_OK)
