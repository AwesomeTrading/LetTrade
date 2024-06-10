from typing import Dict, List, Optional, Set, Tuple, Type

from lettrade import BotStatistic, Commander, LetTrade, LetTradeBot, Plotter
from lettrade.strategy.strategy import Strategy

from .api import LiveAPI
from .data import LiveDataFeed


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

    def init(self):
        self._api.init()
        super().init()


class LetTradeLive(LetTrade):
    """Help to maintain live bots"""

    _data_cls: Type[LiveDataFeed] = LiveDataFeed

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

            data = self._data_cls(
                name=name,
                symbol=symbol,
                timeframe=timeframe,
            )
        elif isinstance(data, Dict):
            data = self._data_cls(
                symbol=data.get("symbol"),
                timeframe=data.get("timeframe"),
                name=data.get("name", None),
            )
        elif isinstance(data, self._data_cls):
            pass
        else:
            return RuntimeError(f"Data {data} is not support yet")

        return super()._datafeed(data=data, **kwargs)


def let_live(
    strategy: Type[Strategy],
    datas: set[set[str]],
    commander: Optional[Commander] = None,
    plotter: Optional[Type[Plotter]] = None,
    stats: Optional[Type[BotStatistic]] = BotStatistic,
    lettrade: Optional[Type[LetTradeLive]] = LetTradeLive,
    bot: Optional[Type[LetTradeLiveBot]] = LetTradeLiveBot,
    api: Optional[Type[LiveAPI]] = LiveAPI,
    **kwargs,
) -> "LetTradeLive":
    """Help to build `LetTradeLive`

    Args:
        strategy (Type[Strategy]): _description_
        datas (set[set[str]]): _description_
        commander (Optional[Commander], optional): _description_. Defaults to None.
        plotter (Optional[Type[Plotter]], optional): _description_. Defaults to None.
        stats (Optional[Type[BotStatistic]], optional): _description_. Defaults to BotStatistic.
        api (Optional[Type[LiveAPI]], optional): _description_. Defaults to LiveAPI.
        bot (Optional[Type[LetTradeLiveBot]], optional): _description_. Defaults to LetTradeLiveBot.
        lettrade (Optional[Type[LetTradeLive]], optional): _description_. Defaults to LetTradeLive.

    Returns:
        LetTradeLive: _description_
    """
    return lettrade(
        strategy=strategy,
        datas=datas,
        commander=commander,
        plotter=plotter,
        stats=stats,
        bot=bot,
        api=api,
        **kwargs,
    )
