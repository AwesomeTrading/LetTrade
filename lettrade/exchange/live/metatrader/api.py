import logging
import time
from datetime import datetime, timedelta
from typing import Optional

from box import Box
from mt5linux import MetaTrader5 as MT5

from lettrade.exchange.live import LiveAPI, LiveOrder, LivePosition

logger = logging.getLogger(__name__)


TIMEFRAME_L2M = {
    "1m": MT5.TIMEFRAME_M1,
    "2m": MT5.TIMEFRAME_M2,
    "3m": MT5.TIMEFRAME_M3,
    "4m": MT5.TIMEFRAME_M4,
    "5m": MT5.TIMEFRAME_M5,
    "6m": MT5.TIMEFRAME_M6,
    "10m": MT5.TIMEFRAME_M10,
    "12m": MT5.TIMEFRAME_M12,
    "15m": MT5.TIMEFRAME_M15,
    "20m": MT5.TIMEFRAME_M20,
    "30m": MT5.TIMEFRAME_M30,
    "1h": MT5.TIMEFRAME_H1,
    "2h": MT5.TIMEFRAME_H2,
    "3h": MT5.TIMEFRAME_H3,
    "4h": MT5.TIMEFRAME_H4,
    "6h": MT5.TIMEFRAME_H6,
    "8h": MT5.TIMEFRAME_H8,
    "12h": MT5.TIMEFRAME_H12,
    "1d": MT5.TIMEFRAME_D1,
    "1w": MT5.TIMEFRAME_W1,
    "1mn": MT5.TIMEFRAME_MN1,
}


class MetaTraderAPI(LiveAPI):
    _mt5: MT5
    _callbacker: "MetaTraderExchange"
    _magic: int

    __deal_time_checked = datetime.now() - timedelta(days=1)
    __orders_stored: dict[int, object] = {}
    __positions_stored: dict[int, object] = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_singleton"):
            cls._singleton = object.__new__(cls)
        return cls._singleton

    @classmethod
    def multiprocess(cls, kwargs, **other_kwargs):
        # Pop to remove parameter "wine", then subprocess will not start wine server
        wine = kwargs.pop("wine", None)
        if not wine:
            return

        cls._wine_process(wine)

    @classmethod
    def _wine_process(cls, wine: str):
        from subprocess import Popen

        logger.info("Start Wine MetaTrader rpyc from path: %s", wine)
        Popen(wine, shell=True)

        # Wait for wine start
        time.sleep(5)

    def __init__(
        self,
        login: int,
        password: str,
        server: str,
        timeout: int = 60,
        retry: int = 20,
        host: str = "localhost",
        port: int = 18812,
        wine: Optional[str] = None,
        magic: int = 88888888,
        **kwargs,
    ):
        self._magic = magic

        # Start wine server if not inited
        if wine:
            self.__class__._wine_process(wine)

        try:
            self._mt5 = MT5(host=host, port=port)
        except ConnectionRefusedError as e:
            raise ConnectionRefusedError(
                "Cannot connect to MetaTrader 5 Terminal rpyc server"
            ) from e
        except TimeoutError as e:
            raise RuntimeError("Timeout start MetaTrader 5 Terminal") from e

        # Terminal
        terminal = self._mt5.terminal_info()
        logger.info("Terminal information: %s", str(terminal))
        if not terminal.trade_allowed:
            logger.warning("Terminal trading mode is not allowed")

        # Login account
        account = self.account()
        if not account or account.login != login:
            while retry > 0:
                login = self._mt5.initialize(
                    login=int(login),
                    password=password,
                    server=server,
                    # timeout=timeout,
                )
                if login:
                    break

                if __debug__:
                    logger.info("Login retry: %d", retry)

                time.sleep(1)
                retry -= 1

            if retry == 0:
                raise RuntimeError(f"Cannot login {account}")

            # Preload trading data
            now = datetime.now()
            self._mt5.history_deals_get(now - timedelta(weeks=4), now)
            self._mt5.orders_get()
            self._mt5.positions_get()
            time.sleep(5)

        logger.info(
            "Login success account=%s, server=%s, version=%s",
            account,
            server,
            self._mt5.version(),
        )

    def start(self, callbacker=None):
        self._callbacker = callbacker
        self._check_transactions()

    def stop(self):
        self._mt5.shutdown()

    def next(self):
        self._check_transactions()

    def heartbeat(self):
        return True

    ### Public
    def market(self, symbol):
        return self._mt5.symbol_info(symbol)

    def markets(self, search=None):
        """The filter for arranging a group of necessary symbols. Optional parameter.
        If the group is specified, the function returns only symbols meeting a specified criteria.

        Search example:
            Get symbols whose names do not contain USD, EUR, JPY and GBP
            search="*,!*USD*,!*EUR*,!*JPY*,!*GBP*"
        """
        return self._mt5.symbols_get(search)

    def tick_get(self, symbol):
        return self._mt5.symbol_info_tick(symbol)

    def bars(
        self,
        symbol,
        timeframe,
        since: Optional[int | datetime] = 0,
        to: Optional[int | datetime] = 1_000,
    ):
        timeframe = TIMEFRAME_L2M[timeframe]

        if isinstance(since, int):
            return self._mt5.copy_rates_from_pos(symbol, timeframe, since, to)

        if isinstance(to, int):
            return self._mt5.copy_rates_from(symbol, timeframe, since, to)

        return self._mt5.copy_rates_range(symbol, timeframe, since, to)

    ### Private
    # Account
    def account(self):
        return self._mt5.account_info()

    # Order
    def order_open(self, order: LiveOrder):
        request = self._parse_order_request(order)
        raw = self._mt5.order_send(request)
        return self._parse_order_response(raw)

    def _parse_order_request(self, order: LiveOrder, deviation=10):
        tick = self.tick_get(order.data.symbol)
        price = tick.ask if order.is_long else tick.bid
        type = MT5.ORDER_TYPE_BUY if order.is_long else MT5.ORDER_TYPE_SELL

        request = {
            "action": MT5.TRADE_ACTION_DEAL,
            "symbol": order.data.symbol,
            "volume": abs(order.size),
            "type": type,
            "price": price,
            "deviation": deviation,
            "magic": self._magic,
            "type_time": MT5.ORDER_TIME_GTC,
            "type_filling": MT5.ORDER_FILLING_IOC,
        }
        if order.sl:
            request["sl"] = order.sl
        if order.tp:
            request["tp"] = order.tp
        if order.tag:
            request["comment"] = order.tag

        if __debug__:
            logger.info("New order request: %s", request)

        return request

    def order_update(self, order: LiveOrder, sl=None, tp=None, **kwargs):
        raise NotImplementedError

    def order_close(self, order: LiveOrder, **kwargs):
        raise NotImplementedError

    def _parse_order_response(self, raw):
        # raw = raw._asdict()
        # raw["request"] = raw["request"]._asdict()

        raw = Box(dict(raw._asdict()))
        raw.code = raw.retcode
        if raw.code == MT5.TRADE_RETCODE_DONE:
            raw.code = 0

        if __debug__:
            logger.info("New order response: %s", raw)

        return raw

    def orders_total(self):
        return self._mt5.orders_total()

    def orders_get(self, **kwargs):
        return self._mt5.orders_get(**kwargs)

    # Trade
    def positions_total(self):
        return self._mt5.positions_total()

    def positions_get(self, **kwargs):
        return self._mt5.positions_get(**kwargs)

    def position_update(self, trade: "LivePosition", sl=None, tp=None, **kwargs):
        raise NotImplementedError

    # Transaction
    def _check_transactions(self):
        if not self._callbacker:
            return

        # Deals
        deals = self._check_deals()
        if deals:
            self._callbacker.on_new_deals(deals)

        # Orders
        orders, removed_orders = self._check_orders()
        if orders:
            self._callbacker.on_new_orders(orders)
        if removed_orders:
            self._callbacker.on_old_orders(removed_orders)

        # Positions
        positions, removed_positions = self._check_positions()
        if positions:
            self._callbacker.on_new_positions(positions)
        if removed_positions:
            self._callbacker.on_old_positions(removed_positions)

    # Deal
    def _check_deals(self):
        to = datetime.now()  # + timedelta(days=1)

        deal_total = self._mt5.history_deals_total(self.__deal_time_checked, to)

        # No thing new in deal
        if deal_total <= 0:
            return

        raws = self._mt5.history_deals_get(self.__deal_time_checked, to)

        # Update last check time +1 second
        self.__deal_time_checked = datetime.fromtimestamp(raws[-1].time + 1)

        return raws

    # Order
    def _check_orders(self):
        order_total = self._mt5.orders_total()

        # No thing new in order
        if order_total <= 0 and len(self.__orders_stored) == 0:
            return None, None

        raws = self._mt5.orders_get()
        tickets = [raw.ticket for raw in raws]

        removed_orders = [
            raw for raw in self.__orders_stored.values() if raw.ticket not in tickets
        ]

        added_orders = []
        for raw in raws:
            if raw.ticket in self.__orders_stored:
                stored = self.__orders_stored[raw.ticket]
                if (
                    raw.sl == stored.sl
                    and raw.tp == stored.tp
                    and raw.volume_current == stored.volume_current
                    and raw.price_open == stored.price_open
                    and raw.price_stoplimit == stored.price_stoplimit
                ):
                    continue

            added_orders.append(raw)
        self.__orders_stored = {raw.ticket: raw for raw in raws}
        return added_orders, removed_orders

    # Trade
    def _check_positions(self):
        positions_total = self._mt5.positions_total()

        # No thing new in trade
        if positions_total <= 0 and len(self.__positions_stored) == 0:
            return None, None

        raws = self._mt5.positions_get()
        tickets = [raw.ticket for raw in raws]

        removed_positions = [
            raw for raw in self.__positions_stored.values() if raw.ticket not in tickets
        ]

        added_positions = []
        for raw in raws:
            if raw.ticket in self.__positions_stored:
                stored = self.__positions_stored[raw.ticket]
                if (
                    raw.time_update == stored.time_update
                    and raw.sl == stored.sl
                    and raw.tp == stored.tp
                    and raw.volume == stored.volume
                    and raw.price_open == stored.price_open
                ):
                    continue

            added_positions.append(raw)

        self.__positions_stored = {raw.ticket: raw for raw in raws}
        return added_positions, removed_positions

    # Bypass pickle
    def __copy__(self):
        return self.__class__._singleton

    def __deepcopy__(self, memo):
        return self.__class__._singleton
