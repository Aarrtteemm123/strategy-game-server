class ChartPriceGoods:
    def __init__(self, name_value = '', data=None, x_axis_label=None, title_text ='',
                 y_max = 0, y_min = 0):
        if x_axis_label is None:
            x_axis_label = []
        if data is None:
            data = []
        self.name_value = name_value
        self.data = data
        self.x_axis_label = x_axis_label
        self.title_text = title_text
        self.y_max = y_max
        self.y_min = y_min

class TableRowProducerView:
    def __init__(self,link_img='',name_country='',number=0,world_place=0):
        self.world_place = world_place
        self.link_img = link_img
        self.name_country = name_country
        self.number = number

class TradeCardView:
    def __init__(self,name = '',link_img = '',price_sell = 0,price_buy = 0,warehouse_has = 0,
                 min_price = 0,data_top_producer=None,chart_price_goods = ChartPriceGoods()):
        if data_top_producer is None:
            data_top_producer = [TableRowProducerView()]
        self.name = name
        self.link_img = link_img
        self.price_sell = price_sell
        self.price_buy = price_buy
        self.min_price = min_price
        self.warehouse_has = warehouse_has
        self.data_top_producer = data_top_producer
        self.chart_price_goods = chart_price_goods