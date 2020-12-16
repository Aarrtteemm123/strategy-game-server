import time

from django.test import TestCase

from polls.models import News, Country
from polls.services.user_service import UserService
from polls.services.game_service import GameService
from polls.services.system_service import SystemService

#print(UserService().register_new_user('pl1','pas1','er@gmail.com','Ukraine','gfg/fgfgf'))
#print(UserService().register_new_user('pl2','pas2','er2@gmail.com','Rus','gfg/fgfgf'))
#print(UserService().register_new_user('pl3','pas3','er3@gmail.com','Ger','gfg/fgfgf'))
#print(UserService().register_new_user('pl4','pas4','er4@gmail.com','Mol','gfg/fgfgf'))
from polls.services.view_service import CountryViewService, NewsViewService

#GameService().calculate_war('Ukraine','Mol')
#CountryViewService().get_army('5f3d511cdd22f0b5a1862f9f')


GameService().update_population(Country.objects(name='Ukraine').first())


class ServiceTestCase(TestCase):
    def setUp(self):
        pass

    def test(self):
        pass
