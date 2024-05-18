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
    mt_login: int,
    mt_password: str,
    mt_server: str,
    commander: Optional[Commander] = None,
    plot: Optional[Type["Plotter"]] = None,
    **kwargs,
):
    mt5 = MetaTrader(
        account=int(mt_login),
        password=mt_password,
        server=mt_server,
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
    _api: MetaTraderAPI
    _feeder: MetaTraderDataFeeder = None
    _exchange: MetaTraderExchange = None
    _account: MetaTraderAccount = None

    _tick: bool

    def __init__(self, tick=5, *args, **kwargs) -> None:
        self._tick = tick

        self._api = MetaTraderAPI()
        self._api.start(*args, **kwargs)

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
