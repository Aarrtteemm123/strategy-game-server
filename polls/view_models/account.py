class AccountView:
    def __init__(self,user_id=0,link_img='',name_country = '',total_profit_country = 0,
                 economic_place = 0,military_place = 0,username = '',password = '',
                 email = '',date_registration = '',days_in_game = 0):
        self.user_id = user_id
        self.link_img = link_img
        self.name_country = name_country
        self.total_profit_country = total_profit_country
        self.economic_place = economic_place
        self.military_place = military_place
        self.username = username
        self.password = password
        self.email = email
        self.date_registration = date_registration
        self.days_in_game = days_in_game
