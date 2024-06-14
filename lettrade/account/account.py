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

    _is_equity_snapshot: bool
    _is_equity_snapshot_everytick: bool
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

        self._is_equity_snapshot = self._config.get("equity_snapshot", True)
        self._is_equity_snapshot_everytick = self._config.get(
            "equity_snapshot_everytick", True
        )
        self._do_equity_snapshot = True  # Snapshot balance

    def init(self, exchange: "Exchange"):
        self._exchange = exchange

    def __repr__(self):
        return "<Account " + str(self) + ">"

    def start(self):
        """Start account"""

    def stop(self):
        """Stop account"""
        self._equity_snapshot()

    def risk(self, side: "OrderSide", size: float, **kwargs) -> float:
        """Risk calculation"""
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

    def _equity_snapshot(self):
        if not self._is_equity_snapshot:
            return

        if self._do_equity_snapshot or (
            self._is_equity_snapshot_everytick and len(self._exchange.trades) > 0
        ):
            bar = self._exchange.data.bar()
            self._equities[bar] = self.equity

            if self._do_equity_snapshot:
                self._do_equity_snapshot = False

    def _on_trade_entry(self, trade: "Trade"):
        if not self._do_equity_snapshot:
            self._do_equity_snapshot = True

    def _on_trade_exit(self, trade: "Trade"):
        self._cash += trade.pl - trade.fee

        if not self._do_equity_snapshot:
            self._do_equity_snapshot = True
