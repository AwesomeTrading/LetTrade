import logging
from typing import Optional, Type

from mt5linux import MetaTrader5 as MT5

from lettrade import Commander, Statistic
from lettrade.exchange.live.base import (
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

logger = logging.getLogger(__name__)


class MetaTraderDataFeed(LiveDataFeed):
    """DataFeed for MetaTrader"""

    api_cls: Type[MetaTraderAPI] = MetaTraderAPI
    """API to communicate with MetaTrader Terminal"""


class MetaTraderDataFeeder(LiveDataFeeder):
    """DataFeeder for MetaTrader"""


class MetaTraderExecute(LiveExecute):
    """
    Execute for MetaTrader
    """


class MetaTraderOrder(LiveOrder):
    """Order for MetaTrader"""

    def _build_place_request(self):
        tick = self._api.tick_get(self.data.symbol)
        price = tick.ask if self.is_long else tick.bid
        type = MT5.ORDER_TYPE_BUY if self.is_long else MT5.ORDER_TYPE_SELL
        deviation = 20
        request = {
            "action": MT5.TRADE_ACTION_DEAL,
            "symbol": self.data.symbol,
            "volume": self.size,
            "type": type,
            "price": price,
            "sl": self.sl,
            "tp": self.tp,
            "deviation": deviation,
            "magic": 234000,
            "comment": self.tag,
            "type_time": MT5.ORDER_TIME_GTC,
            "type_filling": MT5.ORDER_FILLING_IOC,
        }
        return request


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
    plotter: Optional[Type["Plotter"]] = None,
    stats: Optional[Type[Statistic]] = Statistic,
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
        plotter (Optional[Type["Plotter"]], optional): _description_. Defaults to None.
        stats (Optional[Type[Statistic]], optional): _description_. Defaults to Statistic.
        bot (Optional[Type[LetTradeMetaTraderBot]], optional): _description_. Defaults to LetTradeMetaTraderBot.
        lettrade (Optional[Type[LetTradeMetaTrader]], optional): _description_. Defaults to LetTradeMetaTrader.
        api (Optional[Type[MetaTraderAPI]], optional): _description_. Defaults to MetaTraderAPI.
        wine (Optional[str], optional): _description_. Defaults to None.

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
