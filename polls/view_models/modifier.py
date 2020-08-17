class ModifierView:
    def __init__(self, value=0, msg=''):
        self.value = str(value) + ' %'
        self.msg = msg
        self.color = 'green' if value > 0 else 'red'