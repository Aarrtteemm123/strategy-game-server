from django.test import TestCase
from polls.services.user_service import UserService
from polls.services.game_service import GameService
from polls.services.system_service import SystemService

#print(UserService().register_new_user('pl1','pas1','er@gmail.com','Ukr','gfg/fgfgf'))
#print(UserService().register_new_user('pl2','pas2','er2@gmail.com','Rus','gfg/fgfgf'))
#print(UserService().register_new_user('pl3','pas3','er3@gmail.com','Ger','gfg/fgfgf'))
#print(UserService().register_new_user('pl4','pas4','er4@gmail.com','Mol','gfg/fgfgf'))
from polls.services.view_service import CountryViewService
#GameService().calculate_war('Ukr','Mol')
CountryViewService().get_budget('5f3407a1de26def0dc5b5184')
class ServiceTestCase(TestCase):
    def setUp(self):
        pass

    def test(self):
        pass
