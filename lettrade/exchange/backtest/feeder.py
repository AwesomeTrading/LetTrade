from lettrade.data import DataFeeder


class BackTestDataFeeder(DataFeeder):
    def alive(self):
        return self.data.alive()

    def next(self):
        return self.data.next()
