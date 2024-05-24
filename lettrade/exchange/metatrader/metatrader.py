from typing import Dict, List, Optional, Set, Tuple, Type

from lettrade import Commander, LetTrade, Statistic
from lettrade.strategy.strategy import Strategy

from .account import MetaTraderAccount
from .api import MetaTraderAPI
from .data import MetaTraderDataFeed
from .exchange import MetaTraderExchange
from .feeder import MetaTraderDataFeeder


def let_metatrader(
    strategy: Type[Strategy],
    datas: set[set[str]],
    login: int,
    password: str,
    server: str,
    commander: Optional[Commander] = None,
    plotter: Optional[Type["Plotter"]] = None,
    stats: Optional[Type["Statistic"]] = Statistic,
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
        commander (Optional[Commander], optional): _description_. Defaults to None.
        plotter (Optional[Type["Plotter"]], optional): _description_. Defaults to None.
        stats (Optional[Type["Statistic"]], optional): _description_. Defaults to None.
        api (Optional[Type[MetaTraderAPI]], optional): _description_. Defaults to MetaTraderAPI.

    Returns:
        LetTradeMetaTrader: _description_
    """
    api_kwargs: dict = kwargs.pop("api_kwargs", {})
    api_kwargs.update(
        login=int(login),
        password=password,
        server=server,
        wine=wine,
    )

    return LetTradeMetaTrader(
        strategy=strategy,
        datas=datas,
        commander=commander,
        plotter=plotter,
        stats=stats,
        api=api,
        api_kwargs=api_kwargs,
        **kwargs,
    )


class LetTradeMetaTrader(LetTrade):
    """Help to maintain metatrader bots"""

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
        """_summary_

        Args:
            strategy (type[Strategy]): _description_
            datas (set[set[str]]): _description_
            feeder (Type[MetaTraderDataFeeder], optional): _description_. Defaults to MetaTraderDataFeeder.
            exchange (Type[MetaTraderExchange], optional): _description_. Defaults to MetaTraderExchange.
            account (Type[MetaTraderAccount], optional): _description_. Defaults to MetaTraderAccount.
            api (Optional[Type[MetaTraderAPI]], optional): _description_. Defaults to MetaTraderAPI.
        """
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

    def _datafeed(
        self,
        data: MetaTraderDataFeed | List | Set | Tuple,
        **kwargs,
    ) -> MetaTraderDataFeed:
        if isinstance(data, (List | Set | Tuple)):
            if len(data) < 2:
                raise RuntimeError("MetaTraderDataFeed missing (symbol, timeframe)")
            symbol, timeframe = data[0], data[1]
            name = data[2] if len(data) > 2 else None

            data = MetaTraderDataFeed(
                name=name,
                symbol=symbol,
                timeframe=timeframe,
                api=self._api,
            )
        elif isinstance(data, Dict):
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

        return super()._datafeed(data=data, **kwargs)

    def _multiprocess(self, process, **kwargs):
        super()._multiprocess(process, **kwargs)

        api_kwargs = self._kwargs.setdefault("api_kwargs", {})
        self._api.multiprocess(self._is_multiprocess, kwargs=api_kwargs, **kwargs)
