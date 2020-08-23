class NewsView:
    def __init__(self, title='', date = '', rows=None):
        if rows is None:
            rows = []
        self.title = title
        self.date = date
        self.rows = rows

