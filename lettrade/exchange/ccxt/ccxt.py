import logging
from typing import Literal, Optional, Type

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
from lettrade.exchange.live.api import LiveAPI

from .api import CCXTAPI
from .trade import CCXTExecution, CCXTOrder, CCXTPosition

logger = logging.getLogger(__name__)


class CCXTDataFeed(LiveDataFeed):
    """DataFeed for CCXT"""

    _api_cls: Type[CCXTAPI] = CCXTAPI


class CCXTDataFeeder(LiveDataFeeder):
    """DataFeeder for CCXT"""

    _api_cls: Type[CCXTAPI] = CCXTAPI
    _data_cls: Type[CCXTDataFeed] = CCXTDataFeed


class CCXTAccount(LiveAccount):
    """Account for CCXT"""

    _currency: str

    def __init__(self, api: LiveAPI, currency: str = "USDT", **kwargs) -> None:
        super().__init__(api, **kwargs)
        self._currency = currency


class CCXTExchange(LiveExchange):
    """MetaTrade 5 exchange module for `lettrade`"""

    _execution_cls: Type[CCXTExecution] = CCXTExecution
    _order_cls: Type[CCXTOrder] = CCXTOrder
    _position_cls: Type[CCXTPosition] = CCXTPosition


class LetTradeCCXTBot(LetTradeLiveBot):
    """LetTradeBot for CCXT"""


class LetTradeCCXT(LetTradeLive):
    """Help to maintain CCXT bots"""

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
    ccxt_type: Literal["spot", "margin", "future"] = "spot",
    ccxt_verbose: bool = False,
    feeder: Type[CCXTDataFeeder] = CCXTDataFeeder,
    exchange: Type[CCXTExchange] = CCXTExchange,
    account: Type[CCXTAccount] = CCXTAccount,
    commander: Optional[Type[Commander]] = None,
    plotter: Optional[Type[Plotter]] = None,
    stats: Optional[Type[BotStatistic]] = BotStatistic,
    bot: Optional[Type[LetTradeCCXTBot]] = LetTradeCCXTBot,
    lettrade: Optional[Type[LetTradeCCXT]] = LetTradeCCXT,
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
        ccxt_type (Literal["spot", "margin", "future"], optional): _description_. Defaults to "spot".
        ccxt_verbose (bool, optional): _description_. Defaults to False.
        feeder (Type[CCXTDataFeeder], optional): _description_. Defaults to CCXTDataFeeder.
        exchange (Type[CCXTExchange], optional): _description_. Defaults to CCXTExchange.
        account (Type[CCXTAccount], optional): _description_. Defaults to CCXTAccount.
        commander (Optional[Type[Commander]], optional): _description_. Defaults to None.
        plotter (Optional[Type[Plotter]], optional): _description_. Defaults to None.
        stats (Optional[Type[BotStatistic]], optional): _description_. Defaults to BotStatistic.
        bot (Optional[Type[LetTradeCCXTBot]], optional): _description_. Defaults to LetTradeCCXTBot.
        lettrade (Optional[Type[LetTradeCCXT]], optional): _description_. Defaults to LetTradeCCXT.
        api (Optional[Type[CCXTAPI]], optional): _description_. Defaults to CCXTAPI.
        **kwargs (dict): All remaining properties are passed to the constructor of `LetTradeLive`

    Returns:
        LetTradeCCXT: _description_
    """
    api_kwargs: dict = kwargs.setdefault("api_kwargs", {})
    api_kwargs.update(
        exchange=ccxt_exchange,
        key=ccxt_key,
        secret=ccxt_secret,
        type=ccxt_type,
        verbose=ccxt_verbose,
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
