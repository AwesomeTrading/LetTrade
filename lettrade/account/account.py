from abc import ABC, abstractmethod
from typing import Optional


class Account(ABC):
    """
    Manage account balance, leverage, commission. Risk calculate and control
    """

    _risk: float
    _cash: float
    _commission: float
    _margin: float
    _leverage: float
    _equities: dict[str, float]

    _exchange: "Exchange"
    _do_snapshot_equity: bool

    def __init__(
        self,
        risk: float = 0.02,
        cash: float = 10_000,
        commission: float = 0.2,
        margin: float = 1.0,
        leverage: float = 1.0,
        **kwargs,
    ) -> None:
        """_summary_

        Args:
            risk (Optional[float], optional): _description_. Defaults to 0.02.
            cash (Optional[float], optional): _description_. Defaults to 10_000.
            commission (Optional[float], optional): _description_. Defaults to 0.2.
            margin (Optional[float], optional): _description_. Defaults to None.
            leverage (Optional[float], optional): _description_. Defaults to 1.0.
        """
        self._risk = risk
        self._cash = cash
        self._commission = commission
        self._margin = margin
        self._leverage = leverage

        self._equities = dict()
        self._do_snapshot_equity = True  # Snapshot balance

    def __repr__(self):
        return "<Account " + str(self) + ">"

    def init(self, exchange: "Exchange"):
        self._exchange = exchange

    def start(self):
        pass

    def stop(self):
        pass

    def risk(self, side: "OrderSide", size: float, **kwargs) -> float:
        """
        Risk calculation
        """
        if size is None:
            return side * abs(self._risk)
        return side * abs(size)

    def pl(self, size, entry_price: float, exit_price=None):
        """Estimate temporary profit and loss"""
        if exit_price is None:
            exit_price = self._exchange.data.l.open[0]

        return size * (exit_price - entry_price)

    @property
    def equity(self) -> float:
        equity = self._cash
        if len(self._exchange.trades) > 0:
            equity += sum(trade.pl for trade in self._exchange.trades.values())
        return equity

    def _snapshot_equity(self):
        if self._do_snapshot_equity or len(self._exchange.trades) > 0:
            bar = self._exchange.data.bar()
            self._equities[bar] = self.equity

            self._do_snapshot_equity = False

    def _on_trade_exit(self, trade: "Trade"):
        self._cash += trade.pl - trade.fee

        self._do_snapshot_equity = True
