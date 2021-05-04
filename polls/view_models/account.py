class AccountView:
    def __init__(self,user_id: str='0',link_img: str='',name_country: str='',total_profit_country: int = 0,
                 economic_place: int = 0,military_place: int = 0,username: str = '',
                 email: str = '',date_registration: str = '',days_in_game: int = 0):
        self.user_id = user_id
        self.link_img = link_img
        self.name_country = name_country
        self.total_profit_country = total_profit_country
        self.economic_place = economic_place
        self.military_place = military_place
        self.username = username
        self.email = email
        self.date_registration = date_registration
        self.days_in_game = days_in_game
