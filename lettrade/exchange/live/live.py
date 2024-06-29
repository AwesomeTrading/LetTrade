from lettrade import BotStatistic, Commander, LetTrade, LetTradeBot, Plotter
from lettrade.strategy.strategy import Strategy

from .api import LiveAPI
from .data import LiveDataFeed


class LetTradeLiveBot(LetTradeBot):
    """Live bot object"""

    datas: list[LiveDataFeed]

    _api: LiveAPI = None

    def __init__(self, api: LiveAPI | None = LiveAPI, **kwargs) -> None:
        """_summary_

        Args:
            api (LiveAPI | None, optional): _description_. Defaults to LiveAPI.
        """
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

    _data_cls: type[LiveDataFeed] = LiveDataFeed

    def _multiprocess(self, **kwargs):
        # Impletement api dependencies and save to api_kwargs
        api: type[LiveAPI] = self._kwargs.get("api")
        api_kwargs = self._kwargs.setdefault("api_kwargs", {})

        api_cls = api if issubclass(api, LiveAPI) else api.__class__
        api_cls.multiprocess(kwargs=api_kwargs)

        super()._multiprocess(**kwargs)

    def _datafeed(
        self,
        data: LiveDataFeed | list | set | tuple,
        **kwargs,
    ) -> LiveDataFeed:
        if isinstance(data, (list | set | tuple)):
            if len(data) < 2:
                raise RuntimeError("LiveDataFeed missing (symbol, timeframe)")
            symbol, timeframe = data[0], data[1]
            name = data[2] if len(data) > 2 else None

            data = self._data_cls(
                name=name,
                symbol=symbol,
                timeframe=timeframe,
            )
        elif isinstance(data, dict):
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
    datas: set[set[str]],
    strategy: type[Strategy],
    *,
    commander: Commander | None = None,
    stats: type[BotStatistic] = BotStatistic,
    plotter: type[Plotter] | None = None,
    bot: type[LetTradeLiveBot] = LetTradeLiveBot,
    lettrade: type[LetTradeLive] = LetTradeLive,
    api: type[LiveAPI] = LiveAPI,
    **kwargs,
) -> "LetTradeLive":
    """Help to build `LetTradeLive`

    Args:
        datas (set[set[str]]): _description_
        strategy (type[Strategy]): _description_
        commander (Commander | None, optional): _description_. Defaults to None.
        stats (type[BotStatistic], optional): _description_. Defaults to BotStatistic.
        plotter (type[Plotter] | None, optional): _description_. Defaults to None.
        bot (type[LetTradeLiveBot], optional): _description_. Defaults to LetTradeLiveBot.
        lettrade (type[LetTradeLive], optional): _description_. Defaults to LetTradeLive.
        api (type[LiveAPI], optional): _description_. Defaults to LiveAPI.

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
