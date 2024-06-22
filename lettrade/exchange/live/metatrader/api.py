import logging
import time
from datetime import datetime, timedelta
from typing import Optional

from box import Box
from mt5linux import MetaTrader5 as MT5

from lettrade.exchange import OrderType
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
    """API to connect MetaTrader 5 Terminal"""

    _mt5: MT5
    _exchange: "MetaTraderExchange"
    _magic: int
    _use_execution: bool

    __load_history_since: datetime
    __deal_time_checked: datetime
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
        """_summary_

        Args:
            login (int): _description_
            password (str): _description_
            server (str): _description_
            timeout (int, optional): _description_. Defaults to 60.
            retry (int, optional): _description_. Defaults to 20.
            host (str, optional): _description_. Defaults to "localhost".
            port (int, optional): _description_. Defaults to 18812.
            wine (Optional[str], optional): _description_. Defaults to None.
            magic (int, optional): _description_. Defaults to 88888888.

        Raises:
            ConnectionRefusedError: _description_
            RuntimeError: _description_
            RuntimeError: _description_
        """
        # Parameters
        self._magic = magic
        self._use_execution = False
        self.__load_history_since = datetime.now() - timedelta(days=7)
        self.__deal_time_checked = datetime.now() - timedelta(days=1)
        self.__orders_stored = {}
        self.__positions_stored = {}

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
            self._mt5.history_deals_get(self.__deal_time_checked, now)
            self._mt5.history_orders_get(self.__load_history_since, now)
            self._mt5.orders_get()
            self._mt5.positions_get()
            time.sleep(5)

        # Terminal
        terminal = self._mt5.terminal_info()
        logger.info("Terminal information: %s", str(terminal))
        if not terminal.trade_allowed:
            logger.warning("Terminal trading mode is not allowed")

        # Account
        logger.info(
            "Login success account=%s, server=%s, version=%s",
            account,
            server,
            self._mt5.version(),
        )

    def start(self, exchange: "MetaTraderExchange"):
        """_summary_

        Args:
            exchange (MetaTraderExchange): _description_
        """
        self._exchange = exchange
        self._use_execution = exchange.executions is not None

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

    ### Public
    def market(self, symbol: str) -> dict:
        """_summary_

        Args:
            symbol (str): _description_

        Returns:
            dict: _description_
        """
        return self._mt5.symbol_info(symbol)

    def markets(self, search: Optional[str] = None) -> list[dict]:
        """The filter for arranging a group of necessary symbols. Optional parameter.
        If the group is specified, the function returns only symbols meeting a specified criteria.

        Search example:
            Get symbols whose names do not contain USD, EUR, JPY and GBP
            `search="*,!*USD*,!*EUR*,!*JPY*,!*GBP*"`

        Args:
            search (Optional[str], optional): _description_. Defaults to None.

        Returns:
            list[dict]: _description_
        """
        return self._mt5.symbols_get(search)

    def tick_get(self, symbol: str) -> dict:
        """_summary_

        Args:
            symbol (str): _description_

        Returns:
            dict: _description_
        """
        return self._mt5.symbol_info_tick(symbol)

    def bars(
        self,
        symbol,
        timeframe,
        since: Optional[int | datetime] = 0,
        to: Optional[int | datetime] = 1_000,
    ) -> list[list]:
        """_summary_

        Args:
            symbol (_type_): _description_
            timeframe (_type_): _description_
            since (Optional[int  |  datetime], optional): _description_. Defaults to 0.
            to (Optional[int  |  datetime], optional): _description_. Defaults to 1_000.

        Returns:
            list[list]: _description_
        """
        timeframe = TIMEFRAME_L2M[timeframe]

        if isinstance(since, int):
            return self._mt5.copy_rates_from_pos(symbol, timeframe, since, to)

        if isinstance(to, int):
            return self._mt5.copy_rates_from(symbol, timeframe, since, to)

        return self._mt5.copy_rates_range(symbol, timeframe, since, to)

    ### Private
    # Account
    def account(self) -> dict:
        """Metatrader 5 account information

        Returns:
            dict: _description_
        """
        return self._mt5.account_info()

    # Order
    def orders_total(
        self,
        since: Optional[datetime] = None,
        to: Optional[datetime] = None,
        **kwargs,
    ) -> int:
        """_summary_

        Args:
            since (Optional[datetime], optional): _description_. Defaults to None.
            to (Optional[datetime], optional): _description_. Defaults to None.

        Returns:
            int: _description_
        """
        if since is not None:
            kwargs["date_from"] = since
        if to is not None:
            kwargs["date_to"] = to

        return self._mt5.orders_total(**kwargs)

    def orders_get(
        self,
        id: Optional[str] = None,
        symbol: Optional[str] = None,
        **kwargs,
    ) -> list[dict]:
        """_summary_

        Args:
            id (Optional[str], optional): _description_. Defaults to None.
            symbol (Optional[str], optional): _description_. Defaults to None.

        Returns:
            list[dict]: _description_
        """
        if id is not None:
            kwargs["ticket"] = int(id)
        if symbol is not None:
            kwargs["symbol"] = symbol

        raws = self._mt5.orders_get(**kwargs)
        return [self._order_parse_response(raw) for raw in raws]

    def order_open(self, order: LiveOrder) -> dict:
        """_summary_

        Args:
            order (LiveOrder): _description_

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

    def do_order_open(
        self,
        symbol: str,
        size: float,
        type: int,
        price: float,
        sl: float = None,
        tp: float = None,
        tag: str = "",
        deviation: int = 10,
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
        return self._parse_trade_send_response(raw)

    def _parse_trade_request(
        self,
        symbol: Optional[str] = None,
        size: Optional[float] = None,
        type: Optional[int] = None,
        price: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        tag: Optional[str] = None,
        position: Optional[int] = None,
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

    def order_update(self, order: LiveOrder, sl=None, tp=None, **kwargs):
        raise NotImplementedError

    def order_close(self, order: LiveOrder, **kwargs):
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

    def orders_history_total(
        self,
        since: Optional[datetime] = None,
        to: Optional[datetime] = None,
        **kwargs,
    ) -> int:
        """_summary_

        Args:
            since (Optional[datetime], optional): _description_. Defaults to None.
            to (Optional[datetime], optional): _description_. Defaults to None.

        Returns:
            int: _description_
        """
        if since is not None:
            kwargs["date_from"] = since
        if to is not None:
            kwargs["date_to"] = to

        return self._mt5.history_orders_get(**kwargs)

    def orders_history_get(
        self,
        id: Optional[str] = None,
        position_id: Optional[str] = None,
        since: Optional[datetime] = None,
        to: Optional[datetime] = None,
        **kwargs,
    ) -> dict:
        """_summary_

        Args:
            id (Optional[str], optional): _description_. Defaults to None.
            position_id (Optional[str], optional): _description_. Defaults to None.
            since (Optional[datetime], optional): _description_. Defaults to None.
            to (Optional[datetime], optional): _description_. Defaults to None.

        Returns:
            dict: _description_
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
        return [self._order_parse_response(raw) for raw in raws]

    def _order_parse_response(self, raw):
        response = Box(dict(raw._asdict()))
        return response

    # Execution
    def executions_total(
        self,
        since: Optional[datetime] = None,
        to: Optional[datetime] = None,
        **kwargs,
    ) -> int:
        """_summary_

        Args:
            since (Optional[datetime], optional): _description_. Defaults to None.
            to (Optional[datetime], optional): _description_. Defaults to None.

        Returns:
            int: _description_
        """
        if since is not None:
            kwargs["date_from"] = since
        if to is not None:
            kwargs["date_to"] = to

        return self._mt5.history_deals_total(**kwargs)

    def executions_get(
        self,
        position_id: Optional[str] = None,
        search: Optional[str] = None,
        **kwargs,
    ) -> list[dict]:
        """_summary_

        Args:
            position_id (Optional[str], optional): _description_. Defaults to None.
            search (Optional[str], optional): _description_. Defaults to None.

        Returns:
            list[dict]: _description_
        """
        if position_id is not None:
            kwargs["position"] = int(position_id)
        if search is not None:
            kwargs["group"] = search

        raws = self._mt5.history_deals_get(**kwargs)

        if __debug__:
            logger.debug("Raw executions: %s", raws)

        return [self._execution_parse_response(raw) for raw in raws]

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
        if not raws:
            return

        if __debug__:
            logger.debug("Raw execution: %s", raws)

        return self._execution_parse_response(raws[0])

    def _execution_parse_response(self, raw):
        raw = Box(dict(raw._asdict()))
        return raw

    # Position
    def positions_total(
        self,
        since: Optional[datetime] = None,
        to: Optional[datetime] = None,
        **kwargs,
    ) -> int:
        """_summary_

        Args:
            since (Optional[datetime], optional): _description_. Defaults to None.
            to (Optional[datetime], optional): _description_. Defaults to None.

        Returns:
            int: _description_
        """
        if since is not None:
            kwargs["date_from"] = since
        if to is not None:
            kwargs["date_to"] = to

        return self._mt5.positions_total(**kwargs)

    def positions_get(self, id: str = None, symbol: str = None, **kwargs) -> list[dict]:
        """_summary_

        Args:
            id (str, optional): _description_. Defaults to None.
            symbol (str, optional): _description_. Defaults to None.

        Raises:
            RuntimeError: _description_

        Returns:
            list[dict]: _description_
        """
        if id is not None:
            kwargs.update(ticket=int(id))
        if symbol is not None:
            kwargs.update(symbol=symbol)

        raws = self._mt5.positions_get(**kwargs)
        if raws is None:
            raise RuntimeError(f"Cannot get position by parameters {kwargs}")

        return [Box(dict(raw._asdict())) for raw in raws]

    def position_update(
        self,
        position: LivePosition,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        **kwargs,
    ) -> dict:
        """_summary_

        Args:
            position (LivePosition): _description_
            sl (Optional[float], optional): _description_. Defaults to None.
            tp (Optional[float], optional): _description_. Defaults to None.

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

    def do_position_update(
        self,
        id: int,
        # symbol: str,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        **kwargs,
    ) -> dict:
        """_summary_

        Args:
            id (int): _description_
            sl (Optional[float], optional): _description_. Defaults to None.
            tp (Optional[float], optional): _description_. Defaults to None.

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
        return self._parse_trade_send_response(raw)

    def position_close(self, position: LivePosition, **kwargs) -> dict:
        """Close a position

        Args:
            position (LivePosition): _description_

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
        return self._parse_trade_send_response(raw)

    # Transaction
    def _load_history_transactions(self):
        to = datetime.now()  # + timedelta(days=1)

        # History orders
        orders = self._mt5.history_orders_get(self.__load_history_since, to)
        if orders:
            self._exchange.on_orders_old(orders)

        # # Positions
        # positions = self._mt5.positions_get(self.__load_history_since, to)
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
        if self._use_execution:
            deals = self._check_deals()
            if deals:
                self._exchange.on_deals_new(deals)

        # Orders
        orders, removed_orders = self._check_orders()
        if orders:
            self._exchange.on_orders_new(orders)
        if removed_orders:
            self._exchange.on_orders_old(removed_orders)

        # Positions
        positions, removed_positions = self._check_positions()
        if positions:
            self._exchange.on_positions_new(positions)
        if removed_positions:
            self._exchange.on_positions_old(removed_positions)

    # Deal
    def _check_deals(self):
        to = datetime.now()  # + timedelta(days=1)

        deal_total = self._mt5.history_deals_total(self.__deal_time_checked, to)
        if deal_total is None:
            return

        # No thing new in deal
        if deal_total <= 0:
            return

        raws = self._mt5.history_deals_get(self.__deal_time_checked, to)

        if raws:
            # Update last check time +1 second
            self.__deal_time_checked = datetime.fromtimestamp(raws[-1].time + 1)

        return raws

    # Order
    def _check_orders(self):
        order_total = self._mt5.orders_total()
        if order_total is None:
            return None, None

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
        if positions_total is None:
            return None, None

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
                    # and raw.price_open == stored.price_open
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
