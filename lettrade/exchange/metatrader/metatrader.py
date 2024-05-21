from typing import Optional, Type

from lettrade import Commander, LetTrade
from lettrade.strategy.strategy import Strategy

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
    stats: Optional[Type["Statistic"]] = None,
    api: Optional[Type[MetaTraderAPI]] = MetaTraderAPI,
    **kwargs,
):
    api_kwargs = dict(
        login=int(login),
        password=password,
        server=server,
    )

    return LetTradeMetaTrader(
        strategy=strategy,
        datas=datas,
        commander=commander,
        plot=plot,
        stats=stats,
        api=api,
        api_kwargs=api_kwargs,
        **kwargs,
    )


class LetTradeMetaTrader(LetTrade):
    def __init__(
        self,
        strategy: type[Strategy],
        datas: set[set[str]],
        feeder: Type[MetaTraderDataFeeder] = MetaTraderDataFeeder,
        exchange: Type[MetaTraderExchange] = MetaTraderExchange,
        account: Type[MetaTraderAccount] = MetaTraderAccount,
        api: Optional[Type[MetaTraderAPI]] = MetaTraderAPI,
        **kwargs,
    ) -> None:
        # self._api_cls: Type[MetaTraderAPI] = api
        self._api: MetaTraderAPI = api()

        kwargs.setdefault("feeder_kwargs", dict()).update(api=self._api)
        kwargs.setdefault("exchange_kwargs", dict()).update(api=self._api)
        kwargs.setdefault("account_kwargs", dict()).update(api=self._api)

        super().__init__(
            strategy=strategy,
            datas=datas,
            feeder=feeder,
            exchange=exchange,
            account=account,
            **kwargs,
        )

    def datafeed(
        self,
        data: list | MetaTraderDataFeed,
        **kwargs,
    ) -> MetaTraderDataFeed:
        if isinstance(data, (list, set, tuple)):
            if len(data) < 2:
                raise RuntimeError("DataFeed missing data (symbol, timeframe)")
            symbol, timeframe = data[0], data[1]
            name = data[2] if len(data) > 2 else None

            data = MetaTraderDataFeed(
                name=name,
                symbol=symbol,
                timeframe=timeframe,
                api=self._api,
            )
        elif isinstance(data, dict):
            data = MetaTraderDataFeed(
                symbol=data.get("symbol"),
                timeframe=data.get("timeframe"),
                name=data.get("name", None),
                api=self._api,
            )
        elif isinstance(data, MetaTraderDataFeed):
            pass
        else:
            return RuntimeError(f"Data {data} is not support yet")

        return super().datafeed(data=data, **kwargs)

    def _multiprocess(self, process, **kwargs):
        api_kwargs = self._kwargs.setdefault("api_kwargs", {})
        self._api.multiprocess(process, kwargs=api_kwargs, **kwargs)

        super()._multiprocess(process, **kwargs)
