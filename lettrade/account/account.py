from abc import ABCMeta


class Account(metaclass=ABCMeta):
    _exchange: "Exchange"

    def __init__(
        self,
        *,
        risk=0.02,
        cash=10_000,
        commission=0.0,
        margin=None,
        leverage=1.0,
    ) -> None:
        self._risk: risk
        self._cash: float = cash
        self._commission: float = commission
        self._margin = margin
        self._leverage: float = leverage

        self._equities: dict[str, object] = dict()

    def init(self, exchange: "Exchange"):
        self._exchange = exchange

    def __repr__(self):
        return "<Account " + str(self) + ">"

    def risk(self, size=None):
        return self._risk

    @property
    def equity(self) -> float:
        equity = self._cash
        if len(self._exchange.trades) > 0:
            equity += sum(trade.pl for trade in self._exchange.trades.values())
        return equity

    def snapshot_equity(self):
        if len(self._exchange.trades) > 0:
            bar = self._exchange.data.bar()
            self._equities[bar[0]] = {"at": bar[1], "equity": self.equity}
