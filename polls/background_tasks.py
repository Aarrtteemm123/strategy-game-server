from datetime import datetime
import time
from polls.models import GlobalSettings, User, Country, News
from polls.services.system_service import SystemService, EmailEvent


def run_updating_trade():
    print('run_updating_trade')
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
                            if warehouse.filling_speed != 0 and (datetime.utcnow() - country.date_last_warehouse_notification).seconds/60 >= global_settings.frequency_email_notification and (warehouse.goods.value <= 0 or warehouse.goods.value >= warehouse.capacity):
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