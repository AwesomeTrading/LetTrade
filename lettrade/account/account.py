from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

from .error import LetAccountInsufficientException

if TYPE_CHECKING:
    from lettrade.exchange import Exchange, Position, TradeSide


class AccountType(str, Enum):
    """"""

    Hedging = "hedging"
    """"""
    Speculation = "speculation"
    """"""


class Account(metaclass=ABCMeta):
    """Manage account balance, leverage, commission. Risk calculate and control"""

    _exchange: "Exchange"
    _config: dict
    _type: str

    _risk: float
    _balance: float
    _margin: float
    _leverage: float
    _equities: dict[str, float]

    _do_equity_snapshot: bool

    def __init__(
        self,
        risk: float = 0.02,
        balance: float = 10_000,
        margin: float = 1.0,
        leverage: float = 1.0,
        type: AccountType = AccountType.Hedging,
        **kwargs,
    ) -> None:
        """_summary_

        Args:
            risk (float, optional): _description_. Defaults to 0.02.
            balance (float, optional): _description_. Defaults to 10_000.
            margin (float, optional): _description_. Defaults to 1.0.
            leverage (float, optional): _description_. Defaults to 1.0.
            **kwargs (dict, optional): Config of account. Defaults to {}.
        """
        self._risk = risk
        self._balance = balance
        self._margin = margin
        self._leverage = leverage
        self._type = type
        self._config = kwargs

        self._equities = dict()

        self._do_equity_snapshot = True  # Snapshot balance

    def init(self, exchange: "Exchange"):
        self._exchange = exchange

    def __repr__(self):
        return "<Account " + str(self) + ">"

    def start(self):
        """Start account"""

    def next(self):
        """Next account"""

    def next_next(self):
        """Call after strategy.next()"""
        self._equity_snapshot()

    def stop(self):
        """Stop account"""
        try:
            self._equity_snapshot()
        except LetAccountInsufficientException:
            pass

    def risk(self, side: "TradeSide", size: float, **kwargs) -> float:
        """Risk calculation"""
        if size is None:
            return side * abs(self._risk)
        return side * abs(size)

    def pl(self, size, entry_price: float, exit_price=None) -> float:
        """Estimate temporary profit and loss"""
        if exit_price is None:
            exit_price = self._exchange.data.l.open[0]

        return size * (exit_price - entry_price)

    @property
    def balance(self) -> float:
        """Balance of account

        Returns:
            float: _description_
        """
        return self._balance

    @property
    @abstractmethod
    def equity(self) -> float:
        """Equity value of account

        Returns:
            float: _description_
        """
        raise NotImplementedError(type(self))

    def _equity_snapshot(self):
        if self._do_equity_snapshot or len(self._exchange.positions) > 0:
            equity = self.equity

            bar = self._exchange.data.bar()
            self._equities[bar] = equity

            if equity <= 0:
                raise LetAccountInsufficientException()

            if self._do_equity_snapshot:
                self._do_equity_snapshot = False

    def on_positions(self, positions: list["Position"]):
        """Event positions updated"""
        if not self._do_equity_snapshot:
            self._do_equity_snapshot = True
