from typing import Dict, List, Optional, Set, Tuple, Type

from lettrade import Commander, LetTrade, LetTradeBot, Statistic
from lettrade.strategy.strategy import Strategy

from .account import LiveAccount
from .api import LiveAPI
from .data import LiveDataFeed
from .exchange import LiveExchange
from .feeder import LiveDataFeeder


class LetTradeLiveBot(LetTradeBot):
    datas: list[LiveDataFeed]

    _api: LiveAPI = None

    def __init__(
        self,
        api: Optional[LiveAPI] = LiveAPI,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        if issubclass(api, LiveAPI):
            self._api = api(**self._kwargs.get("api_kwargs", {}))
        else:
            self._api = api

        self._kwargs.setdefault("feeder_kwargs", dict()).update(api=self._api)
        self._kwargs.setdefault("exchange_kwargs", dict()).update(api=self._api)
        self._kwargs.setdefault("account_kwargs", dict()).update(api=self._api)

        for data in self.datas:
            data._api = self._api

    def _init(self):
        self._api.init()
        super()._init()


class LetTradeLive(LetTrade):
    """Help to maintain live bots"""

    def _multiprocess(self, **kwargs):
        # Impletement api dependencies and save to api_kwargs
        api: Type[LiveAPI] = self._kwargs.get("api")
        api_kwargs = self._kwargs.setdefault("api_kwargs", {})

        api_cls = api if issubclass(api, LiveAPI) else api.__class__
        api_cls.multiprocess(kwargs=api_kwargs)

        super()._multiprocess(**kwargs)

    def _datafeed(
        self,
        data: LiveDataFeed | List | Set | Tuple,
        **kwargs,
    ) -> LiveDataFeed:
        if isinstance(data, (List | Set | Tuple)):
            if len(data) < 2:
                raise RuntimeError("LiveDataFeed missing (symbol, timeframe)")
            symbol, timeframe = data[0], data[1]
            name = data[2] if len(data) > 2 else None

            data = LiveDataFeed(
                name=name,
                symbol=symbol,
                timeframe=timeframe,
            )
        elif isinstance(data, Dict):
            data = LiveDataFeed(
                symbol=data.get("symbol"),
                timeframe=data.get("timeframe"),
                name=data.get("name", None),
            )
        elif isinstance(data, LiveDataFeed):
            pass
        else:
            return RuntimeError(f"Data {data} is not support yet")

        return super()._datafeed(data=data, **kwargs)


def let_live(
    strategy: Type[Strategy],
    datas: set[set[str]],
    commander: Optional[Commander] = None,
    plotter: Optional[Type["Plotter"]] = None,
    stats: Optional[Type["Statistic"]] = Statistic,
    api: Optional[Type[LiveAPI]] = LiveAPI,
    bot: Optional[Type[LetTradeLiveBot]] = LetTradeLiveBot,
    **kwargs,
) -> "LetTradeLive":
    """Help to build `LetTradeLive`

    Args:
        strategy (Type[Strategy]): _description_
        datas (set[set[str]]): _description_
        login (int): _description_
        password (str): _description_
        server (str): _description_
        commander (Optional[Commander], optional): _description_. Defaults to None.
        plotter (Optional[Type["Plotter"]], optional): _description_. Defaults to None.
        stats (Optional[Type["Statistic"]], optional): _description_. Defaults to None.
        api (Optional[Type[LiveAPI]], optional): _description_. Defaults to LiveAPI.

    Returns:
        LetTradeLive: _description_
    """
    return LetTradeLive(
        strategy=strategy,
        datas=datas,
        commander=commander,
        plotter=plotter,
        stats=stats,
        bot=bot,
        api=api,
        **kwargs,
    )
