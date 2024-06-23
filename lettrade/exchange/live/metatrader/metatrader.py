import logging
from typing import Optional, Type

from lettrade import BotStatistic, Commander, Plotter, Strategy
from lettrade.exchange.live import (
    LetTradeLive,
    LetTradeLiveBot,
    LiveAccount,
    LiveDataFeed,
    LiveDataFeeder,
    LiveExchange,
    let_live,
)

from .api import MetaTraderAPI
from .trade import MetaTraderExecution, MetaTraderOrder, MetaTraderPosition

logger = logging.getLogger(__name__)


class MetaTraderDataFeed(LiveDataFeed):
    """DataFeed for MetaTrader"""

    _api_cls: Type[MetaTraderAPI] = MetaTraderAPI
    _bar_datetime_unit: str = "s"

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
    _data_cls: Type[MetaTraderDataFeed] = MetaTraderDataFeed


class MetaTraderAccount(LiveAccount):
    """Account for MetaTrader"""


class MetaTraderExchange(LiveExchange):
    """MetaTrade 5 exchange module for `lettrade`"""

    _execution_cls: Type[MetaTraderExecution] = MetaTraderExecution
    _order_cls: Type[MetaTraderOrder] = MetaTraderOrder
    _position_cls: Type[MetaTraderPosition] = MetaTraderPosition

    def on_order(
        self,
        order: MetaTraderOrder,
        broadcast: Optional[bool] = True,
        **kwargs,
    ) -> None:
        if not order.is_real:
            if order.id in self.history_orders:
                del self.history_orders[order.id]

        return super().on_order(order=order, broadcast=broadcast, **kwargs)


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
