from typing import List, Dict


class PlayerView:
    def __init__(self,link_country_flag: str,name_country: str,username: str,economic_place: int,
                 military_place: int,money: int,population: int,farms: int,mines: int,factories: int,solders: int,army_units_dict: Dict[str,int]):
        self.link_country_flag = link_country_flag
        self.name_country = name_country
        self.username = username
        self.economic_place = economic_place
        self.military_place = military_place
        self.money = money
        self.population = population
        self.farms = farms
        self.mines = mines
        self.factories = factories
        self.solders = solders
        self.army_units_dict = army_units_dict

class TopPlayersPage:
    def __init__(self,economic_place: int,military_place: int,top_players: List[PlayerView]):
        self.economic_place = economic_place
        self.military_place = military_place
        self.top_players = top_players