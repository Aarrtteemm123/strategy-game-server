from polls.models import Country, Budget, Population, Army, User


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
        # send notification email
        return True

    def delete_user_account(self, username):
        try:
            country_pk = User.objects(username=username).only('country').first().country.pk
            Country.objects(pk=country_pk).delete()
            # send notification email
            return True
        except:
            return False

    def change_username(self, username, new_username):
        if User.objects(username=new_username).count() == 0:
            if User.objects(username=username).only('username').update_one(username=new_username) == 1:
                # send notification email
                return True
        return False

    def change_password(self, username, new_password):
        if User.objects(username=username).only('password').update_one(password=new_password) == 1:
            # send notification email
            return True
        return False

    def change_country_name(self, country_name, new_country_name):
        if Country.objects(name=country_name).only('name').update_one(name=new_country_name) == 1:
            # send notification email
            return True
        return False

    def change_country_flag(self, country_name, new_country_flag):
        if Country.objects(name=country_name).only('link_img').update_one(link_img=new_country_flag) == 1:
            # send notification email
            return True
        return False
