import logging
from typing import Optional, Type

import pandas as pd

from lettrade import (
    Account,
    Commander,
    DataFeed,
    DataFeeder,
    Exchange,
    LetTrade,
    Strategy,
)

from .account import BackTestAccount
from .commander import BackTestCommander
from .data import BackTestDataFeed, CSVBackTestDataFeed
from .exchange import BackTestExchange
from .feeder import BackTestDataFeeder

logger = logging.getLogger(__name__)


def let_backtest(
    strategy: Type[Strategy],
    datas: Optional[DataFeed | list[DataFeed] | str | list[str]],
    feeder: Optional[DataFeeder] = None,
    exchange: Optional[Exchange] = None,
    commander: Optional[Commander] = None,
    plot: Optional[Type["Plotter"]] = None,
    cash: Optional[float] = 10_000.0,
    account: Optional[Account] = None,
    **kwargs,
) -> "LetTrade":
    """Complete `lettrade` backtest depenencies

    Args:
        strategy (Type[Strategy]): The Strategy implement class
        datas (Optional[DataFeed  |  list[DataFeed]  |  str  |  list[str]]): _description_
        feeder (Optional[DataFeeder], optional): _description_. Defaults to None.
        exchange (Optional[Exchange], optional): _description_. Defaults to None.
        commander (Optional[Commander], optional): _description_. Defaults to None.
        plot (Optional[Type[Plotter]], optional): _description_. Defaults to None.
        cash (Optional[float], optional): _description_. Defaults to 10_000.0.
        account (Optional[Account], optional): _description_. Defaults to None.

    Raises:
        RuntimeError: The validate parameter error

    Returns:
        LetTrade: The LetTrade backtest object
    """
    from lettrade.plot import Plotter

    # Data
    feeds = []
    # Support single and multiple data
    if not isinstance(datas, list):
        datas = [datas]
    for data in datas:
        if isinstance(data, str):
            feeds.append(CSVBackTestDataFeed(data))
            continue

        if isinstance(data, pd.DataFrame) and not isinstance(data, DataFeed):
            feeds.append(BackTestDataFeed(data))
            continue

        if not isinstance(data, DataFeed):
            raise RuntimeError(f"Data {data} type is invalid")

    # DataFeeder
    if not feeder:
        feeder = BackTestDataFeeder()

    # Account
    if account is None:
        account = BackTestAccount()

    # Exchange
    if exchange is None:
        exchange = BackTestExchange()

    # Commander
    if commander is None:
        commander = BackTestCommander()

    # Plot
    if plot is None:
        plot = Plotter

    return LetTrade(
        strategy=strategy,
        datas=feeds,
        feeder=feeder,
        exchange=exchange,
        commander=commander,
        plot=plot,
        cash=cash,
        account=account,
        **kwargs,
    )
