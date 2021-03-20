from datetime import datetime
import time
from polls.models import GlobalSettings, User, Country, News
from polls.services.game_service import GameService
from polls.services.system_service import SystemService, EmailEvent

def run_updating_price_goods():
    print('run_updating_price_goods')
    while True:
        GameService().update_price_goods()
        time.sleep(3600)

def run_updating_politics_cache():
    print('run_updating_politics_cache')
    global_settings = GlobalSettings()
    while True:
        SystemService().update_politics_cache()
        time.sleep(global_settings.frequency_update_politics_cache * 60)


def run_updating_cache_trade():
    print('run_updating_cache_trade')
    system_service = SystemService()
    global_settings = GlobalSettings()
    while True:
        try:
            system_service.update_trade_cache()
            time.sleep(global_settings.frequency_update_trade * 60)
        except Exception as e:
            print(e)


def run_updating_top_players():
    print('run_updating_top_players')
    system_service = SystemService()
    global_settings = GlobalSettings()
    while True:
        try:
            system_service.update_top_players_cache(global_settings.number_top_players)
            time.sleep(global_settings.frequency_update_top_players * 60)
        except Exception as e:
            print(e)


def run_updating_players():
    print('run_updating_players')
    system_service = SystemService()
    while True:
        try:
            system_service.update_players()
        except Exception as e:
            print(e)


def run_check_warehouses():
    print('run_check_warehouses')
    global_settings = GlobalSettings.objects().first()
    if global_settings.email_notification:
        while True:
            try:
                users = User.objects()
                for user in users:
                    if user.settings['warehouse overflow or empty']:
                        country = Country.objects(id=user.country).first()
                        for warehouse in country.warehouses:
                            if warehouse.filling_speed != 0 and (datetime.utcnow() - country.date_last_warehouse_notification).total_seconds()/60 >= global_settings.frequency_email_notification and (warehouse.goods.value <= 0 or warehouse.goods.value >= warehouse.capacity):
                                SystemService().send_notification([user.email],EmailEvent.WAREHOUSE)
                                break
                time.sleep(global_settings.frequency_check_warehouses * 60)
            except Exception as e:
                print(e)

def run_check_news():
    print('run_check_news')
    global_settings = GlobalSettings.objects().first()
    number_of_news = len(News.objects())
    if global_settings.email_notification:
        while True:
            try:
                news_len_lst = len(News.objects())

                if news_len_lst < number_of_news:
                    number_of_news = news_len_lst

                if news_len_lst > number_of_news:
                    number_of_news = news_len_lst
                    users = User.objects()
                    to_emails_lst = []
                    for user in users:
                        if user.settings['news']:
                           to_emails_lst.append(user.email)
                    SystemService().send_notification(to_emails_lst, EmailEvent.NEWS)

                time.sleep(global_settings.frequency_check_news * 60)
            except Exception as e:
                print(e)

def clear_country_attack_history():
    print('clear_country_attack_history')
    global_settings = GlobalSettings.objects().first()
    while True:
        for country in Country.objects():
            active_history_lst = []
            for history in country.army.history_attacks:
                if (datetime.utcnow() - history.time).total_seconds()/60 < global_settings.pause_between_war:
                    active_history_lst.append(history)
            country.army.history_attacks = active_history_lst
            country.save()
        time.sleep(3600 * 24)
