import functools
import logging
import time
from datetime import datetime, timedelta
from subprocess import Popen
from typing import TYPE_CHECKING

from box import Box
from mt5linux import MetaTrader5 as MT5

from lettrade.exchange import OrderType
from lettrade.exchange.live import LetLiveOrderInvalidException, LiveAPI

if TYPE_CHECKING:
    from .metatrader import MetaTraderExchange
    from .trade import MetaTraderOrder, MetaTraderPosition

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


class _RetryException(Exception):
    pass


def mt5_connection(api_function):
    @functools.wraps(api_function)
    def wrapper(self: "MetaTraderAPI", *args, api_retry: int = 3, **kwargs):
        while api_retry > 0:
            try:
                return api_function(self, *args, **kwargs)
            except _RetryException:
                pass

            logger.warning(
                "Retry to reconnect MetaTrader 5 RPC for functon %s", api_function
            )
            if not self._refresh_environments():
                return None

            time.sleep(1)
            api_retry -= 1

    return wrapper


class MetaTraderAPI(LiveAPI):
    """API to connect MetaTrader 5 Terminal"""

    _mt5: MT5
    _exchange: "MetaTraderExchange"
    _magic: int
    _config: dict

    _load_history_since: datetime
    _deal_time_checked: datetime
    _orders_stored: dict[int, object]
    _executions_stored: dict[int, object]
    _positions_stored: dict[int, object]

    _wine_process: Popen | None = None

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

        cls._wine_run(wine)

    @classmethod
    def _wine_run(cls, wine: str):
        if cls._wine_process is not None and cls._wine_process.poll() is None:
            logger.info("Wine MetaTrader rpyc is running: %s", wine)
            return

        logger.info("Start new Wine MetaTrader rpyc from path: %s", wine)
        cls._wine_process = Popen(wine, shell=True)

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
        wine: str | None = None,
        path: str | None = None,
        magic: int = 88888888,
        **kwargs,
    ):
        """_summary_

        Args:
            login (int): _description_
            password (str): _description_
            server (str): _description_
            timeout (int, optional): _description_. Defaults to 60.
            retry (int, optional): _description_. Defaults to 20.
            host (str, optional): _description_. Defaults to "localhost".
            port (int, optional): _description_. Defaults to 18812.
            wine (str | None, optional): _description_. Defaults to None.
            magic (int, optional): _description_. Defaults to 88888888.

        Raises:
            ConnectionRefusedError: _description_
            RuntimeError: _description_
        """
        # Parameters
        self._config = kwargs
        self._magic = magic

        self._load_history_since = datetime.now() - timedelta(days=7)
        self._deal_time_checked = datetime.now() - timedelta(days=1)
        self._orders_stored = dict()
        self._executions_stored = dict()
        self._positions_stored = dict()

        # Update config
        self._config.update(
            host=host,
            port=port,
            login=int(login),
            password=password,
            server=server,
            wine=wine,
            path=path,
            retry=retry,
        )

        # Start enviroments
        self._refresh_environments()

    def _refresh_environments(self) -> bool:
        # Check start wine server if not inited yet
        wine = self._config.get("wine", False)
        if wine:
            self.__class__._wine_run(wine)

        # Init MT5
        if not hasattr(self, "_mt5") or self._mt5.account_info() is None:
            host = self._config.get("host")
            port = self._config.get("port")

            try:
                self._mt5 = MT5(host=host, port=port)
            except ConnectionRefusedError as e:
                raise ConnectionRefusedError(
                    "Cannot connect to MetaTrader 5 Terminal rpyc server"
                ) from e
            except TimeoutError as e:
                raise RuntimeError("Timeout start MetaTrader 5 Terminal") from e

        # Login account
        account = self._mt5.account_info()
        login = self._config.get("login")
        if not account or account.login != login:
            kwargs = dict()
            kwargs["login"] = int(login)
            kwargs["password"] = self._config.get("password")
            kwargs["server"] = self._config.get("server")

            path = self._config.get("path", None)
            if path is not None:
                kwargs["path"] = path

            retry = self._config.get("retry")
            while retry > 0:
                login = self._mt5.initialize(**kwargs)
                if login:
                    break

                if __debug__:
                    logger.debug("Login retry: %d", retry)

                time.sleep(1)
                retry -= 1

            if retry == 0:
                raise RuntimeError(f"Cannot login {account}: {self._mt5.last_error()}")

            # Terminal
            terminal = self._mt5.terminal_info()
            logger.info("Terminal: %s", str(terminal))
            if not terminal.trade_allowed:
                logger.warning("Terminal trading mode is not allowed")

            # Account
            logger.info("Login success: %s %s", kwargs, self._mt5.version())

            # Preload trading data
            now = datetime.now()
            self._mt5.history_deals_get(self._deal_time_checked, now)
            self._mt5.history_orders_get(self._load_history_since, now)
            self._mt5.orders_get()
            self._mt5.positions_get()
            time.sleep(3)

        return True

    def start(self, exchange: "MetaTraderExchange"):
        """_summary_

        Args:
            exchange (MetaTraderExchange): _description_
        """
        self._exchange = exchange

        self._load_history_transactions()
        self._check_transaction_events()

    def stop(self):
        """Stop MetaTrader 5 Terminal"""
        self._mt5.shutdown()

    def next(self):
        """Next tick action"""
        self._check_transaction_events()

    def heartbeat(self) -> bool:
        """Heartbeat

        Returns:
            bool: _description_
        """
        return True

    # ----- Public
    # --- Market
    @mt5_connection
    def market(self, symbol: str, **kwargs) -> dict:
        """_summary_

        Args:
            symbol (str): _description_

        Returns:
            dict: _description_
        """
        raw = self._mt5.symbol_info(symbol)
        if raw is None:
            raise _RetryException()
        return self._market_parse_response(raw)

    @mt5_connection
    def markets(self, search: str | None = None, **kwargs) -> list[dict]:
        """The filter for arranging a group of necessary symbols.
        If the group is specified, the function returns only symbols meeting a specified criteria.

        Search example:
            Get symbols whose names do not contain USD, EUR, JPY and GBP
            `search="*,!*USD*,!*EUR*,!*JPY*,!*GBP*"`

        Args:
            search (str | None, optional): _description_. Defaults to None.

        Returns:
            list[dict]: _description_
        """
        raws = self._mt5.symbols_get(search)
        if raws is None:
            raise _RetryException()
        return [self._market_parse_response(raw) for raw in raws]

    def _market_parse_response(self, raw):
        raw = Box(dict(raw._asdict()))
        type = raw.path.split("\\", 1)[0]
        return Box(
            symbol=raw.name,
            type=type,
            description=raw.description,
            currency_base=raw.currency_base,
            currency_profit=raw.currency_profit,
            raw=raw,
        )

    # --- Tick
    @mt5_connection
    def tick_get(self, symbol: str, **kwargs) -> dict:
        """_summary_

        Args:
            symbol (str): _description_

        Returns:
            dict: _description_
        """
        raw = self._mt5.symbol_info_tick(symbol)
        if raw is None:
            raise _RetryException()
        return raw

    @mt5_connection
    def bars(
        self,
        symbol,
        timeframe,
        since: int | datetime | None = 0,
        to: int | datetime | None = 1_000,
        **kwargs,
    ) -> list[list]:
        """_summary_

        Args:
            symbol (_type_): _description_
            timeframe (_type_): _description_
            since (int | datetime | None, optional): _description_. Defaults to 0.
            to (int | datetime | None, optional): _description_. Defaults to 1_000.

        Returns:
            list[list]: _description_
        """
        timeframe = TIMEFRAME_L2M[timeframe]

        if isinstance(since, int):
            raw = self._mt5.copy_rates_from_pos(symbol, timeframe, since, to)

        elif isinstance(to, int):
            raw = self._mt5.copy_rates_from(symbol, timeframe, since, to)
        else:
            raw = self._mt5.copy_rates_range(symbol, timeframe, since, to)

        if raw is None:
            raise _RetryException()
        return raw

    # Private
    # Account
    @mt5_connection
    def account(self, **kwargs) -> dict:
        """Metatrader 5 account information

        Returns:
            dict: _description_
        """
        raw = self._mt5.account_info()
        if raw is None:
            raise _RetryException()
        return raw

    # Order
    @mt5_connection
    def orders_total(
        self,
        since: datetime | None = None,
        to: datetime | None = None,
        **kwargs,
    ) -> int:
        """_summary_

        Args:
            since (datetime | None, optional): _description_. Defaults to None.
            to (datetime | None, optional): _description_. Defaults to None.

        Returns:
            int: _description_
        """
        if since is not None:
            kwargs["date_from"] = since
        if to is not None:
            kwargs["date_to"] = to

        raw = self._mt5.orders_total(**kwargs)
        if raw is None:
            raise _RetryException()

        return raw

    @mt5_connection
    def orders_get(
        self,
        id: str | None = None,
        symbol: str | None = None,
        **kwargs,
    ) -> list[dict]:
        """_summary_

        Args:
            id (str | None, optional): _description_. Defaults to None.
            symbol (str | None, optional): _description_. Defaults to None.

        Returns:
            list[dict]: _description_
        """
        if id is not None:
            kwargs["ticket"] = int(id)
        if symbol is not None:
            kwargs["symbol"] = symbol

        raws = self._mt5.orders_get(**kwargs)

        # Return None to retry
        if raws is None:
            raise _RetryException()

        return [self._order_parse_response(raw) for raw in raws]

    def order_open(self, order: "MetaTraderOrder") -> dict:
        """_summary_

        Args:
            order (MetaTraderOrder): _description_

        Raises:
            NotImplementedError: _description_

        Returns:
            dict: _description_
        """
        match order.type:
            case OrderType.Limit:
                price = order.limit_price
            case OrderType.Stop:
                price = order.stop_price
            case OrderType.Market:
                tick = self.tick_get(order.data.symbol)
                price = tick.ask if order.is_long else tick.bid
            case _:
                raise NotImplementedError(
                    f"Open order type {order.type} is not implement yet"
                )

        type = MT5.ORDER_TYPE_BUY if order.is_long else MT5.ORDER_TYPE_SELL

        return self.do_order_open(
            symbol=order.data.symbol,
            type=type,
            size=order.size,
            price=price,
            sl=order.sl,
            tp=order.tp,
            tag=order.tag,
        )

    @mt5_connection
    def do_order_open(
        self,
        symbol: str,
        size: float,
        type: int,
        price: float,
        sl: float = None,
        tp: float = None,
        tag: str | None = None,
        deviation: int = 10,
        **kwargs,
    ) -> dict:
        """_summary_

        Args:
            symbol (str): _description_
            size (float): _description_
            type (int): _description_
            price (float): _description_
            sl (float, optional): _description_. Defaults to None.
            tp (float, optional): _description_. Defaults to None.
            tag (str, optional): _description_. Defaults to "".
            deviation (int, optional): _description_. Defaults to 10.

        Returns:
            dict: _description_
        """
        request = self._parse_trade_request(
            symbol=symbol,
            size=size,
            type=type,
            price=price,
            sl=sl,
            tp=tp,
            tag=tag,
            deviation=deviation,
        )
        raw = self._mt5.order_send(request)

        # Retry
        if raw is None:
            raise _RetryException()

        raw = self._parse_trade_send_response(raw)
        if raw.code != 0:
            raise LetLiveOrderInvalidException(raw.error, raw=raw)

        return raw

    def _parse_trade_request(
        self,
        symbol: str | None = None,
        size: float | None = None,
        type: int | None = None,
        price: float | None = None,
        sl: float | None = None,
        tp: float | None = None,
        tag: str | None = None,
        position: int | None = None,
        deviation: int = 10,
        action: int = MT5.TRADE_ACTION_DEAL,
        type_time: int = MT5.ORDER_TIME_GTC,
        type_filling: int = MT5.ORDER_FILLING_IOC,
    ):
        request = {
            "magic": self._magic,
            "action": action,
            "deviation": deviation,
            "type_time": type_time,
            "type_filling": type_filling,
        }

        if symbol is not None:
            request["symbol"] = symbol
        if size is not None:
            request["volume"] = abs(size)
        if type is not None:
            request["type"] = type
        if price is not None:
            request["price"] = price
        if sl is not None:
            request["sl"] = sl
        if tp is not None:
            request["tp"] = tp
        if tag is not None:
            request["comment"] = tag
        if position is not None:
            request["position"] = position

        if __debug__:
            logger.info("New trade request: %s", request)

        return request

    def order_update(self, order: "MetaTraderOrder", sl=None, tp=None, **kwargs):
        raise NotImplementedError

    def order_close(self, order: "MetaTraderOrder", **kwargs):
        raise NotImplementedError

    def _parse_trade_send_response(self, raw) -> dict:
        if raw is None:
            raise RuntimeError("Trade response is None")

        response = Box(dict(raw._asdict()))

        # Error code
        response.code = response.retcode
        if response.code == MT5.TRADE_RETCODE_DONE:
            response.code = 0
        elif response.code == MT5.TRADE_RETCODE_NO_CHANGES:
            logger.warning(
                "Trade response nothing changes code %s %s", response.code, response
            )
            response.code = 0
        if response.code != 0:
            response.error = response.comment

        # Order
        if hasattr(response, "order"):
            response.order_id = response.order

        # Execution
        if hasattr(response, "deal"):
            response.execution_id = response.deal

        if __debug__:
            logger.info("New order response: %s", response)

        return response

    @mt5_connection
    def orders_history_total(
        self,
        since: datetime | None = None,
        to: datetime | None = None,
        **kwargs,
    ) -> int:
        """_summary_

        Args:
            since (datetime | None, optional): _description_. Defaults to None.
            to (datetime | None, optional): _description_. Defaults to None.

        Returns:
            int: _description_
        """
        if since is not None:
            kwargs["date_from"] = since
        if to is not None:
            kwargs["date_to"] = to

        raw = self._mt5.history_orders_get(**kwargs)
        if raw is None:
            raise _RetryException()
        return raw

    @mt5_connection
    def orders_history_get(
        self,
        id: str | None = None,
        position_id: str | None = None,
        since: datetime | None = None,
        to: datetime | None = None,
        **kwargs,
    ) -> list[dict]:
        """_summary_

        Args:
            id (str | None, optional): _description_. Defaults to None.
            position_id (str | None, optional): _description_. Defaults to None.
            since (datetime | None, optional): _description_. Defaults to None.
            to (datetime | None, optional): _description_. Defaults to None.

        Returns:
            list[dict]: _description_
        """
        if id is not None:
            kwargs["ticket"] = int(id)
        if position_id is not None:
            kwargs["position"] = int(position_id)
        if since is not None:
            kwargs["date_from"] = since
        if to is not None:
            kwargs["date_to"] = to

        raws = self._mt5.history_orders_get(**kwargs)

        # Retry
        if raws is None:
            raise _RetryException()

        return [self._order_parse_response(raw) for raw in raws]

    def _order_parse_response(self, raw):
        response = Box(dict(raw._asdict()))
        return response

    # Execution
    @mt5_connection
    def executions_total(
        self,
        since: datetime | None = None,
        to: datetime | None = None,
        **kwargs,
    ) -> int:
        """_summary_

        Args:
            since (datetime | None, optional): _description_. Defaults to None.
            to (datetime | None, optional): _description_. Defaults to None.

        Returns:
            int: _description_
        """
        if since is not None:
            kwargs["date_from"] = since
        if to is not None:
            kwargs["date_to"] = to

        raw = self._mt5.history_deals_total(**kwargs)
        if raw is None:
            raise _RetryException()
        return raw

    @mt5_connection
    def executions_get(
        self,
        position_id: str | None = None,
        search: str | None = None,
        **kwargs,
    ) -> list[dict]:
        """_summary_

        Args:
            position_id (str | None, optional): _description_. Defaults to None.
            search (str | None, optional): _description_. Defaults to None.

        Returns:
            list[dict]: _description_
        """
        if position_id is not None:
            kwargs["position"] = int(position_id)
        if search is not None:
            kwargs["group"] = search

        raws = self._mt5.history_deals_get(**kwargs)

        # Retry
        if raws is None:
            raise _RetryException()

        # May be wrong account when position exist but no execution
        if not raws and position_id is not None:
            logger.warning(
                "Execution retry check connection when position=%s exist but no execution",
                position_id,
            )

            # Retry check mt5 connection
            raise _RetryException()

        if __debug__:
            logger.debug("Raw executions: %s", raws)

        return [self._execution_parse_response(raw) for raw in raws]

    @mt5_connection
    def execution_get(self, id: str, **kwargs) -> dict:
        """_summary_

        Args:
            id (str): _description_

        Returns:
            dict: _description_
        """
        if id is not None:
            kwargs["ticket"] = int(id)

        raws = self._mt5.history_deals_get(**kwargs)

        # Retry
        if raws is None:
            raise _RetryException()

        if __debug__:
            logger.debug("Raw execution: %s", raws)

        return self._execution_parse_response(raws[0])

    def _execution_parse_response(self, raw):
        # Store
        self._executions_stored[raw.ticket] = raw

        raw = Box(dict(raw._asdict()))
        return raw

    # Position
    @mt5_connection
    def positions_total(
        self,
        since: datetime | None = None,
        to: datetime | None = None,
        **kwargs,
    ) -> int:
        """_summary_

        Args:
            since (datetime | None, optional): _description_. Defaults to None.
            to (datetime | None, optional): _description_. Defaults to None.

        Returns:
            int: _description_
        """
        if since is not None:
            kwargs["date_from"] = since
        if to is not None:
            kwargs["date_to"] = to

        raw = self._mt5.positions_total(**kwargs)
        if raw is None:
            raise _RetryException()
        return raw

    @mt5_connection
    def positions_get(
        self,
        id: str = None,
        symbol: str = None,
        **kwargs,
    ) -> list[dict]:
        """_summary_

        Args:
            id (str, optional): _description_. Defaults to None.
            symbol (str, optional): _description_. Defaults to None.

        Returns:
            list[dict]: _description_
        """
        if id is not None:
            kwargs.update(ticket=int(id))
        if symbol is not None:
            kwargs.update(symbol=symbol)

        raws = self._mt5.positions_get(**kwargs)

        # Retry
        if raws is None:
            raise _RetryException()

        return [self._position_parse_response(raw) for raw in raws]

    def position_update(
        self,
        position: "MetaTraderPosition",
        sl: float | None = None,
        tp: float | None = None,
        **kwargs,
    ) -> dict:
        """_summary_

        Args:
            position (MetaTraderPosition): _description_
            sl (float | None, optional): _description_. Defaults to None.
            tp (float | None, optional): _description_. Defaults to None.

        Returns:
            dict: _description_
        """
        return self.do_position_update(
            id=int(position.id),
            symbol=position.data.symbol,
            sl=sl,
            tp=tp,
            **kwargs,
        )

    @mt5_connection
    def do_position_update(
        self,
        id: int,
        # symbol: str,
        sl: float | None = None,
        tp: float | None = None,
        **kwargs,
    ) -> dict:
        """_summary_

        Args:
            id (int): _description_
            sl (float | None, optional): _description_. Defaults to None.
            tp (float | None, optional): _description_. Defaults to None.

        Returns:
            dict: _description_
        """
        request = self._parse_trade_request(
            position=id,
            # symbol=symbol,
            sl=sl,
            tp=tp,
            action=MT5.TRADE_ACTION_SLTP,
            **kwargs,
        )
        raw = self._mt5.order_send(request)

        # Retry
        if raw is None:
            raise _RetryException()

        return self._parse_trade_send_response(raw)

    def position_close(self, position: "MetaTraderPosition", **kwargs) -> dict:
        """Close a position

        Args:
            position (MetaTraderPosition): _description_

        Returns:
            dict: _description_
        """
        tick = self.tick_get(position.data.symbol)
        price = tick.ask if position.is_long else tick.bid

        # Opposite with position side
        type = MT5.ORDER_TYPE_SELL if position.is_long else MT5.ORDER_TYPE_BUY

        return self.do_position_close(
            id=int(position.id),
            symbol=position.data.symbol,
            type=type,
            size=position.size,
            price=price,
            **kwargs,
        )

    @mt5_connection
    def do_position_close(
        self,
        id: int,
        symbol: str,
        type: int,
        price: float,
        size: float,
        **kwargs,
    ) -> dict:
        request = self._parse_trade_request(
            position=id,
            symbol=symbol,
            type=type,
            price=price,
            size=size,
            **kwargs,
        )
        raw = self._mt5.order_send(request)

        # Retry
        if raw is None:
            raise _RetryException()

        return self._parse_trade_send_response(raw)

    def _position_parse_response(self, raw) -> dict:
        return Box(dict(raw._asdict()))

    # Transaction
    def _load_history_transactions(self):
        to = datetime.now()  # + timedelta(days=1)

        # History orders
        raws = self._mt5.history_orders_get(self._load_history_since, to)
        if raws is None:
            raise _RetryException()

        self._exchange.on_orders_event(old=raws)

        # # Positions
        # positions = self._mt5.positions_get(self._load_history_since, to)
        # if positions:
        #     self._exchange.on_positions_new(positions)

        # TODO: generate history order from
        # # History positions
        # positions = self._mt5.history_()
        # self._exchange.on_positions_old(positions)

    def _check_transaction_events(self):
        if not self._exchange:
            return

        # Deals
        deals = self._check_deals()
        if deals:
            self._exchange.on_executions_event(deals)

        # Orders
        orders_new, orders_old = self._check_orders()
        if orders_new or orders_old:
            self._exchange.on_orders_event(new=orders_new, old=orders_old)

        # Positions
        positions_new, positions_old = self._check_positions()
        if positions_new or positions_old:
            self._exchange.on_positions_event(new=positions_new, old=positions_old)

    # Deal
    @mt5_connection
    def _check_deals(self, **kwargs) -> list | bool | None:
        to = datetime.now()  # + timedelta(days=1)

        deal_total = self._mt5.history_deals_total(self._deal_time_checked, to)

        # Retry
        if deal_total is None:
            raise _RetryException()

        # No thing new in deal
        if deal_total <= 0:
            return False

        raws = self._mt5.history_deals_get(self._deal_time_checked, to)

        # Retry
        if raws is None:
            raise _RetryException()

        if len(raws) > 0:
            # Update last check time +1 second
            self._deal_time_checked = datetime.fromtimestamp(raws[-1].time + 1)

            # Store
            for raw in raws:
                self._executions_stored[raw.ticket] = raw

        return raws

    # Order
    @mt5_connection
    def _check_orders(self, **kwargs) -> tuple | None:
        order_total = self._mt5.orders_total()

        # Retry
        if order_total is None:
            raise _RetryException()

        # No thing new in order
        if order_total <= 0 and len(self._orders_stored) == 0:
            return None, None

        raws = self._mt5.orders_get()

        # Retry
        if raws is None:
            raise _RetryException()

        tickets = [raw.ticket for raw in raws]

        removed_orders = [
            raw for raw in self._orders_stored.values() if raw.ticket not in tickets
        ]

        added_orders = []
        for raw in raws:
            if raw.ticket in self._orders_stored:
                stored = self._orders_stored[raw.ticket]
                if (
                    raw.sl == stored.sl
                    and raw.tp == stored.tp
                    and raw.volume_current == stored.volume_current
                    and raw.price_open == stored.price_open
                    and raw.price_stoplimit == stored.price_stoplimit
                ):
                    continue

            added_orders.append(raw)
        self._orders_stored = {raw.ticket: raw for raw in raws}
        return added_orders, removed_orders

    # Trade
    @mt5_connection
    def _check_positions(self, **kwargs) -> tuple | None:
        positions_total = self._mt5.positions_total()

        # Retry
        if positions_total is None:
            raise _RetryException()

        # No thing new in trade
        if positions_total <= 0 and not bool(self._positions_stored):
            return None, None

        raws = self._mt5.positions_get()

        # Retry
        if raws is None:
            raise _RetryException()

        # May be wrong account when position exist but no execution
        if not raws and bool(self._positions_stored):
            position_exit = list(self._positions_stored.values())[-1]
            executions = [
                e
                for e in self._executions_stored.values()
                if e.position_id == position_exit.ticket
            ]

            # Execution is not close of position
            if not executions or executions[-1].type == position_exit.type:
                logger.warning(
                    "Positions retry check connection when position=%s exited but no execution",
                    position_exit.ticket,
                )
            raise _RetryException()

        tickets = [raw.ticket for raw in raws]
        raws = {raw.ticket: self._position_parse_response(raw) for raw in raws}

        removed_positions = [
            raw for raw in self._positions_stored.values() if raw.ticket not in tickets
        ]

        added_positions = []
        for raw in raws.values():
            if raw.ticket in self._positions_stored:
                stored = self._positions_stored[raw.ticket]
                if (
                    raw.time_update == stored.time_update
                    and raw.sl == stored.sl
                    and raw.tp == stored.tp
                    and raw.volume == stored.volume
                    # and raw.price_open == stored.price_open
                ):
                    continue

            added_positions.append(raw)

        self._positions_stored = raws
        return added_positions, removed_positions

    # Bypass pickle
    def __copy__(self):
        return self.__class__._singleton

    def __deepcopy__(self, memo):
        return self.__class__._singleton
