# import logging
from typing import Optional, Type

from lettrade import BotStatistic, Commander, Plotter
from lettrade.exchange.live import (
    LetTradeLive,
    LetTradeLiveBot,
    LiveAccount,
    LiveDataFeed,
    LiveDataFeeder,
    LiveExchange,
    LiveExecute,
    LiveOrder,
    LiveTrade,
    let_live,
)
from lettrade.strategy.strategy import Strategy

from .api import MetaTraderAPI

# import numpy as np
# import pandas as pd


# logger = logging.getLogger(__name__)


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


class MetaTraderExecute(LiveExecute):
    """Execute for MetaTrader"""


class MetaTraderOrder(LiveOrder):
    """Order for MetaTrader"""


class MetaTraderTrade(LiveTrade):
    """Trade for MetaTrader"""


class MetaTraderAccount(LiveAccount):
    """Account for MetaTrader"""


class MetaTraderExchange(LiveExchange):
    """MetaTrade 5 exchange module for `lettrade`"""


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
