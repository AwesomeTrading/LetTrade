from lettrade.account import Account


class BackTestAccount(Account):
    def __repr__(self):
        return "<BackTestAccount " + str(self) + ">"


class ForexBackTestAccount(Account):
    def __repr__(self):
        return "<ForexBackTestAccount " + str(self) + ">"
