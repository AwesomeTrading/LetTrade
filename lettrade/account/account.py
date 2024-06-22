from typing import TYPE_CHECKING

from .error import LetAccountInsufficientException

if TYPE_CHECKING:
    from lettrade.exchange import Exchange, Position, TradeSide


class Account:
    """
    Manage account balance, leverage, commission. Risk calculate and control
    """

    _config: dict

    _risk: float
    _cash: float
    _margin: float
    _leverage: float
    _equities: dict[str, float]

    _exchange: "Exchange"

    _do_equity_snapshot: bool

    def __init__(
        self,
        risk: float = 0.02,
        cash: float = 10_000,
        margin: float = 1.0,
        leverage: float = 1.0,
        **kwargs,
    ) -> None:
        """_summary_

        Args:
            risk (float, optional): _description_. Defaults to 0.02.
            cash (float, optional): _description_. Defaults to 10_000.
            margin (float, optional): _description_. Defaults to 1.0.
            leverage (float, optional): _description_. Defaults to 1.0.
        """
        self._risk = risk
        self._cash = cash
        self._margin = margin
        self._leverage = leverage
        self._config = kwargs

        self._equities = dict()

        self._do_equity_snapshot = True  # Snapshot balance

    def init(self, exchange: "Exchange"):
        self._exchange = exchange

    def __repr__(self):
        return "<Account " + str(self) + ">"

    def start(self):
        """Start account"""

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
    def equity(self) -> float:
        equity = self._cash
        if len(self._exchange.positions) > 0:
            equity += sum(position.pl for position in self._exchange.positions.values())
        return equity

    def _equity_snapshot(self):
        if self._do_equity_snapshot or len(self._exchange.positions) > 0:
            equity = self.equity

            bar = self._exchange.data.bar()
            self._equities[bar] = equity

            if equity <= 0:
                raise LetAccountInsufficientException()

            if self._do_equity_snapshot:
                self._do_equity_snapshot = False

    def _on_position_entry(self, position: "Position"):
        if not self._do_equity_snapshot:
            self._do_equity_snapshot = True

    def _on_position_exit(self, position: "Position"):
        self._cash += position.pl - position.fee

        if not self._do_equity_snapshot:
            self._do_equity_snapshot = True
