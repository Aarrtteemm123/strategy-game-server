import datetime
import json
import time
from django.test import TestCase
from sendgrid import SendGridAPIClient, Mail
from sendgrid import SendGridAPIClient, Mail

from polls.exceptions import UnknownNameTaxError
from polls.models import News, Country, User, ArmyUnit, Cache
from polls.services.user_service import UserService
from polls.services.game_service import GameService
from polls.services.system_service import SystemService, EmailTemplate

#print(UserService().register_new_user('pl1','pas1','er@gmail.com','Ukraine','https://i.pinimg.com/originals/c2/b2/75/c2b2757203f9b9e1b86986aad502d2d5.jpg'))
#print(UserService().register_new_user('pl2','pas2','er2@gmail.com','Great Britain','https://images-na.ssl-images-amazon.com/images/I/71d6ai1UMEL._AC_SL1500_.jpg'))
#print(UserService().register_new_user('pl3','pas3','er3@gmail.com','Germany','https://image.winudf.com/v2/image1/Y29tLmZsYWd3YWxscGFwZXIuZ2VybWFueV9zY3JlZW5fNF8xNTQ3NDgyNTMyXzA1OA/screen-5.jpg?fakeurl=1&type=.jpg'))
#print(UserService().register_new_user('pl4','pas4','er4@gmail.com','Moldova','https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Flag_of_Moldova.svg/1280px-Flag_of_Moldova.svg.png'))
from polls.services.view_service import CountryViewService, NewsViewService, PlayerViewService

#country = Country.objects(name='Ukraine').first()
#user = User.objects(username='pl1').first()
#print(user.token,user.date_last_login)
#UserService().logout(user.id)
#user = User.objects(username='pl1').first()
#print(user.token,user.date_last_login)
#GameService().build_industry(country.name,'Fertilizer factory')
#GameService().buy_goods(country.name,'Salt',100)
#GameService().buy_goods(country.name,'Minerals',100)
#SystemService().update_system()
#GameService().update_population(country)
#print(make_password('pas0'))
#print(UserService().delete_user_account('5fe0d7a9c17049903ac3b6f3','pas12'))
#SystemService().create_default_global_settings()
#SystemService().update_top_players_cache()
#SystemService().update_trade_cache()

class ServiceTestCase(TestCase):
    def setUp(self):
        pass

    def test(self):
        pass
