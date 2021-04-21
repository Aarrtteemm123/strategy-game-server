from django.test import TestCase

from polls.exceptions import UnknownNameTaxError, TaxValueNotInRangeError, LowBudgetError
from polls.models import User, Country
from polls.services.game_service import GameService
from polls.services.user_service import UserService


class GameServiceTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        UserService().register_new_user('Test user', '1234', 'test@gmail.com', 'country name', '')

    def setUp(self):
        self.country = Country.objects(name='country name').first()
        self.country.budget.money = 100000
        self.country.save()

    def test_incorrect_name_tax(self):
        with self.assertRaises(UnknownNameTaxError):
            GameService().set_taxes(self.country, 'blablablabla', 20)

    def test_incorrect_tax_value(self):
        with self.assertRaises(TaxValueNotInRangeError):
            GameService().set_taxes(self.country, 'population_taxes', -20)

    def test_change_population_taxes(self):
        GameService().set_taxes(self.country, 'population_taxes', 20)
        self.country.reload()
        result = next(filter(lambda x: x.address_from == 'population taxes', self.country.population.modifiers), None)
        self.assertIsNotNone(result)
        self.assertEqual(self.country.budget.population_taxes, 20)

    def test_change_farms_taxes(self):
        GameService().set_taxes(self.country, 'farms_taxes', 80)
        self.country.reload()
        result = next(filter(lambda x: x.address_from == 'farms taxes', self.country.industry_modifiers), None)
        self.assertIsNotNone(result)
        self.assertEqual(self.country.budget.farms_taxes, 80)

    def test_change_mines_taxes(self):
        GameService().set_taxes(self.country, 'mines_taxes', 10)
        self.country.reload()
        result = next(filter(lambda x: x.address_from == 'mines taxes', self.country.industry_modifiers), None)
        self.assertIsNotNone(result)
        self.assertEqual(self.country.budget.mines_taxes, 10)

    def test_change_factories_taxes(self):
        GameService().set_taxes(self.country, 'factories_taxes', 90)
        self.country.reload()
        result = next(filter(lambda x: x.address_from == 'factories taxes', self.country.industry_modifiers), None)
        self.assertIsNotNone(result)
        self.assertEqual(self.country.budget.factories_taxes, 90)

    def test_upgrade_medicine_technology(self):
        money_before = self.country.budget.money
        GameService().upgrade_technology(self.country, 'Medicine technology')
        self.country.reload()
        res = next(filter(lambda t: t.name == 'Medicine technology', self.country.technologies), None)
        self.assertIsNotNone(res)
        self.assertEqual(res.level, 1)
        self.assertEqual(money_before, self.country.budget.money + (res.price_upgrade / res.increase_price))

    def test_upgrade_weapons_technology(self):
        money_before = self.country.budget.money
        GameService().upgrade_technology(self.country, 'Upgrade weapons')
        self.country.reload()
        res = next(filter(lambda t: t.name == 'Upgrade weapons', self.country.technologies), None)
        self.assertIsNotNone(res)
        self.assertEqual(res.level, 1)
        self.assertEqual(money_before, self.country.budget.money + (res.price_upgrade / res.increase_price))

    def test_upgrade_defence_technology(self):
        money_before = self.country.budget.money
        GameService().upgrade_technology(self.country, 'Upgrade defence system')
        self.country.reload()
        res = next(filter(lambda t: t.name == 'Upgrade defence system', self.country.technologies), None)
        self.assertIsNotNone(res)
        self.assertEqual(res.level, 1)
        self.assertEqual(money_before, self.country.budget.money + (res.price_upgrade / res.increase_price))

    def test_upgrade_computers_technology(self):
        money_before = self.country.budget.money
        GameService().upgrade_technology(self.country, 'Computers technology')
        self.country.reload()
        res = next(filter(lambda t: t.name == 'Computers technology', self.country.technologies), None)
        self.assertIsNotNone(res)
        self.assertEqual(res.level, 1)
        self.assertEqual(money_before, self.country.budget.money + (res.price_upgrade / res.increase_price))

    def test_build_farm(self):
        money_before = self.country.budget.money
        farmers_before = self.country.population.farmers
        GameService().build_industry(self.country, 'Seed farm')
        self.country.reload()
        res = next(filter(lambda t: t.name == 'Seed farm', self.country.farms), None)
        self.assertIsNotNone(res)
        self.assertEqual(res.number, 1)
        self.assertEqual(money_before, self.country.budget.money + res.price_build)
        self.assertEqual(farmers_before + res.workers, self.country.population.farmers)

    def test_build_mine(self):
        money_before = self.country.budget.money
        miners_before = self.country.population.miners
        GameService().build_industry(self.country, 'Iron mine')
        self.country.reload()
        res = next(filter(lambda t: t.name == 'Iron mine', self.country.mines), None)
        self.assertIsNotNone(res)
        self.assertEqual(res.number, 1)
        self.assertEqual(money_before, self.country.budget.money + res.price_build)
        self.assertEqual(miners_before + res.workers, self.country.population.miners)

    def test_build_factory(self):
        money_before = self.country.budget.money
        factory_workers_before = self.country.population.farmers
        GameService().build_industry(self.country, 'Bakery factory')
        self.country.reload()
        res = next(filter(lambda t: t.name == 'Bakery factory', self.country.factories), None)
        self.assertIsNotNone(res)
        self.assertEqual(res.number, 1)
        self.assertEqual(money_before, self.country.budget.money + res.price_build)
        self.assertEqual(factory_workers_before + res.workers, self.country.population.factory_workers)

    def test_remove_farm(self):
        farmers_before = self.country.population.farmers
        GameService().remove_industry(self.country, 'Seed farm')
        self.country.reload()
        res = next(filter(lambda t: t.name == 'Seed farm', self.country.farms), None)
        self.assertIsNotNone(res)
        self.assertEqual(res.number, 0)
        self.assertEqual(farmers_before - res.workers, self.country.population.farmers)

    def test_remove_mine(self):
        miners_before = self.country.population.miners
        GameService().remove_industry(self.country, 'Iron mine')
        self.country.reload()
        res = next(filter(lambda t: t.name == 'Iron mine', self.country.mines), None)
        self.assertIsNotNone(res)
        self.assertEqual(res.number, 0)
        self.assertEqual(miners_before - res.workers, self.country.population.miners)

    def test_remove_factory(self):
        factory_workers_before = self.country.population.factory_workers
        GameService().remove_industry(self.country, 'Bakery factory')
        self.country.reload()
        res = next(filter(lambda t: t.name == 'Bakery factory', self.country.factories), None)
        self.assertIsNotNone(res)
        self.assertEqual(res.number, 0)
        self.assertEqual(factory_workers_before - res.workers, self.country.population.factory_workers)

    def test_get_number_soldiers_from_units(self):
        solders = GameService().get_number_soldiers_from_units(self.country)
        self.assertEqual(solders, 100)

    def test_upgrade_warehouse(self):
        money_before = self.country.budget.money
        GameService().upgrade_warehouse(self.country, 'Seed')
        self.country.reload()
        res = next(filter(lambda t: t.goods.name == 'Seed', self.country.warehouses), None)
        self.assertIsNotNone(res)
        self.assertEqual(res.level, 1)
        self.assertEqual(money_before - (res.price_upgrade / res.increase_price), self.country.budget.money)

    def test_set_politics_law(self):
        self.assertFalse('Free medicine' in self.country.adopted_laws)
        GameService().set_politics_law(self.country, 'Free medicine')
        self.assertTrue('Free medicine' in self.country.adopted_laws)

    def test_set_conscript_law(self):
        self.assertFalse('Conscript law: Elite' in self.country.adopted_laws)
        GameService().set_conscript_law(self.country, 'Conscript law: Elite')
        self.assertTrue('Conscript law: Elite' in self.country.adopted_laws)

    def test_cancel_politics_law(self):
        GameService().set_politics_law(self.country, 'Free medicine')
        self.assertTrue('Free medicine' in self.country.adopted_laws)
        GameService().cancel_politics_law(self.country, 'Free medicine')
        self.assertFalse('Free medicine' in self.country.adopted_laws)

    def test_low_budget(self):
        self.country.budget.money = 0
        with self.assertRaises(LowBudgetError):
            GameService().set_politics_law(self.country, 'Free medicine')

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        user = User.objects(username='Test user').first()
        UserService().delete_user_account(user.id, user.password)
