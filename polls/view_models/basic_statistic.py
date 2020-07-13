import json


class ChartBudgetData:
    def __init__(self, profit_data=None, expenses_data=None, x_axis_label=None, y_axis_max = 0):
        if x_axis_label is None:
            x_axis_label = []
        if expenses_data is None:
            expenses_data = []
        if profit_data is None:
            profit_data = []
        self.profit_data = profit_data
        self.expenses_data = expenses_data
        self.x_axis_label = x_axis_label
        self.y_axis_max = y_axis_max


class ChartPopulationData:
    def __init__(self, data=None, x_axis_label=None):
        if x_axis_label is None:
            x_axis_label = []
        if data is None:
            data = []
        self.data = data
        self.x_axis_label = x_axis_label


class ChartProfitData:
    def __init__(self,data=None,x_axis_label=None,y_max=0,y_min=0,tick_amount=10):
        if x_axis_label is None:
            x_axis_label = []
        if data is None:
            data = []
        self.data = data
        self.x_axis_label = x_axis_label
        self.y_max = y_max
        self.y_min = y_min
        self.tick_amount = tick_amount


class ChartGoodsData:
    def __init__(self, data=None, x_axis_label=None):
        if x_axis_label is None:
            x_axis_label = []
        if data is None:
            data = []
        self.data = data
        self.x_axis_label = x_axis_label

class TableRowDataView:
    def __init__(self,id=0,link_img='',name_goods='',number=0,world_place=0):
        self.id = id
        self.link_img = link_img
        self.name_goods = name_goods
        self.number = number
        self.world_place = world_place


class BasicStatisticView:
    def __init__(self, link_img = '', name_country = '', population = 0, budget = 0,
                 total_profit_country = 0, economic_place = 0, military_place = 0,
                 victories_battles = 0, losses_battles = 0, chart_budget = ChartBudgetData(),
                 chart_population = ChartPopulationData(), chart_profit = ChartProfitData(),
                 farms_goods_chart = ChartGoodsData(), mines_goods_chart = ChartGoodsData(),
                 industrial_goods_chart = ChartGoodsData(), military_goods_chart = ChartGoodsData(),
                 farm_goods_table=None, mine_goods_table=None, industrial_goods_table=None,
                 military_goods_table=None):
        if military_goods_table is None:
            military_goods_table = [TableRowDataView()]
        if industrial_goods_table is None:
            industrial_goods_table = [TableRowDataView()]
        if mine_goods_table is None:
            mine_goods_table = [TableRowDataView()]
        if farm_goods_table is None:
            farm_goods_table = [TableRowDataView()]
        self.link_img = link_img
        self.name_country = name_country
        self.population = population
        self.budget = budget
        self.total_profit_country = total_profit_country
        self.economic_place = economic_place
        self.military_place = military_place
        self.victories_battles = victories_battles
        self.losses_battles = losses_battles
        self.chart_budget = chart_budget
        self.chart_population = chart_population
        self.chart_profit = chart_profit
        self.farms_goods_chart = farms_goods_chart
        self.mines_goods_chart = mines_goods_chart
        self.industrial_goods_chart = industrial_goods_chart
        self.military_goods_chart = military_goods_chart
        self.farm_goods_table = farm_goods_table
        self.mine_goods_table = mine_goods_table
        self.industrial_goods_table = industrial_goods_table
        self.military_goods_table = military_goods_table

bs = BasicStatisticView()
print(json.dumps(bs.__dict__,default=lambda x: x.__dict__))
