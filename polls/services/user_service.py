from polls.models import Country, Budget, Population, Army, User
from polls.services.system_service import EmailTemplate, SystemService
from serverDjango.settings import ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD


class UserService:
    def login(self, username, password):
        return User.objects(username=username, password=password).only('isAuth').update_one(isAuth=True) == 1

    def logout(self, username):
        return User.objects(username=username).only('isAuth').update_one(isAuth=False) == 1

    def register_new_user(self, username, password, email, country_name, link_country_flag):
        country = Country(link_img=link_country_flag, name=country_name, budget=Budget(), population=Population(),
                          army=Army())
        user = User(username=username, password=password, email=email, country=country)
        try:
            country.save()
        except:
            return False
        try:
            user.save()
        except:
            country.delete()
            return False
        html_msg = EmailTemplate().get_html_registration(username,password,country_name,str(user.pk),link_country_flag)
        SystemService().send_email(ADMIN_EMAIL,email,ADMIN_EMAIL_PASSWORD,html_msg,EmailTemplate.REGISTRATION_TITLE)
        return True

    def delete_user_account(self, username):
        if User.objects(username=username).count() == 1:
            try:
                obj = User.objects(username=username).only('email','country').first()
                user_email = obj.email
                country_pk = obj.country.pk
                Country.objects(pk=country_pk).delete()
                html_msg = EmailTemplate().get_html_delete_account(username)
                SystemService().send_email(ADMIN_EMAIL, user_email, ADMIN_EMAIL_PASSWORD, html_msg,EmailTemplate.DELETE_TITLE)
                return True
            except:
                return False
        return False

    def change_username(self, username, new_username):
        if User.objects(username=new_username).count() == 0:
            if User.objects(username=username).only('username').update_one(username=new_username) == 1:
                obj = User.objects(username=new_username).only('password','country','email').first()
                country = Country.objects(pk=obj.country.pk).first()
                html_msg = EmailTemplate().get_html_edit_account(new_username,obj.password,country.name,country.link_img)
                SystemService().send_email(ADMIN_EMAIL, obj.email, ADMIN_EMAIL_PASSWORD, html_msg,EmailTemplate.CHANGE_TITLE)
                return True
        return False

    def change_password(self, username, new_password):
        if User.objects(username=username).only('password').update_one(password=new_password) == 1:
            obj = User.objects(username=username).only('country', 'email').first()
            country = Country.objects(pk=obj.country.pk).first()
            html_msg = EmailTemplate().get_html_edit_account(username, new_password, country.name, country.link_img)
            SystemService().send_email(ADMIN_EMAIL, obj.email, ADMIN_EMAIL_PASSWORD, html_msg,
                                       EmailTemplate.CHANGE_TITLE)
            return True
        return False

    def change_country_name(self, country_name, new_country_name):
        if Country.objects(name=country_name).only('name').update_one(name=new_country_name) == 1:
            country = Country.objects(name=new_country_name).only('link_img').first()
            obj = User.objects(country=country.pk).only('username', 'password','email').first()
            html_msg = EmailTemplate().get_html_edit_account(obj.username, obj.password, new_country_name, country.link_img)
            SystemService().send_email(ADMIN_EMAIL, obj.email, ADMIN_EMAIL_PASSWORD, html_msg,
                                       EmailTemplate.CHANGE_TITLE)
            return True
        return False

    def change_country_flag(self, country_name, new_country_flag):
        if Country.objects(name=country_name).only('link_img').update_one(link_img=new_country_flag) == 1:
            country = Country.objects(name=country_name).only('link_img').first()
            obj = User.objects(country=country.pk).only('username', 'password', 'email').first()
            html_msg = EmailTemplate().get_html_edit_account(obj.username, obj.password, country_name,
                                                             country.link_img)
            SystemService().send_email(ADMIN_EMAIL, obj.email, ADMIN_EMAIL_PASSWORD, html_msg,
                                       EmailTemplate.CHANGE_TITLE)
            return True
        return False
