import logging
from typing import Optional, Type

import pandas as pd
from mt5linux import MetaTrader5 as MT5

from lettrade import (
    BotStatistic,
    Commander,
    Order,
    OrderResult,
    OrderResultError,
    OrderState,
    OrderType,
    Plotter,
    PositionResultError,
    PositionState,
    TradeSide,
)
from lettrade.exchange import PositionResult
from lettrade.exchange.live import (
    LetTradeLive,
    LetTradeLiveBot,
    LiveAccount,
    LiveDataFeed,
    LiveDataFeeder,
    LiveExchange,
    LiveExecution,
    LiveOrder,
    LivePosition,
    let_live,
)
from lettrade.strategy.strategy import Strategy

from .api import MetaTraderAPI

logger = logging.getLogger(__name__)


class MetaTraderDataFeed(LiveDataFeed):
    """DataFeed for MetaTrader"""

    _api_cls: Type[MetaTraderAPI] = MetaTraderAPI
    """API to communicate with MetaTrader Terminal"""

    # def push(self, rows: list):
    #     if isinstance(rows, np.ndarray):
    #         df = pd.DataFrame(
    #             rows,
    #             columns=[
    #                 "time",
    #                 "open",
    #                 "high",
    #                 "low",
    #                 "close",
    #                 "tick_volume",
    #             ],
    #         )
    #         df.rename(
    #             columns={
    #                 "time": "datetime",
    #                 "tick_volume": "volume",
    #             },
    #             inplace=True,
    #         )
    #         df["datetime"] = pd.to_datetime(df["datetime"], unit="s")
    #         df.set_index("datetime", inplace=True)
    #         print(df, df.dtypes)

    #     return super().push(df)


class MetaTraderDataFeeder(LiveDataFeeder):
    """DataFeeder for MetaTrader"""

    _api_cls: Type[MetaTraderAPI] = MetaTraderAPI
    """API to communicate with MetaTrader Terminal"""

    _data_cls: Type[MetaTraderDataFeed] = MetaTraderDataFeed
    """DataFeed for MetaTrader"""


class MetaTraderExecution(LiveExecution):
    """Execution for MetaTrader"""

    @classmethod
    def from_raw(
        cls,
        raw,
        exchange: "MetaTraderExchange",
        api: MetaTraderAPI = None,
    ) -> "MetaTraderExecution":
        """Building new MetaTraderExecution from live api raw object

        Args:
            raw (_type_): _description_
            exchange (MetaTraderExchange): _description_

        Returns:
            MetaTraderExecution: _description_
        """

        return cls(
            exchange=exchange,
            id=raw.ticket,
            # TODO: Fix by get data from symbol
            data=exchange.data,
            # TODO: size and type from raw.type
            size=raw.volume,
            price=raw.price,
            # TODO: set bar time
            at=None,
            order_id=raw.order,
            position_id=raw.position_id,
            tag=raw.comment,
            api=api,
            raw=raw,
        )


class MetaTraderOrder(LiveOrder):
    """Order for MetaTrader"""

    exchange: "MetaTraderExchange"

    def place(self) -> OrderResult:
        if self.state != OrderState.Pending:
            raise RuntimeError(f"Order {self.id} state {self.state} is not Pending")

        result = self._api.order_open(self)
        self.raw = result
        if result.code != 0:
            logger.error("Place order %s", str(result))
            error = OrderResultError(
                error=result.error,
                code=result.code,
                order=self,
                raw=result,
            )
            self.exchange.on_notify(error=error)
            return error

        self.id = result.order
        # TODO: get current order time
        return super(LiveOrder, self).place(at=self.data.l.index[0], raw=result)

    def update(
        self,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        caller: Optional[float] = None,
        **kwargs,
    ) -> OrderResult:
        if caller is self:
            raise RuntimeError(f"Order recusive update {self}")

        if self.parent is None:
            result = self._api.order_update(
                order=self,
                limit_price=limit_price,
                stop_price=stop_price,
                sl=sl,
                tp=tp,
                **kwargs,
            )
            return super(LiveOrder, self).update(
                limit_price=result.limit_price,
                stop_price=result.stop_price,
                sl=result.sl,
                tp=result.tp,
            )
        else:
            # SL/TP Order just a virtual order
            if caller is not self.parent:
                if self.is_sl_order:
                    self.parent.update(sl=stop_price, caller=self)
                elif self.is_tp_order:
                    self.parent.update(tp=limit_price, caller=self)
                else:
                    raise RuntimeError(f"Abandon order {self}")

            return super(LiveOrder, self).update(
                limit_price=limit_price,
                stop_price=stop_price,
            )

    @classmethod
    def from_raw(
        cls,
        raw,
        exchange: "MetaTraderExchange",
        api: MetaTraderAPI = None,
    ) -> Optional["MetaTraderOrder"]:
        """_summary_

        Raises:
            NotImplementedError: _description_
            NotImplementedError: _description_

        Returns:
            _type_: _description_
        """
        # DataFeed
        data = None
        for d in exchange.datas:
            if d.symbol == raw.symbol:
                data = d
                break
        if data is None:
            logger.warning("Raw order %s is not handling %s", raw.symbol, raw)
            return

        # Prices & Side & Type
        limit_price = None
        stop_price = None
        match raw.type:
            case MT5.ORDER_TYPE_BUY:
                side = TradeSide.Buy
                type = OrderType.Market
            case MT5.ORDER_TYPE_SELL:
                side = TradeSide.Sell
                type = OrderType.Market
            case MT5.ORDER_TYPE_BUY_LIMIT:
                side = TradeSide.Buy
                type = OrderType.Limit
                limit_price = raw.price_open
            case MT5.ORDER_TYPE_SELL_LIMIT:
                side = TradeSide.Sell
                type = OrderType.Limit
                limit_price = raw.price_open
            case MT5.ORDER_TYPE_BUY_STOP:
                side = TradeSide.Buy
                type = OrderType.Stop
                stop_price = raw.price_open
            case MT5.ORDER_TYPE_SELL_STOP:
                side = TradeSide.Sell
                type = OrderType.Stop
                stop_price = raw.price_open
            # case MT5.ORDER_TYPE_BUY_STOP_LIMIT:
            #     side = TradeSide.Buy
            #     type = OrderType.StopLimit
            #     # TODO
            #     limit_price = raw.price_open
            #     stop_price = raw.price_open
            # case MT5.ORDER_TYPE_SELL_STOP_LIMIT:
            #     side = TradeSide.Sell
            #     type = OrderType.StopLimit
            #     # TODO
            #     limit_price = raw.price_open
            #     stop_price = raw.price_open
            # case MT5.ORDER_TYPE_CLOSE_BY:
            case _:
                raise NotImplementedError(
                    f"Order type {raw.type} is not implement",
                    raw,
                )
        # State
        match raw.state:
            case MT5.ORDER_STATE_STARTED:
                state = OrderState.Pending
            case MT5.ORDER_STATE_PLACED:
                state = OrderState.Placed
            case MT5.ORDER_STATE_CANCELED:
                state = OrderState.Canceled
            case MT5.ORDER_STATE_PARTIAL:
                state = OrderState.Partial
            case MT5.ORDER_STATE_FILLED:
                state = OrderState.Filled
            case MT5.ORDER_STATE_REJECTED:
                state = OrderState.Canceled
            case MT5.ORDER_STATE_EXPIRED:
                state = OrderState.Canceled
            case MT5.ORDER_STATE_REQUEST_ADD:
                state = OrderState.Placed
            case MT5.ORDER_STATE_REQUEST_MODIFY:
                state = OrderState.Placed
            case MT5.ORDER_STATE_REQUEST_CANCEL:
                state = OrderState.Canceled
            case _:
                raise NotImplementedError(
                    f"Raw order state {raw.state} is not implement"
                )

        order = cls(
            exchange=exchange,
            id=raw.ticket,
            state=state,
            data=data,
            size=side * (raw.volume_current or raw.volume_initial),
            type=type,
            limit_price=limit_price,
            stop_price=stop_price,
            sl_price=raw.sl or None,
            tp_price=raw.tp or None,
            tag=raw.comment,
            placed_at=pd.to_datetime(raw.time_setup_msc, unit="ms", utc=True),
            api=api,
            raw=raw,
        )

        if hasattr(raw, "time_done_msc"):
            order.filled_price = raw.price_current
            order.filled_at = pd.to_datetime(raw.time_done_msc, unit="ms", utc=True)

        return order

    @classmethod
    def from_position(
        cls, position: "MetaTraderPosition", sl=None, tp=None
    ) -> "MetaTraderOrder":
        """_summary_

        Args:
            position (MetaTraderPosition): _description_
            sl (_type_, optional): _description_. Defaults to None.
            tp (_type_, optional): _description_. Defaults to None.

        Raises:
            RuntimeError: _description_

        Returns:
            _type_: _description_
        """
        if not sl and not tp:
            raise RuntimeError("not sl and not tp")
        return cls(
            id=f"{position.id}-{'sl' if sl else 'tp'}",
            exchange=position.exchange,
            data=position.data,
            state=OrderState.Placed,
            type=OrderType.Stop if sl else OrderType.Limit,
            size=-position.size,
            limit_price=tp,
            stop_price=sl,
            parent=position,
            placed_at=position.entry_at,
        )


class MetaTraderPosition(LivePosition):
    """Position for MetaTrader"""

    exchange: "MetaTraderExchange"

    def update(
        self,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        caller: Optional[float] = None,
        **kwargs,
    ):
        if not sl and not tp:
            raise RuntimeError("Update sl=None and tp=None")
        if caller is self:
            raise RuntimeError(f"Position recusive update {self}")

        result = self._api.position_update(position=self, sl=sl, tp=tp)
        if result.code != 0:
            logger.error("Update position %s", str(result))
            error = PositionResultError(
                error=result.error,
                code=result.code,
                position=self,
                raw=result,
            )
            self.exchange.on_notify(error=error)
            return error

        if sl is not None:
            if self.sl_order:
                if caller is not self.sl_order:
                    self.sl_order.update(stop_price=sl, caller=self)
            else:
                self.sl_order = self.exchange._order_cls.from_position(
                    position=self, sl=sl
                )

        if tp is not None:
            if self.tp_order:
                if caller is not self.tp_order:
                    self.tp_order.update(limit_price=tp, caller=self)
            else:
                self.tp_order = self.exchange._order_cls.from_position(
                    position=self, tp=tp
                )

        return super(LivePosition, self).update(raw=result)

    def exit(self) -> PositionResult:
        result = self._api.position_close(position=self)
        if result.code != 0:
            logger.error("Update position %s", str(result))
            error = PositionResultError(
                error=result.error,
                code=result.code,
                position=self,
                raw=result,
            )
            self.exchange.on_notify(error=error)
            return error

        execution_raw = self._api.executions_get(id=result.execution_id)
        # TODO: execution object and event
        result.execution_raw = execution_raw

        return super(LivePosition, self).exit(
            price=result.price,
            at=pd.to_datetime(execution_raw.time_msc, unit="ms", utc=True),
            pl=result.profit,
            fee=execution_raw.fee + execution_raw.swap + execution_raw.commission,
            raw=result,
        )

    @classmethod
    def from_raw(
        cls,
        raw,
        exchange: "MetaTraderExchange",
        data: MetaTraderDataFeed = None,
        api: MetaTraderAPI = None,
    ) -> "MetaTraderPosition":
        """_summary_

        Args:
            raw (_type_): _description_
            exchange (MetaTraderExchange): _description_

        Raises:
            NotImplementedError: _description_

        Returns:
            MetaTraderPosition: _description_
        """
        # DataFeed
        if data is None:
            for d in exchange.datas:
                if d.symbol == raw.symbol:
                    data = d
                    break
            if data is None:
                logger.warning("Raw position %s is not handling %s", raw.symbol, raw)
                return

        # Side
        match raw.type:
            case MT5.POSITION_TYPE_BUY:
                side = TradeSide.Buy
            case MT5.POSITION_TYPE_SELL:
                side = TradeSide.Sell
            case _:
                raise NotImplementedError(
                    f"Position type {raw.type} is not implement",
                    raw,
                )

        position = cls(
            exchange=exchange,
            id=raw.ticket,
            data=data,
            state=PositionState.Open,
            size=side * raw.volume,
            entry_price=raw.price_open,
            entry_fee=raw.swap,
            entry_at=pd.to_datetime(raw.time_msc, unit="ms", utc=True),
            parent=None,
            tag=raw.comment,
            api=api,
            raw=raw,
        )

        # SL
        if raw.sl > 0.0:
            position.sl_order = exchange._order_cls.from_position(
                position=position, sl=raw.sl
            )
            exchange.on_order(position.sl_order)

        # TP
        if raw.tp > 0.0:
            position.tp_order = exchange._order_cls.from_position(
                position=position, tp=raw.tp
            )
            exchange.on_order(position.tp_order)

        return position

    # @classmethod
    # def from_id(
    #     cls,
    #     id: str,
    #     exchange: "MetaTraderExchange",
    #     data: MetaTraderDataFeed = None,
    #     api: MetaTraderAPI = None,
    # ) -> "MetaTraderPosition":
    #     if api is None:
    #         api = exchange._api

    #     raws = api.positions_get(id=id)
    #     return cls.from_raw(
    #         raw=raws[0],
    #         exchange=exchange,
    #         data=data,
    #         api=api,
    #     )


class MetaTraderAccount(LiveAccount):
    """Account for MetaTrader"""


class MetaTraderExchange(LiveExchange):
    """MetaTrade 5 exchange module for `lettrade`"""

    _execution_cls: Type[MetaTraderExecution] = MetaTraderExecution
    _order_cls: Type[MetaTraderOrder] = MetaTraderOrder
    _position_cls: Type[MetaTraderPosition] = MetaTraderPosition


class LetTradeMetaTraderBot(LetTradeLiveBot):
    """LetTradeBot for MetaTrader"""


class LetTradeMetaTrader(LetTradeLive):
    """Help to maintain MetaTrader bots"""

    _data_cls: Type[MetaTraderDataFeed] = MetaTraderDataFeed

    def __init__(
        self,
        feeder: Type[MetaTraderDataFeeder] = MetaTraderDataFeeder,
        exchange: Type[MetaTraderExchange] = MetaTraderExchange,
        account: Type[MetaTraderAccount] = MetaTraderAccount,
        **kwargs,
    ) -> None:
        """_summary_

        Args:
            feeder (Type[MetaTraderDataFeeder], optional): _description_. Defaults to MetaTraderDataFeeder.
            exchange (Type[MetaTraderExchange], optional): _description_. Defaults to MetaTraderExchange.
            account (Type[MetaTraderAccount], optional): _description_. Defaults to MetaTraderAccount.
        """
        super().__init__(
            feeder=feeder,
            exchange=exchange,
            account=account,
            **kwargs,
        )


def let_metatrader(
    strategy: Type[Strategy],
    datas: set[set[str]],
    mt5_login: int,
    mt5_password: str,
    mt5_server: str,
    mt5_wine: Optional[str] = None,
    feeder: Type[MetaTraderDataFeeder] = MetaTraderDataFeeder,
    exchange: Type[MetaTraderExchange] = MetaTraderExchange,
    account: Type[MetaTraderAccount] = MetaTraderAccount,
    commander: Optional[Type[Commander]] = None,
    plotter: Optional[Type[Plotter]] = None,
    stats: Optional[Type[BotStatistic]] = BotStatistic,
    bot: Optional[Type[LetTradeMetaTraderBot]] = LetTradeMetaTraderBot,
    lettrade: Optional[Type[LetTradeMetaTrader]] = LetTradeMetaTrader,
    api: Optional[Type[MetaTraderAPI]] = MetaTraderAPI,
    **kwargs,
) -> LetTradeMetaTrader:
    """Help to build `LetTradeMetaTrader`

    Args:
        strategy (Type[Strategy]): _description_
        datas (set[set[str]]): _description_
        mt5_login (int): _description_
        mt5_password (str): _description_
        mt5_server (str): _description_
        mt5_wine (Optional[str], optional): WineHQ execute path. Defaults to None.
        feeder (Type[MetaTraderDataFeeder], optional): _description_. Defaults to MetaTraderDataFeeder.
        exchange (Type[MetaTraderExchange], optional): _description_. Defaults to MetaTraderExchange.
        account (Type[MetaTraderAccount], optional): _description_. Defaults to MetaTraderAccount.
        commander (Optional[Type[Commander]], optional): _description_. Defaults to None.
        plotter (Optional[Type[Plotter]], optional): _description_. Defaults to None.
        stats (Optional[Type[BotStatistic]], optional): _description_. Defaults to BotStatistic.
        bot (Optional[Type[LetTradeMetaTraderBot]], optional): _description_. Defaults to LetTradeMetaTraderBot.
        lettrade (Optional[Type[LetTradeMetaTrader]], optional): _description_. Defaults to LetTradeMetaTrader.
        api (Optional[Type[MetaTraderAPI]], optional): _description_. Defaults to MetaTraderAPI.
        **kwargs (dict): All remaining properties are passed to the constructor of `LetTradeLive`

    Returns:
        LetTradeMetaTrader: _description_
    """
    api_kwargs: dict = kwargs.setdefault("api_kwargs", {})
    api_kwargs.update(
        login=int(mt5_login),
        password=mt5_password,
        server=mt5_server,
        wine=mt5_wine,
    )

    return let_live(
        strategy=strategy,
        datas=datas,
        feeder=feeder,
        exchange=exchange,
        account=account,
        commander=commander,
        plotter=plotter,
        stats=stats,
        bot=bot,
        lettrade=lettrade,
        api=api,
        **kwargs,
    )
