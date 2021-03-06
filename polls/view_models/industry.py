class TableRowGoodsView:
    def __init__(self,link_img='',name_goods='',number=0):
        self.link_img = link_img
        self.name_goods = name_goods
        self.number = number

class IndustrialCardView:
    def __init__(self, name = '', link_img = '', production_speed = 0,
                 total_production_speed = 0,price_build = 0,
                 workers=0, number = 0, active_number = 0, total_workers = 0, need_goods=None):
        if need_goods is None:
            need_goods = [TableRowGoodsView()]
        self.name = name
        self.link_img = link_img
        self.production_speed = production_speed
        self.total_production_speed = total_production_speed
        self.price_build = price_build
        self.workers = workers
        self.number = number
        self.active_number = active_number
        self.total_workers = total_workers
        self.need_goods = need_goods