import logging
from datetime import datetime
from multiprocessing.managers import BaseManager
from typing import TYPE_CHECKING, Literal, Optional

import ccxt

from lettrade.exchange.live import LiveAPI

if TYPE_CHECKING:
    from .ccxt import CCXTExchange
    from .trade import CCXTOrder, CCXTPosition


logger = logging.getLogger(__name__)


class CCXTAPIExchange:
    """Single instance across multiprocessing. Help pickle-able result and send across multiprocessing"""

    _exchange: ccxt.Exchange

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_singleton"):
            cls._singleton = object.__new__(cls)
        return cls._singleton

    def __init__(
        self,
        exchange: str,
        key: str,
        secret: str,
        options: Optional[dict] = None,
        type: Literal["spot", "margin", "future"] = "spot",
        sandbox: bool = True,
        verbose: bool = False,
        **kwargs,
    ) -> None:
        config = dict(
            apiKey=key,
            secret=secret,
            enableRateLimit=True,
            defaultType=type,
            options={
                "sandboxMode": sandbox,
                "warnOnFetchOpenOrdersWithoutSymbol": False,
                "tradesLimit": 1,
                "ordersLimit": 1,
                "OHLCVLimit": 1,
            },
        )
        config.update(kwargs)

        if options is not None:
            config["options"].update(options)

        self._exchange = getattr(ccxt, exchange)(config)

        # Must call sanbox function instead of option sandboxMode
        self._exchange.set_sandbox_mode(sandbox)
        self._exchange.verbose = verbose
        logger.info("Starting exchange class: %s", self._exchange)

    def start(self):
        self._exchange.load_markets()

    def stop(self):
        """"""
        # self._exchange.close()

    # def __getattr__(self, attr: str) -> ccxt.Exchange:
    #     # if hasattr(self._exchange, attr):
    #     return getattr(self._exchange, attr)

    # Public functions
    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        return self._exchange.watch_trades(symbol, since, limit, params)

    def fetch_time(self):
        return self._exchange.milliseconds()

    # Ticker
    def fetch_ticker(self, symbol, **kwargs):
        return self._exchange.fetch_ticker(symbol, **kwargs)

    def watch_ticker(self, symbol, **kwargs):
        return self._exchange.watch_ticker(symbol, **kwargs)

    def fetch_tickers(self, symbols, **kwargs):
        return self._exchange.fetch_tickers(symbols, **kwargs)

    def watch_tickers(self, symbols, **kwargs):
        return self._exchange.watch_tickers(symbols)

    # Market
    def fetch_markets(self):
        return self._exchange.markets

    # Bar
    def fetch_ohlcv(self, *args, **kwargs):
        return self._exchange.fetch_ohlcv(*args, **kwargs)

    def watch_ohlcv(self, *args, **kwargs):
        return self._exchange.watch_ohlcv(*args, **kwargs)

    # Account functions
    # balance
    def fetch_my_balance(self, params={}):
        return self._exchange.fetch_balance(params)

    def watch_my_balance(self, params={}, **kwargs):
        return self._exchange.watch_balance(params)

    # Order
    def create_my_order(self, symbol, type, side, amount, price, **kwargs):
        return self._exchange.create_order(
            symbol=symbol,
            type=type,
            side=side,
            amount=amount,
            price=price,
            **kwargs,
        )

    def fetch_my_order(self, oid, symbol):
        return self._exchange.fetch_order(oid, symbol)

    def fetch_my_orders(self, symbol=None, since=None, limit=None, params={}):
        return self._exchange.fetch_orders(symbol, since, limit, params)

    def fetch_my_open_orders(self, symbol=None, since=None, limit=None, params={}):
        return self._exchange.fetch_open_orders(symbol, since, limit, params)

    def cancel_my_order(self, id, symbol):
        return self._exchange.cancel_order(id, symbol)

    def cancel_my_orders(self, symbol=None, params={}):
        return self._exchange.cancel_all_orders(symbol, params)

    # Trade
    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        return self._exchange.fetch_my_trades(symbol, since, limit, params)

    def watch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        return self._exchange.watch_my_trades(symbol, since, limit, params)

    # Position
    def fetch_my_position(self, symbol: str, params={}):
        return self._exchange.fetch_position(symbol, params)

    def fetch_my_positions(self, symbols=None, params={}):
        return self._exchange.fetch_positions(symbols, params)


class CCXTAPI(LiveAPI):
    """CCXT API"""

    _ccxt: CCXTAPIExchange
    _exchange: "CCXTExchange"

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_singleton"):
            cls._singleton = object.__new__(cls)
        return cls._singleton

    @classmethod
    def multiprocess(cls, kwargs, **other_kwargs):
        BaseManager.register("CCXTAPIExchange", CCXTAPIExchange)
        manager = BaseManager()
        manager.start()
        kwargs["ccxt"] = manager.CCXTAPIExchange(**kwargs)

    def __init__(
        self,
        exchange: int,
        key: str,
        secret: str,
        ccxt: Optional[CCXTAPIExchange] = None,
        **kwargs,
    ):
        """_summary_

        Args:
            exchange (int): _description_
            key (str): _description_
            secret (str): _description_
            ccxt (Optional[CCXTAPIExchange], optional): _description_. Defaults to None.
        """
        if ccxt is None:
            ccxt = CCXTAPIExchange(exchange=exchange, key=key, secret=secret, **kwargs)
        self._ccxt = ccxt

    # Bypass pickle
    def __copy__(self):
        return self.__class__._singleton

    def __deepcopy__(self, memo):
        return self.__class__._singleton

    def start(self, exchange: Optional["CCXTExchange"] = None):
        self._exchange = exchange
        self._ccxt.start()

    def stop(self):
        """"""
        # self._ccxt.stop()

    def next(self):
        pass

    def heartbeat(self):
        return True

    def market(self, symbol: str) -> dict:
        pass

    def markets(self, symbols: list[str]) -> dict:
        pass

    def tick_get(self, symbol: str) -> dict:
        pass

    # Bars
    def bars(
        self,
        symbol,
        timeframe,
        since: Optional[int | datetime] = 0,
        to: Optional[int | datetime] = 1_000,
        **kwargs,
    ) -> list[list]:
        return self._ccxt.fetch_ohlcv(symbol, timeframe, limit=to, **kwargs)

    ### Private
    # Account
    def account(self) -> dict:
        """"""
        return self._ccxt.fetch_my_balance()

    #  Order
    def order_open(self, order: "CCXTOrder", **kwargs):
        """"""
        result = self._ccxt.create_my_order(
            symbol=order.data.symbol,
            type=order.type.lower(),
            side=order.side.lower(),
            amount=abs(order.size),
            price=order.place_price,
            **kwargs,
        )
        print("order_open", order, result)
        return result

    def order_update(self, order: "CCXTOrder"):
        pass

    def order_close(self, order: "CCXTOrder"):
        """"""

    def orders_total(self):
        """"""

    def orders_get(self, **kwargs):
        """"""

    # Execution
    def executions_total(
        self,
        since: Optional[datetime] = None,
        to: Optional[datetime] = None,
        **kwargs,
    ) -> int:
        """"""

    def executions_get(
        self,
        position_id: Optional[str] = None,
        search: Optional[str] = None,
        **kwargs,
    ) -> list[dict]:
        """"""

    def execution_get(self, id: str, **kwargs) -> dict:
        """"""

    # Position
    def positions_total(
        self,
        since: Optional[datetime] = None,
        to: Optional[datetime] = None,
        **kwargs,
    ) -> int:
        """"""

    def positions_get(self, id: str = None, symbol: str = None, **kwargs) -> list[dict]:
        """"""

    def position_update(
        self,
        position: "CCXTPosition",
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        **kwargs,
    ) -> dict:
        """"""

    def position_close(self, position: "CCXTPosition", **kwargs) -> dict:
        """"""
