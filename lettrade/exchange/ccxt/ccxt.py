import logging
from typing import Literal

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

    _api_cls: type[CCXTAPI] = CCXTAPI


class CCXTDataFeeder(LiveDataFeeder):
    """DataFeeder for CCXT"""

    _api_cls: type[CCXTAPI] = CCXTAPI
    _data_cls: type[CCXTDataFeed] = CCXTDataFeed


class CCXTAccount(LiveAccount):
    """Account for CCXT"""

    _currency: str

    def __init__(self, api: LiveAPI, currency: str = "USDT", **kwargs) -> None:
        super().__init__(api, **kwargs)
        self._currency = currency


class CCXTExchange(LiveExchange):
    """MetaTrade 5 exchange module for `lettrade`"""

    _execution_cls: type[CCXTExecution] = CCXTExecution
    _order_cls: type[CCXTOrder] = CCXTOrder
    _position_cls: type[CCXTPosition] = CCXTPosition


class LetTradeCCXTBot(LetTradeLiveBot):
    """LetTradeBot for CCXT"""


class LetTradeCCXT(LetTradeLive):
    """Help to maintain CCXT bots"""

    _data_cls: type[CCXTDataFeed] = CCXTDataFeed

    def __init__(
        self,
        feeder: type[CCXTDataFeeder] = CCXTDataFeeder,
        exchange: type[CCXTExchange] = CCXTExchange,
        account: type[CCXTAccount] = CCXTAccount,
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
    datas: set[set[str]],
    strategy: type[Strategy],
    *,
    ccxt_exchange: str,
    ccxt_key: str,
    ccxt_secret: str,
    ccxt_type: Literal["spot", "margin", "future"] = "spot",
    ccxt_verbose: bool = False,
    feeder: type[CCXTDataFeeder] = CCXTDataFeeder,
    exchange: type[CCXTExchange] = CCXTExchange,
    account: type[CCXTAccount] = CCXTAccount,
    commander: type[Commander] | None = None,
    stats: type[BotStatistic] | None = BotStatistic,
    plotter: type[Plotter] | None = None,
    bot: type[LetTradeCCXTBot] | None = LetTradeCCXTBot,
    lettrade: type[LetTradeCCXT] | None = LetTradeCCXT,
    api: type[CCXTAPI] | None = CCXTAPI,
    **kwargs,
) -> LetTradeCCXT:
    """Help to build `LetTradeCCXT`

    Args:
        datas (set[set[str]]): _description_
        strategy (Type[Strategy]): _description_
        ccxt_exchange (str): _description_
        ccxt_key (str): _description_
        ccxt_secret (str): _description_
        ccxt_type (Literal["spot", "margin", "future"], optional): _description_. Defaults to "spot".
        ccxt_verbose (bool, optional): _description_. Defaults to False.
        feeder (Type[CCXTDataFeeder], optional): _description_. Defaults to CCXTDataFeeder.
        exchange (Type[CCXTExchange], optional): _description_. Defaults to CCXTExchange.
        account (Type[CCXTAccount], optional): _description_. Defaults to CCXTAccount.
        commander (Type[Commander] | None, optional): _description_. Defaults to None.
        stats (Type[BotStatistic] | None, optional): _description_. Defaults to BotStatistic.
        plotter (Type[Plotter] | None, optional): _description_. Defaults to None.
        bot (Type[LetTradeCCXTBot] | None, optional): _description_. Defaults to LetTradeCCXTBot.
        lettrade (Type[LetTradeCCXT] | None, optional): _description_. Defaults to LetTradeCCXT.
        api (Type[CCXTAPI] | None, optional): _description_. Defaults to CCXTAPI.
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
