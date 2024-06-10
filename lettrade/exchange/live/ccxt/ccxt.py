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

from .api import CCXTAPI

# logger = logging.getLogger(__name__)


class CCXTDataFeed(LiveDataFeed):
    """DataFeed for CCXT"""

    _api_cls: Type[CCXTAPI] = CCXTAPI
    """API to communicate with CCXT Terminal"""


class CCXTDataFeeder(LiveDataFeeder):
    """DataFeeder for CCXT"""

    _api_cls: Type[CCXTAPI] = CCXTAPI
    """API to communicate with CCXT Terminal"""

    _data_cls: Type[CCXTDataFeed] = CCXTDataFeed
    """DataFeed for CCXT"""


class CCXTExecute(LiveExecute):
    """Execute for CCXT"""


class CCXTOrder(LiveOrder):
    """Order for CCXT"""


class CCXTTrade(LiveTrade):
    """Trade for CCXT"""


class CCXTAccount(LiveAccount):
    """Account for CCXT"""


class CCXTExchange(LiveExchange):
    """MetaTrade 5 exchange module for `lettrade`"""


class LetTradeCCXTBot(LetTradeLiveBot):
    """LetTradeBot for CCXT"""


class LetTradeCCXT(LetTradeLive):
    """Help to maintain CCXT bot"""

    _data_cls: Type[CCXTDataFeed] = CCXTDataFeed

    def __init__(
        self,
        feeder: Type[CCXTDataFeeder] = CCXTDataFeeder,
        exchange: Type[CCXTExchange] = CCXTExchange,
        account: Type[CCXTAccount] = CCXTAccount,
        **kwargs,
    ) -> None:
        """_summary_

        Args:
            feeder (Type[CCXTDataFeeder], optional): _description_. Defaults to CCXTDataFeeder.
            exchange (Type[CCXTExchange], optional): _description_. Defaults to CCXTExchange.
            account (Type[CCXTAccount], optional): _description_. Defaults to CCXTAccount.
        """
        super().__init__(
            feeder=feeder,
            exchange=exchange,
            account=account,
            **kwargs,
        )


def let_ccxt(
    strategy: Type[Strategy],
    datas: set[set[str]],
    ccxt_exchange: str,
    ccxt_key: str,
    ccxt_secret: str,
    feeder: Type[CCXTDataFeeder] = CCXTDataFeeder,
    exchange: Type[CCXTExchange] = CCXTExchange,
    account: Type[CCXTAccount] = CCXTAccount,
    commander: Optional[Type[Commander]] = None,
    plotter: Optional[Type[Plotter]] = None,
    stats: Optional[Type[BotStatistic]] = BotStatistic,
    lettrade: Optional[Type[LetTradeCCXT]] = LetTradeCCXT,
    bot: Optional[Type[LetTradeCCXTBot]] = LetTradeCCXTBot,
    api: Optional[Type[CCXTAPI]] = CCXTAPI,
    **kwargs,
) -> LetTradeCCXT:
    """Help to build `LetTradeCCXT`

    Args:
        strategy (Type[Strategy]): _description_
        datas (set[set[str]]): _description_
        ccxt_exchange (str): _description_
        ccxt_key (str): _description_
        ccxt_secret (str): _description_
        feeder (Type[CCXTDataFeeder], optional): _description_. Defaults to CCXTDataFeeder.
        exchange (Type[CCXTExchange], optional): _description_. Defaults to CCXTExchange.
        account (Type[CCXTAccount], optional): _description_. Defaults to CCXTAccount.
        commander (Optional[Type[Commander]], optional): _description_. Defaults to None.
        plotter (Optional[Type[Plotter]], optional): _description_. Defaults to None.
        stats (Optional[Type[BotStatistic]], optional): _description_. Defaults to BotStatistic.
        lettrade (Optional[Type[LetTradeCCXT]], optional): _description_. Defaults to LetTradeCCXT.
        bot (Optional[Type[LetTradeCCXTBot]], optional): _description_. Defaults to LetTradeCCXTBot.
        api (Optional[Type[CCXTAPI]], optional): _description_. Defaults to CCXTAPI.

    Returns:
        LetTradeCCXT: _description_
    """
    api_kwargs: dict = kwargs.setdefault("api_kwargs", {})
    api_kwargs.update(
        exchange=ccxt_exchange,
        key=ccxt_key,
        secret=ccxt_secret,
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
        lettrade=lettrade,
        bot=bot,
        api=api,
        **kwargs,
    )
