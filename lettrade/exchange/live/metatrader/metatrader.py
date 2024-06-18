import logging
from typing import Optional, Type

import pandas as pd
from mt5linux import MetaTrader5 as MT5

from lettrade import (
    BotStatistic,
    Commander,
    OrderState,
    OrderType,
    Plotter,
    PositionState,
    TradeSide,
)
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


class MetaTraderOrder(LiveOrder):
    """Order for MetaTrader"""

    @classmethod
    def from_raw(
        cls, raw, exchange: "MetaTraderExchange"
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
            size=side * raw.volume_current,
            type=type,
            limit_price=limit_price,
            stop_price=stop_price,
            sl_price=raw.sl,
            tp_price=raw.tp,
            tag=raw.comment,
            raw=raw,
        )
        order.place_at = pd.to_datetime(raw.time_setup_msc, unit="ms")
        return order

    @classmethod
    def from_position(cls, position: "MetaTraderPosition", sl=None, tp=None):
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
        )


class MetaTraderPosition(LivePosition):
    """Position for MetaTrader"""

    @classmethod
    def from_raw(cls, raw, exchange: "MetaTraderExchange") -> "MetaTraderPosition":
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
        data = None
        for d in exchange.datas:
            if d.symbol == raw.symbol:
                data = d
                break
        if data is None:
            logger.warning("Raw order %s is not handling %s", raw.symbol, raw)
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
            parent=None,
            tag=raw.comment,
            raw=raw,
        )
        position.entry_at = pd.to_datetime(raw.time_msc, unit="ms")

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
    login: int,
    password: str,
    server: str,
    feeder: Type[MetaTraderDataFeeder] = MetaTraderDataFeeder,
    exchange: Type[MetaTraderExchange] = MetaTraderExchange,
    account: Type[MetaTraderAccount] = MetaTraderAccount,
    commander: Optional[Type[Commander]] = None,
    plotter: Optional[Type[Plotter]] = None,
    stats: Optional[Type[BotStatistic]] = BotStatistic,
    bot: Optional[Type[LetTradeMetaTraderBot]] = LetTradeMetaTraderBot,
    lettrade: Optional[Type[LetTradeMetaTrader]] = LetTradeMetaTrader,
    api: Optional[Type[MetaTraderAPI]] = MetaTraderAPI,
    wine: Optional[str] = None,
    **kwargs,
) -> LetTradeMetaTrader:
    """Help to build `LetTradeMetaTrader`

    Args:
        strategy (Type[Strategy]): _description_
        datas (set[set[str]]): _description_
        login (int): _description_
        password (str): _description_
        server (str): _description_
        feeder (Type[MetaTraderDataFeeder], optional): _description_. Defaults to MetaTraderDataFeeder.
        exchange (Type[MetaTraderExchange], optional): _description_. Defaults to MetaTraderExchange.
        account (Type[MetaTraderAccount], optional): _description_. Defaults to MetaTraderAccount.
        commander (Optional[Type[Commander]], optional): _description_. Defaults to None.
        plotter (Optional[Type[Plotter]], optional): _description_. Defaults to None.
        stats (Optional[Type[BotStatistic]], optional): _description_. Defaults to BotStatistic.
        bot (Optional[Type[LetTradeMetaTraderBot]], optional): _description_. Defaults to LetTradeMetaTraderBot.
        lettrade (Optional[Type[LetTradeMetaTrader]], optional): _description_. Defaults to LetTradeMetaTrader.
        api (Optional[Type[MetaTraderAPI]], optional): _description_. Defaults to MetaTraderAPI.
        wine (Optional[str], optional): _description_. Defaults to None.
        **kwargs (dict): All remaining properties are passed to the constructor of `LetTradeLive`

    Returns:
        LetTradeMetaTrader: _description_
    """
    api_kwargs: dict = kwargs.setdefault("api_kwargs", {})
    api_kwargs.update(
        login=int(login),
        password=password,
        server=server,
        wine=wine,
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
