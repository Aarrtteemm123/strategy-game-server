import time
from polls.models import GlobalSettings
from polls.services.system_service import SystemService

def run_updating_trade():
    print('run_updating_trade')
    system_service = SystemService()
    global_settings = GlobalSettings()
    while True:
        system_service.update_trade_cache()
        time.sleep(global_settings.frequency_update_trade*60)

def run_updating_top_players():
    print('run_updating_top_players')
    system_service = SystemService()
    global_settings = GlobalSettings()
    while True:
        system_service.update_top_players_cache(global_settings.number_top_players)
        time.sleep(global_settings.frequency_update_top_players*60)

def run_updating_players():
    print('run_updating_players')
    system_service = SystemService()
    while True:
        system_service.update_players()