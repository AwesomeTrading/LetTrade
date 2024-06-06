import logging
from multiprocessing.managers import BaseManager
from typing import Optional

import ccxt

from lettrade.exchange.live import LiveAPI, LiveOrder

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
        options: dict = {},
        sandbox: bool = True,
        debug=False,
    ) -> None:
        config = dict(
            apiKey=key,
            secret=secret,
            enableRateLimit=True,
            options={
                "sandboxMode": sandbox,
                "warnOnFetchOpenOrdersWithoutSymbol": False,
                "tradesLimit": 1,
                "ordersLimit": 1,
                "OHLCVLimit": 1,
            },
        )
        config["options"].update(options)

        self._exchange = getattr(ccxt, exchange)(config)

        # Must call sanbox function instead of option sandboxMode
        self._exchange.set_sandbox_mode(sandbox)
        self._exchange.verbose = debug
        logger.info("Starting exchange class: %s", self._exchange)

    def start(self):
        self._exchange.load_markets()

    # def stop(self):
    #     self._exchange.close()

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
    def create_my_order(self, symbol, type, side, amount, price, params):
        return self._exchange.create_order(
            symbol=symbol,
            type=type,
            side=side,
            amount=amount,
            price=price,
            params=params,
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
    _ccxt: CCXTAPIExchange
    _callbacker: "CCXTExchange"

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

    # Bypass pickle
    def __copy__(self):
        return self.__class__._singleton

    def __deepcopy__(self, memo):
        return self.__class__._singleton

    def __init__(
        self,
        exchange: int,
        key: str,
        secret: str,
        ccxt: Optional[CCXTAPIExchange] = None,
        **kwargs,
    ):
        # Start wine server if not inited
        if ccxt is None:
            ccxt = CCXTAPIExchange(exchange=exchange, key=key, secret=secret, **kwargs)
        self._ccxt = ccxt

    def start(self, callbacker: Optional["CCXTExchange"] = None):
        self._callbacker = callbacker
        self._ccxt.start()

    def stop(self):
        """"""
        # self._ccxt.stop()

    def next(self):
        pass

    def heartbeat(self):
        return True

    def market(self, symbol):
        pass

    def markets(self, symbols: list):
        pass

    def tick_get(self, symbol):
        pass

    # Bars
    def bars(self, symbol, timeframe, since=0, to=1000):
        raws = self._ccxt.fetch_ohlcv(symbol, timeframe, limit=to)
        return self._parse_bars(raws)

    def _parse_bars(self, raws):
        for raw in raws:
            raw[0] = raw[0] / 1_000
        return raws

    ### Private
    # Account
    def account(self):
        """"""

    #  Order
    def order_open(self, order: LiveOrder):
        """"""

    def order_update(self, order: LiveOrder):
        pass

    def order_close(self, order: LiveOrder):
        """"""

    def orders_total(self):
        """"""

    def orders_get(self, **kwargs):
        """"""

    # Trade
    def trades_total(self):
        """"""

    def trades_get(self, **kwargs):
        """"""
