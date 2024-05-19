from typing import Optional, Type

from lettrade import Commander, LetTrade

from .account import MetaTraderAccount
from .api import MetaTraderAPI
from .data import MetaTraderDataFeed
from .exchange import MetaTraderExchange
from .feeder import MetaTraderDataFeeder


def let_metatrader(
    strategy: Type["Strategy"],
    datas: set[set[str]],
    login: int,
    password: str,
    server: str,
    commander: Optional[Commander] = None,
    plot: Optional[Type["Plotter"]] = None,
    api: Optional[Type[MetaTraderAPI]] = MetaTraderAPI,
    **kwargs,
):
    mt5 = MetaTrader(
        account=int(login),
        password=password,
        server=server,
        api=api,
    )

    feeds = []
    for d in datas:
        feeds.append(mt5.data(d[0], d[1]))

    return LetTrade(
        strategy=strategy,
        datas=feeds,
        feeder=mt5.feeder(),
        exchange=mt5.exchange(),
        account=mt5.account(),
        commander=commander,
        plot=plot,
        **kwargs,
    )


class MetaTrader:
    def __init__(
        self,
        tick: int = 5,
        api: Optional[Type[MetaTraderAPI]] = MetaTraderAPI,
        *args,
        **kwargs,
    ) -> None:
        self._tick: int = tick

        self._api: MetaTraderAPI = api()
        self._api.start(*args, **kwargs)

        self._feeder: MetaTraderDataFeeder = None
        self._exchange: MetaTraderExchange = None
        self._account: MetaTraderAccount = None

    def data(
        self,
        symbol: str,
        timeframe: str,
        name: str = None,
    ) -> MetaTraderDataFeed:
        return MetaTraderDataFeed(
            name=name,
            symbol=symbol,
            timeframe=timeframe,
            feeder=self.feeder(),
            api=self._api,
        )

    def feeder(self) -> MetaTraderDataFeeder:
        if not self._feeder:
            self._feeder = MetaTraderDataFeeder(api=self._api, tick=self._tick)
        return self._feeder

    def exchange(self) -> MetaTraderExchange:
        if not self._exchange:
            self._exchange = MetaTraderExchange(api=self._api)
        return self._exchange

    def account(self) -> MetaTraderAccount:
        if not self._account:
            self._account = MetaTraderAccount(api=self._api)
        return self._account
