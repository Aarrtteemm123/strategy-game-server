class UnknownNameTaxError(Exception):
    def __init__(self,name,msg='Tax with name {} not exist, choose one of these: population_taxes, farms_taxes, mines_taxes, factories_taxes, military_taxes'):
        super().__init__(msg.format(name))

class UnknownNameLawError(Exception):
    def __init__(self,name,msg='Law with name {} not exist, choose one of these: Free medicine, Isolation, Free housing, Free education'):
        super().__init__(msg.format(name))

class UnknownNameConscriptLawError(Exception):
    def __init__(self,name,msg='Conscript law with name {} not exist, choose one of these: Conscript law: Elite, Conscript law: Volunteer, Conscript law: Limited Conscription, Conscript law: Extensive Conscription, Conscript law: Service by Requirement, Conscript law: All Adults Serve, Conscript law: All with weapons'):
        super().__init__(msg.format(name))

class UnknownNameTechnologyError(Exception):
    def __init__(self,name,msg='Technology with name {} not exist, choose one of these: Medicine technology, Computers technology, Upgrade weapons, Upgrade defence system'):
        super().__init__(msg.format(name))

class UnknownTypeBuildingError(Exception):
    def __init__(self,name,msg='Type building with name {} not exist, choose one of these: farm, mine, well, factory'):
        super().__init__(msg.format(name))

class UnknownNameUnitError(Exception):
    def __init__(self,name,msg='Unit with name {} not exist, choose one of these: Infantry, Artillery, PTO, PVO, Tank, Aviation'):
        super().__init__(msg.format(name))

class TaxValueNotInRangeError(Exception):
    def __init__(self,msg='Taxes value must be between 0 and 100'):
        super().__init__(msg)

class LowBudgetError(Exception):
    def __init__(self,msg='Not enough money'):
        super().__init__(msg)

class FreePeopleError(Exception):
    def __init__(self,msg='Not enough free people'):
        super().__init__(msg)

class MilitaryManpowerError(Exception):
    def __init__(self,msg='Not enough military manpower'):
        super().__init__(msg)

class UnitError(Exception):
    def __init__(self,msg='Check goods and new number of units'):
        super().__init__(msg)

class MaxLevelError(Exception):
    def __init__(self,max_level,msg='There is already a max level - {}'):
        super().__init__(msg.format(max_level))

class GoodsValueNotInRangeError(Exception):
    def __init__(self,max_value,min_value=0,msg='Number of goods must be in range ({},{})'):
        super().__init__(msg.format(min_value,max_value))