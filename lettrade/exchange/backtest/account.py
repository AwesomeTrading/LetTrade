from lettrade.account import Account


class BackTestAccount(Account):
    def __repr__(self):
        return "<BackTestAccount " + str(self) + ">"


class ForexBackTestAccount(Account):
    def __repr__(self):
        return "<ForexBackTestAccount " + str(self) + ">"

    def pl(self, size, entry_price: float, exit_price=None) -> float:
        return (
            super().pl(
                size=size,
                entry_price=entry_price,
                exit_price=exit_price,
            )
            * 1_000_000
        )
