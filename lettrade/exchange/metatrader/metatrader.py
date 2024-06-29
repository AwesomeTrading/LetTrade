import logging

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

    _api_cls: type[MetaTraderAPI] = MetaTraderAPI
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

    _api_cls: type[MetaTraderAPI] = MetaTraderAPI
    _data_cls: type[MetaTraderDataFeed] = MetaTraderDataFeed


class MetaTraderAccount(LiveAccount):
    """Account for MetaTrader"""


class MetaTraderExchange(LiveExchange):
    """MetaTrade 5 exchange module for `lettrade`"""

    _execution_cls: type[MetaTraderExecution] = MetaTraderExecution
    _order_cls: type[MetaTraderOrder] = MetaTraderOrder
    _position_cls: type[MetaTraderPosition] = MetaTraderPosition

    def on_order(
        self,
        order: MetaTraderOrder,
        broadcast: bool | None = True,
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

    _data_cls: type[MetaTraderDataFeed] = MetaTraderDataFeed

    def __init__(
        self,
        feeder: type[MetaTraderDataFeeder] = MetaTraderDataFeeder,
        exchange: type[MetaTraderExchange] = MetaTraderExchange,
        account: type[MetaTraderAccount] = MetaTraderAccount,
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
    datas: set[set[str]],
    strategy: type[Strategy],
    *,
    mt5_login: int,
    mt5_password: str,
    mt5_server: str,
    mt5_wine: str | None = None,
    feeder: type[MetaTraderDataFeeder] = MetaTraderDataFeeder,
    exchange: type[MetaTraderExchange] = MetaTraderExchange,
    account: type[MetaTraderAccount] = MetaTraderAccount,
    commander: type[Commander] | None = None,
    stats: type[BotStatistic] = BotStatistic,
    plotter: type[Plotter] | None = None,
    bot: type[LetTradeMetaTraderBot] = LetTradeMetaTraderBot,
    lettrade: type[LetTradeMetaTrader] = LetTradeMetaTrader,
    api: type[MetaTraderAPI] = MetaTraderAPI,
    **kwargs,
) -> LetTradeMetaTrader:
    """Help to build `LetTradeMetaTrader`

    Args:
        datas (set[set[str]]): _description_
        strategy (type[Strategy]): _description_
        mt5_login (int): _description_
        mt5_password (str): _description_
        mt5_server (str): _description_
        mt5_wine (str | None, optional): WineHQ execute path. Defaults to None.
        feeder (type[MetaTraderDataFeeder], optional): _description_. Defaults to MetaTraderDataFeeder.
        exchange (type[MetaTraderExchange], optional): _description_. Defaults to MetaTraderExchange.
        account (type[MetaTraderAccount], optional): _description_. Defaults to MetaTraderAccount.
        commander (type[Commander] | None, optional): _description_. Defaults to None.
        stats (type[BotStatistic], optional): _description_. Defaults to BotStatistic.
        plotter (type[Plotter] | None, optional): _description_. Defaults to None.
        bot (type[LetTradeMetaTraderBot], optional): _description_. Defaults to LetTradeMetaTraderBot.
        lettrade (type[LetTradeMetaTrader], optional): _description_. Defaults to LetTradeMetaTrader.
        api (type[MetaTraderAPI], optional): _description_. Defaults to MetaTraderAPI.

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
        stats=stats,
        plotter=plotter,
        bot=bot,
        lettrade=lettrade,
        api=api,
        **kwargs,
    )
