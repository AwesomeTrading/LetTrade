from abc import ABC, abstractmethod
from typing import Optional

from lettrade.account import Account
from lettrade.commander import Commander
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange, Execute, Order, OrderResult, Position, Trade


class Strategy(ABC):
    def __init__(
        self,
        feeder: DataFeeder,
        exchange: Exchange,
        account: Account,
        commander: Commander,
        is_optimize: bool = False,
    ):
        self.__feeder: DataFeeder = feeder
        self.__exchange: Exchange = exchange
        self.__account: Account = account
        self.__commander: Commander = commander

        if is_optimize and self.is_live:
            raise RuntimeError("Optimize a live datafeeder")
        self.__is_optimize: bool = is_optimize

    def init(self):
        pass

    def indicators(self):
        """
        All indicator and signal should implement here to cacheable
        Because of lettrade will cache/pre-load DataFeeds
        """

    def start(self, df: DataFeed):
        "start function will called before first next() is called"

    @abstractmethod
    def next(self, df: DataFeed):
        pass

    def end(self, df: DataFeed):
        pass

    def plot(self, df: DataFeed):
        return dict()

    def buy(
        self,
        *,
        size: Optional[float] = None,
        limit: Optional[float] = None,
        stop: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        tag: object = None,
        **kwargs,
    ) -> OrderResult:
        """
        Place a new long order. For explanation of parameters, see `Order` and its properties.
        """
        params = dict(
            limit=limit,
            stop=stop,
            sl=sl,
            tp=tp,
            tag=tag,
            **kwargs,
        )
        params["size"] = self.__account.risk(size=abs(size), **params)

        return self.__exchange.new_order(**params)

    def sell(
        self,
        *,
        size: Optional[float] = None,
        limit: Optional[float] = None,
        stop: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        tag: object = None,
        **kwargs,
    ) -> OrderResult:
        """
        Place a new short order. For explanation of parameters, see `Order` and its properties.
        """
        params = dict(
            limit=limit,
            stop=stop,
            sl=sl,
            tp=tp,
            tag=tag,
            **kwargs,
        )
        params["size"] = self.__account.risk(size=-abs(size), **params)

        return self.__exchange.new_order(**params)

    @property
    def feeder(self) -> DataFeeder:
        return self.__feeder

    @property
    def exchange(self) -> Exchange:
        return self.__exchange

    @property
    def now(self):
        return self.data.now

    @property
    def account(self) -> Account:
        return self.__account

    @property
    def commander(self) -> Commander:
        return self.__commander

    @property
    def data(self) -> DataFeed:
        return self.__feeder.data

    @property
    def datas(self) -> list[DataFeed]:
        return self.__feeder.datas

    @property
    def orders(self) -> dict[str, Order]:
        return self.__exchange.orders

    @property
    def history_orders(self) -> dict[str, Order]:
        return self.__exchange.history_orders

    @property
    def trades(self) -> dict[str, Trade]:
        return self.__exchange.trades

    @property
    def history_trades(self) -> dict[str, Trade]:
        return self.__exchange.history_trades

    @property
    def positions(self) -> dict[str, Position]:
        return self.__exchange.positions

    @property
    def is_live(self) -> bool:
        return self.__feeder.is_continous

    @property
    def is_backtest(self) -> bool:
        return not self.is_live

    @property
    def is_optimize(self) -> bool:
        return self.__is_optimize

    # Events
    def on_transaction(self, t):
        pass

    def on_execute(self, execute: Execute):
        pass

    def on_order(self, order: Order):
        pass

    def on_trade(self, trade: Trade):
        pass

    def on_position(self, position: Position):
        pass

    def on_notify(self, *args, **kwargs):
        pass

    # Commander
    def send_notify(self, msg, **kwargs):
        return self.commander.send_message(msg=msg, **kwargs)
