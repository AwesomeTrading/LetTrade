import logging
from typing import Optional, Type

from mt5linux import MetaTrader5 as mt5

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
    """"""


class MetaTraderDataFeeder(LiveDataFeeder):
    """"""


class MetaTraderExecute(LiveExecute):
    """
    Execute for MetaTrader
    """


class MetaTraderOrder(LiveOrder):
    """"""

    def _build_place_request(self):
        tick = self._api.tick_get(self.data.symbol)
        price = tick.ask if self.is_long else tick.bid
        type = mt5.ORDER_TYPE_BUY if self.is_long else mt5.ORDER_TYPE_SELL
        deviation = 20
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.data.symbol,
            "volume": self.size,
            "type": type,
            "price": price,
            "sl": self.sl,
            "tp": self.tp,
            "deviation": deviation,
            "magic": 234000,
            "comment": self.tag,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        return request


class MetaTraderTrade(LiveTrade):
    """"""


class MetaTraderAccount(LiveAccount):
    """"""


class MetaTraderExchange(LiveExchange):
    """MetaTrade 5 exchange module for `lettrade`"""


class LetTradeMetaTraderBot(LetTradeLiveBot):
    """"""


class LetTradeMetaTrader(LetTradeLive):
    """Help to maintain metatrader bots"""

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
    stats: Optional[Type["Statistic"]] = Statistic,
    bot: Optional[Type[LetTradeMetaTraderBot]] = LetTradeMetaTraderBot,
    api: Optional[Type[MetaTraderAPI]] = MetaTraderAPI,
    wine: Optional[str] = None,
    **kwargs,
) -> "LetTradeMetaTrader":
    """Help to build `LetTradeMetaTrader`

    Args:
        strategy (Type[Strategy]): _description_
        datas (set[set[str]]): _description_
        login (int): _description_
        password (str): _description_
        server (str): _description_
        commander (Optional[Type[Commander]], optional): _description_. Defaults to None.
        plotter (Optional[Type["Plotter"]], optional): _description_. Defaults to None.
        stats (Optional[Type["Statistic"]], optional): _description_. Defaults to None.
        api (Optional[Type[MetaTraderAPI]], optional): _description_. Defaults to MetaTraderAPI.

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
        api=api,
        bot=bot,
        **kwargs,
    )
