import logging
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import product, repeat
from typing import Optional, Type

import numpy as np
import pandas as pd

from lettrade import (
    Account,
    Commander,
    DataFeed,
    DataFeeder,
    Exchange,
    LetTrade,
    Statistic,
    Strategy,
)
from lettrade.plot import Plotter

from .account import BackTestAccount
from .commander import BackTestCommander
from .data import BackTestDataFeed, CSVBackTestDataFeed
from .exchange import BackTestExchange
from .feeder import BackTestDataFeeder

logger = logging.getLogger(__name__)


def logging_filter_optimize():
    logging.getLogger("lettrade.exchange.backtest.commander").setLevel(logging.WARNING)
    logging.getLogger("lettrade.exchange.backtest.exchange").setLevel(logging.WARNING)
    logging.getLogger("lettrade.stats.stats").setLevel(logging.WARNING)


def let_backtest(
    strategy: Type[Strategy],
    datas: DataFeed | list[DataFeed] | str | list[str],
    feeder: Type[DataFeeder] = BackTestDataFeeder,
    exchange: Type[Exchange] = BackTestExchange,
    account: Type[Account] = BackTestAccount,
    commander: Optional[Type[Commander]] = BackTestCommander,
    plot: Optional[Type[Plotter]] = Plotter,
    **kwargs,
) -> "LetTradeBackTest":
    """Complete `lettrade` backtest depenencies

    Args:
        strategy (Type[Strategy]): The Strategy implement class
        datas (DataFeed | list[DataFeed] | str | list[str]): _description_
        feeder (Type[DataFeeder], optional): _description_. Defaults to BackTestDataFeeder.
        exchange (Type[Exchange], optional): _description_. Defaults to BackTestExchange.
        account (Type[Account], optional): _description_. Defaults to BackTestAccount.
        commander (Optional[Type[Commander]], optional): _description_. Defaults to BackTestCommander.
        plot (Optional[Type[Plotter]], optional): _description_. Defaults to Plotter.

    Raises:
        RuntimeError: The validate parameter error

    Returns:
        LetTradeBackTest: The LetTrade backtesting object
    """
    return LetTradeBackTest(
        strategy=strategy,
        datas=datas,
        feeder=feeder,
        exchange=exchange,
        commander=commander,
        plot=plot,
        account=account,
        **kwargs,
    )


class LetTradeBackTest(LetTrade):

    def datafeed(
        self,
        data: str | DataFeed | BackTestDataFeed | pd.DataFrame,
        index: int,
        **kwargs,
    ):
        match data:
            case str():
                data = CSVBackTestDataFeed(data)
            case BackTestDataFeed():
                pass
            case DataFeed():
                data = BackTestDataFeed(name=data.name, data=data)
            case pd.DataFrame():
                data = BackTestDataFeed(name=f"data_{index}", data=data)
            case _:
                raise RuntimeError(f"Data {data} type is invalid")

        return super().datafeed(data, index=index, **kwargs)

    def optimize(
        self,
        multiprocessing: Optional[str] = "auto",
        **kwargs,
    ):
        """Backtest optimization

        Args:
            multiprocessing (Optional[str], optional): _description_. Defaults to "auto".
        """
        optimizes = list(product(*(zip(repeat(k), v) for k, v in kwargs.items())))

        # Disable logging
        logging_filter_optimize()

        # Run
        self._optimizes_task(optimizes, multiprocessing=multiprocessing)

    def _optimizes_task(self, optimizes: list[dict], multiprocessing="auto"):
        from tqdm.auto import tqdm

        optimizes_batches = list(_batch(optimizes))

        results = []
        # If multiprocessing start method is 'fork' (i.e. on POSIX), use
        # a pool of processes to compute results in parallel.
        # Otherwise (i.e. on Windows), sequential computation will be "faster".
        if multiprocessing == "fork" or (
            multiprocessing == "auto" and os.name == "posix"
        ):
            with ProcessPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        self._optimizes_run,
                        optimizes=optimizes,
                        index=i,
                    )
                    for i, optimizes in enumerate(optimizes_batches)
                ]
                # for future in futures:
                for future in tqdm(
                    as_completed(futures),
                    total=len(futures),
                    desc="Optimizing",
                ):
                    result = future.result()
                    results.extend(result)
        else:
            if os.name == "posix":
                logger.warning(
                    "For multiprocessing support in `optimize()` "
                    "set multiprocessing='fork'."
                )
            # for i, optimize in enumerate(optimizes):
            for i, optimize in tqdm(enumerate(optimizes)):
                result = self._optimize_run(**optimize, index=i)
                results.extend(result)
        print(results)

    def _optimizes_run(
        self,
        optimizes: list[dict],
        index,
        **kwargs,
    ):
        results = []
        for i, optimize in enumerate(optimizes):
            result = self._optimize_run(
                optimize=optimize,
                index=i,
                batch_index=index,
                **kwargs,
            )
            results.append(result)
        return results

    def _optimize_run(
        self,
        optimize: dict[str, object],
        **kwargs,
    ):
        self._init(is_optimize=True)

        feeder = self.feeder
        exchange = self.exchange
        strategy = self.strategy
        brain = self.brain

        for param in optimize:
            attr, val = param
            setattr(strategy, attr, val)

        brain.run()
        stats = Statistic(
            feeder=feeder,
            exchange=exchange,
            strategy=strategy,
        )
        stats.compute()
        stats.show()

        return stats.result


def _batch(seq):
    n = np.clip(int(len(seq) // (os.cpu_count() or 1)), 1, 300)
    for i in range(0, len(seq), n):
        yield seq[i : i + n]
