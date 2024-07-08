import logging
from datetime import datetime
from typing import Any, final

from lettrade.account import Account
from lettrade.commander import Commander
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import (
    Exchange,
    Execution,
    Order,
    OrderResult,
    Position,
    TradeSide,
)

logger = logging.getLogger(__name__)


class Strategy:
    """
    Base class to implement a strategy
    """

    def __init__(
        self,
        feeder: DataFeeder,
        exchange: Exchange,
        account: Account,
        commander: Commander,
        is_optimize: bool = False,
        **kwargs,
    ):
        """_summary_

        Args:
            feeder (DataFeeder): DataFeeder for strategy
            exchange (Exchange): Trading exchange
            account (Account): Account manager
            commander (Commander): Event/Command manager
            is_optimize (bool, optional): flag validate optimize condiction. Defaults to False.

        Raises:
            RuntimeError: Validate valid is_optimize flag
        """
        self.__feeder: DataFeeder = feeder
        self.__exchange: Exchange = exchange
        self.__account: Account = account
        self.__commander: Commander = commander

        self.__datas: list[DataFeed] = self.__feeder.datas
        self.__data: DataFeed = self.__feeder.data

        if is_optimize and self.is_live:
            raise RuntimeError("Optimize a live datafeeder")
        self.__is_optimize: bool = is_optimize

        # Set parameters
        if kwargs:
            logger.info("Update strategy parameters %s", kwargs)
            for k, v in kwargs.items():
                setattr(self, k, v)

    def init(self) -> None:
        """Init strategy variables"""

    def indicators(self, df: DataFeed) -> None:
        """All indicator and signal should implement here to cacheable.
        Because of `lettrade` will cache/pre-load all `DataFeed`.

        To add indicators for a special DataFeed, define a new function name
        `indicators_<DataFeed name>`.

        Usage:
            ```python
            df_eurusd = DataFeed(name="eurusd")
            df_gbpusd = DataFeed(name="gbpusd")

            # This function will load indicators for df_eurusd
            def indicators(self, df: DataFeed):
                df['ema'] = df.i.ema(window=21)

            # This function will load indicators for df_gbpusd
            def indicators_gbpusd(self, df: DataFeed):
                df['ema'] = df.i.ema(window=25)
            ```

        Args:
            df (DataFeed): DataFeed need to load indicators value
        """

    @final
    def _indicators_loader_inject(self):
        for data in self.datas:
            fn_name = f"indicators_{data.name.lower()}"
            if hasattr(self, fn_name):
                fn = getattr(self, fn_name)
            else:
                fn = self.indicators
            object.__setattr__(data, "indicators_load", fn)

    @final
    def _indicators_load(self):
        for data in self.datas:
            data.indicators_load(data)

    @final
    def _start(self):
        self._indicators_loader_inject()
        self._indicators_load()
        self.start(*self.datas)

    def start(self, df: DataFeed, *others: list[DataFeed]) -> None:
        """call after `init()` and before first `next()` is called

        Args:
            df (DataFeed): _description_

        Returns:
            _type_: `None`
        """

    @final
    def _next(self) -> None:
        if self.is_live:
            self._indicators_load()
        self.next(*self.datas)

    def next(self, df: DataFeed, *others: list[DataFeed]) -> None:
        """Next bar event"""

    @final
    def _stop(self) -> None:
        self.stop(*self.datas)

    def stop(self, df: DataFeed, *others: list[DataFeed]) -> None:
        """Call when strategy run completed

        Args:
            df (DataFeed): main data of strategy
        """

    @final
    def _plot(self, *datas: list[DataFeed]) -> dict:
        from lettrade.indicator import indicator_load_plotters
        from lettrade.plot import plot_merge

        config = dict()
        for data in datas:
            plot_merge(config, indicator_load_plotters(data))

        return plot_merge(config, self.plot(*datas))

    def plot(self, df: DataFeed, *others: list[DataFeed]) -> dict:
        """Custom config of plot

        Example:
            ```json
            {
                # Global items is main datafeed item
                "items": [],

                # DataFeed plot config
                "datafeed_name_eurusd": {
                    "items": [
                        {
                            "type": "scatter",
                            "x": dataframe.index,
                            "y": dataframe["close"],
                            "name": "EMA",
                            "mode": "lines",
                            "line": { "color": '#00bad6', "width": 1 },
                        }
                    ]
                },

                # Layout config
                {
                    "hovermode": "x unified"
                }
            }
            ```

        Args:
            df (DataFeed): plot DataFeed

        Returns:
            dict: config
        """
        return dict()

    @final
    def order_buy(
        self,
        size: float | None = None,
        limit: float | None = None,
        stop: float | None = None,
        sl: float | None = None,
        tp: float | None = None,
        tag: str | None = None,
        **kwargs,
    ) -> OrderResult:
        """Place a new long order.

        Args:
            size (float | None, optional): _description_. Defaults to None.
            limit (float | None, optional): _description_. Defaults to None.
            stop (float | None, optional): _description_. Defaults to None.
            sl (float | None, optional): _description_. Defaults to None.
            tp (float | None, optional): _description_. Defaults to None.
            tag (str | None, optional): _description_. Defaults to None.
            **kwargs (dict | None, optional): Extra-parameters send to `Exchange.new_order`

        Returns:
            OrderResult: order result information
        """
        return self.order_place(
            side=TradeSide.Buy,
            size=size,
            limit=limit,
            stop=stop,
            sl=sl,
            tp=tp,
            tag=tag,
            **kwargs,
        )

    buy = order_buy

    @final
    def order_sell(
        self,
        size: float | None = None,
        limit: float | None = None,
        stop: float | None = None,
        sl: float | None = None,
        tp: float | None = None,
        tag: str | None = None,
        **kwargs,
    ) -> OrderResult:
        """Place a new short order.

        Args:
            size (float | None, optional): _description_. Defaults to None.
            limit (float | None, optional): _description_. Defaults to None.
            stop (float | None, optional): _description_. Defaults to None.
            sl (float | None, optional): _description_. Defaults to None.
            tp (float | None, optional): _description_. Defaults to None.
            tag (str | None, optional): _description_. Defaults to None.
            **kwargs (dict | None, optional): Extra-parameters send to `Exchange.new_order`

        Returns:
            OrderResult: order result information
        """
        return self.order_place(
            side=TradeSide.Sell,
            size=size,
            limit=limit,
            stop=stop,
            sl=sl,
            tp=tp,
            tag=tag,
            **kwargs,
        )

    sell = order_sell

    @final
    def order_place(
        self,
        side: TradeSide,
        size: float | None = None,
        limit: float | None = None,
        stop: float | None = None,
        sl: float | None = None,
        tp: float | None = None,
        tag: str | None = None,
        **kwargs,
    ) -> OrderResult:
        """_summary_

        Args:
            side (TradeSide): _description_
            size (float | None, optional): _description_. Defaults to None.
            limit (float | None, optional): _description_. Defaults to None.
            stop (float | None, optional): _description_. Defaults to None.
            sl (float | None, optional): _description_. Defaults to None.
            tp (float | None, optional): _description_. Defaults to None.
            tag (str | None, optional): _description_. Defaults to None.

        Returns:
            OrderResult: _description_
        """
        params = dict(
            size=size,
            limit=limit,
            stop=stop,
            sl=sl,
            tp=tp,
            tag=tag,
            **kwargs,
        )
        params["size"] = side * abs(self.__account.risk(side=side, **params))
        return self.__exchange.new_order(**params)

    @final
    def positions_exit(self, side: TradeSide | None = None):
        for p in list(self.positions.values()):
            if side is not None and p.side != side:
                continue
            p.exit()

    @final
    @property
    def feeder(self) -> DataFeeder:
        """Getter of `DataFeeder`

        Returns:
            DataFeeder: _description_
        """
        return self.__feeder

    @final
    @property
    def exchange(self) -> Exchange:
        """Getter of `Exchange`

        Returns:
            Exchange: _description_
        """
        return self.__exchange

    @final
    @property
    def now(self) -> datetime:
        """Getter of current datetime

        Returns:
            datetime: current datetime of bar
        """
        return self.data.now

    @final
    @property
    def account(self) -> Account:
        """Getter of `Account`

        Returns:
            Account: _description_
        """
        return self.__account

    @final
    @property
    def commander(self) -> Commander:
        """Getter of `Commander`

        Returns:
            Commander: _description_
        """
        return self.__commander

    @final
    @property
    def data(self) -> DataFeed:
        """Getter of main DataFeed

        Returns:
            DataFeed: _description_
        """
        return self.__data

    @final
    @property
    def datas(self) -> list[DataFeed]:
        """Getter of all DataFeed

        Returns:
            list[DataFeed]: _description_
        """
        return self.__datas

    @final
    @property
    def orders(self) -> dict[str, Order]:
        """Getter of `Order` dict

        Returns:
            dict[str, Order]: _description_
        """
        return self.__exchange.orders

    @final
    @property
    def history_orders(self) -> dict[str, Order]:
        """Getter of history `Order` dict

        Returns:
            dict[str, Order]: _description_
        """
        return self.__exchange.history_orders

    @final
    @property
    def positions(self) -> dict[str, Position]:
        """Getter of `Position` dict

        Returns:
            dict[str, Position]: _description_
        """
        return self.__exchange.positions

    @final
    @property
    def history_positions(self) -> dict[str, Position]:
        """Getter of history `Position` dict

        Returns:
            dict[str, Position]: _description_
        """
        return self.__exchange.history_positions

    @final
    @property
    def is_live(self) -> bool:
        """Flag to check strategy is running in live DataFeeder

        Returns:
            bool: _description_
        """
        return self.__feeder.is_continous

    @final
    @property
    def is_backtest(self) -> bool:
        """Flag to check strategy is running in backtest DataFeeder

        Returns:
            bool: _description_
        """
        return not self.is_live

    @final
    @property
    def is_optimize(self) -> bool:
        """Flag to check strategy is running in optimize session

        Returns:
            bool: _description_
        """
        return self.__is_optimize

    # Events
    def on_transactions(self, trans: list[Execution | Order | Position]):
        """Listen for transaction events since `next()` begin

        Args:
            trans (list[Execution  |  Order  |  Position]): _description_
        """
        if hasattr(self, "on_transaction"):
            for tran in trans:
                self.on_transaction(tran)

    def on_executions(self, executions: list[Execution]):
        """Listen for `Execution` event since `next()` begin

        Args:
            executions (list[Execution]): _description_
        """
        if hasattr(self, "on_execution"):
            for execution in executions:
                self.on_execution(execution)

    def on_orders(self, orders: list[Order]):
        """Listen for `Order` event

        Args:
            orders (list[Order]): _description_
        """
        if hasattr(self, "on_order"):
            for order in orders:
                self.on_order(order)

    def on_positions(self, positions: list[Position]):
        """Listen for `Position` event since `next()` begin

        Args:
            positions (list[Position]): _description_
        """
        if hasattr(self, "on_position"):
            for position in positions:
                self.on_position(position)

    def on_notify(self, *args, **kwargs) -> None:
        """Listen for `notify` event since `next()` begin

        Returns:
            _type_: `None`
        """

    # Commander
    @final
    def send(self, msg: str, **kwargs) -> Any:
        """Send message to commander

        Args:
            msg (str): message string

        Returns:
            Any: _description_
        """
        return self.commander.send_message(msg=msg, **kwargs)
