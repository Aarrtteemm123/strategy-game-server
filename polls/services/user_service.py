import random

import tokenlib as tokenlib
from django.utils import timezone

from polls.models import Country, User
from polls.services.system_service import EmailTemplate, SystemService
from polls.errors import UnknownUserError
from serverDjango.settings import ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD, SECRET_KEY


class UserService:
    def login(self, username, password):
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

    def logout(self, user_id):
        user = User.objects(id=user_id).first()
        if user:
            user.isAuth = False
            user.token = ''
            user.save()
            return True
        else:
            raise UnknownUserError(str(user_id))

    def register_new_user(self, username, password, email, country_name, link_country_flag):
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
        #html_msg = EmailTemplate().get_html_registration(username, password, country_name, str(user.pk),link_country_flag)
        #SystemService().send_email(ADMIN_EMAIL, email, ADMIN_EMAIL_PASSWORD, html_msg, EmailTemplate.REGISTRATION_TITLE)
        return True

    def delete_user_account(self, user_id,password):
        if User.objects(id=user_id).count() == 1 and User.objects(id=user_id).first().password == password:
            try:
                user = User.objects(id=user_id).first()
                user_email = user.email
                country_pk = user.country.id
                country = Country.objects(id=country_pk).first()
                country.delete()
                user.delete()
                #html_msg = EmailTemplate().get_html_delete_account(user.username)
                #SystemService().send_email(ADMIN_EMAIL, user_email, ADMIN_EMAIL_PASSWORD, html_msg,EmailTemplate.DELETE_TITLE)
                return True
            except Exception as e:
                print(e)
                return False
        return False

    def change_user_data(self,user_id,new_username=None,new_password=None,
                         new_country_name=None,new_country_flag=None):
        user = User.objects(id=user_id).first()
        if user is not None:
            country = Country.objects(id=user.country.id).first()
            user.username = new_username if new_username is not None and User.objects(username=new_username).count() == 0 else user.username
            user.password = new_password if new_password is not None else user.password
            country.name = new_country_name if new_country_name is not None and Country.objects(name=new_country_name).count() == 0 else country.name
            country.link_img = new_country_flag if new_country_flag is not None else country.link_img
            country.save()
            user.country = country.to_dbref()
            user.save()
            #html_msg = EmailTemplate().get_html_edit_account(user.username, user.password, country.name,country.link_img)
            #SystemService().send_email(ADMIN_EMAIL, user.email, ADMIN_EMAIL_PASSWORD, html_msg,EmailTemplate.CHANGE_TITLE)
            return True
        return False
