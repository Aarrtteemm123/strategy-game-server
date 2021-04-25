import random

import tokenlib as tokenlib
from django.utils import timezone

from polls.models import Country, User, GlobalSettings
from polls.services.system_service import EmailTemplate, SystemService, EmailEvent
from polls.exceptions import UnknownUserError
from serverDjango.settings import ADMIN_EMAIL, SECRET_KEY


class UserService:
    def login(self, username: str, password: str):
        user = User.objects(username=username,password=password).first()
        if user:
            token = tokenlib.make_token({"user_id": str(user.id), 'username':username, 'password':password, 'random_value':random.randint(0,1000000)}, secret=SECRET_KEY)
            user.isAuth = True
            user.token = token
            user.date_last_login = timezone.now()
            user.save()
            return token
        else:
            raise UnknownUserError(username)

    def logout(self, user_id: str):
        user = User.objects(id=user_id).first()
        if user:
            user.isAuth = False
            user.token = ''
            user.save()
            return True
        else:
            raise UnknownUserError(str(user_id))

    def register_new_user(self, username: str, password: str, email: str, country_name: str, link_country_flag: str):
        country = SystemService().create_default_country(country_name,link_country_flag)
        try:
            country.save()
        except Exception as error:
            print(error)
            return False
        user = User(username=username, password=password, email=email, country=country.pk)
        try:
            user.save()
        except Exception as error:
            print(error)
            country.delete()
            return False
        if GlobalSettings.objects().first().email_notification:
            SystemService().send_notification([email], EmailEvent.REGISTRATION, username, country_name, str(user.pk), link_country_flag)
        return True

    def delete_user_account(self, user_id: str, password: str):
        if User.objects(id=user_id).count() == 1 and User.objects(id=user_id).first().password == password:
            try:
                user = User.objects(id=user_id).first()
                user_email = user.email
                country_pk = user.country.id
                country = Country.objects(id=country_pk).first()
                country.delete()
                user.delete()
                if GlobalSettings.objects().first().email_notification:
                    SystemService().send_notification([user_email], EmailEvent.DELETE, user.username)
                return True
            except Exception as e:
                print(e)
                return False
        return False

    def change_user_data(self,user_id: str,new_password: str=None,
                         new_country_name: str=None,new_country_flag: str=None):
        user = User.objects(id=user_id).first()
        if user is not None:
            country = Country.objects(id=user.country.id).first()
            user.password = new_password if new_password is not None else user.password
            country.name = new_country_name if new_country_name is not None and Country.objects(name=new_country_name).count() == 0 else country.name
            country.link_img = new_country_flag if new_country_flag is not None else country.link_img
            country.save()
            user.country = country.to_dbref()
            user.save()
            if GlobalSettings.objects().first().email_notification:
                SystemService().send_notification([user.email], EmailEvent.CHANGE_DATA, user.username, country.name, country.link_img)
            return True
        return False
