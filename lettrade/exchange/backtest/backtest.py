import logging
import os
import queue
import threading
from concurrent.futures import Future, ProcessPoolExecutor
from itertools import product, repeat
from multiprocessing import Manager, Queue
from multiprocessing.managers import SyncManager
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
    plotter: Optional[Type[Plotter]] = Plotter,
    stats: Optional[Type[Statistic]] = Statistic,
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
        plotter (Optional[Type[Plotter]], optional): _description_. Defaults to Plotter.

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
        account=account,
        plotter=plotter,
        stats=stats,
        **kwargs,
    )


class LetTradeBackTest(LetTrade):

    def _datafeed(
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

        return super()._datafeed(data, index=index, **kwargs)

    def optimize(
        self,
        multiprocessing: Optional[str] = "auto",
        workers: int = None,
        **kwargs,
    ):
        """Backtest optimization

        Args:
            multiprocessing (Optional[str], optional): _description_. Defaults to "auto".
        """
        optimizes = list(product(*(zip(repeat(k), v) for k, v in kwargs.items())))

        # Disable logging
        logging_filter_optimize()

        # Disable commander
        if self._commander_cls:
            self._commander_cls = None

        # Disable Plotter
        if self._plotter_cls:
            self._plotter_cls = None

        # Queue to update process bar
        processbar_queue = _t_process_bar(size=len(optimizes))

        # Run optimize in multiprocessing
        results = self._optimizes_multiproccess(
            optimizes=optimizes,
            multiprocessing=multiprocessing,
            processbar_queue=processbar_queue,
            workers=workers,
        )

        # Process bar queue None mean Done
        try:
            processbar_queue.put(None)
        except Exception:
            pass

        print("results", results)

    def _optimizes_multiproccess(
        self,
        optimizes: list[set],
        multiprocessing: str,
        processbar_queue: Queue,
        workers: int,
    ):
        optimizes_batches = list(_batch(optimizes, workers=workers))

        # Set max workers
        if workers is None or workers > len(optimizes_batches):
            workers = len(optimizes_batches)
            logger.info("Set optimize workers to %d", workers)

        results = []
        # If multiprocessing start method is 'fork' (i.e. on POSIX), use
        # a pool of processes to compute results in parallel.
        # Otherwise (i.e. on Windows), sequential computation will be "faster".
        if multiprocessing == "fork" or (
            multiprocessing == "auto" and os.name == "posix"
        ):
            with ProcessPoolExecutor(max_workers=workers) as executor:
                futures: list[Future] = []
                index = 0
                for optimizes in optimizes_batches:
                    future = executor.submit(
                        self._optimizes_run,
                        datas=self.datas,
                        optimizes=optimizes,
                        index=index,
                        q=processbar_queue,
                    )
                    futures.append(future)
                    index += len(optimizes)

                for future in futures:
                    result = future.result()
                    results.extend(result)
        else:
            if os.name == "posix":
                logger.warning(
                    "For multiprocessing support in `optimize()` "
                    "set multiprocessing='fork'."
                )

            # self.datas will be override by _run()
            datas = self.datas

            for i, optimize in enumerate(optimizes):
                result = self._optimize_run(
                    datas=[d.copy(deep=True) for d in datas],
                    optimize=optimize,
                    index=i,
                    multiprocess=None,
                    q=processbar_queue,
                )
                results.append(result)
        return results

    def _optimizes_run(
        self,
        datas: list[DataFeed],
        optimizes: list[dict],
        index: int,
        **kwargs,
    ):
        results = []
        for i, optimize in enumerate(optimizes):
            result = self._optimize_run(
                datas=[d.copy(deep=True) for d in datas],
                optimize=optimize,
                index=index + i,
                **kwargs,
            )
            results.append(result)
        return results

    def _optimize_run(
        self,
        datas: list[DataFeed],
        optimize: dict[str, object],
        index: int,
        multiprocess: Optional[str] = "worker",
        q: Queue = None,
        **kwargs,
    ):
        try:
            self._run(
                datas=datas,
                init_kwargs=dict(
                    optimize=optimize,
                    multiprocess=multiprocess,
                    is_optimize=True,
                    **kwargs,
                ),
            )
        except Exception as e:
            logger.error("Optimize %d", index, exc_info=e)
            raise e

        if q is not None:
            q.put(index)

        return self.stats.result

    def _init(self, is_optimize=False, optimize=None, **kwargs):
        super()._init(is_optimize)

        if not is_optimize:
            return

        for param in optimize:
            attr, val = param
            setattr(self.strategy, attr, val)


# Process bar handler
def _t_process_bar(size):
    # queue = Queue(maxsize=1_000)
    manager = Manager()
    q = manager.Queue(maxsize=1_000)
    t = threading.Thread(
        target=_process_bar,
        kwargs=dict(
            size=size,
            q=q,
            manager=manager,
        ),
    )
    t.start()
    return q


def _process_bar(size: int, q: Queue, manager: SyncManager):
    from tqdm import tqdm

    pbar = tqdm(total=size)
    while True:
        try:
            index = q.get(timeout=3)
        except queue.Empty:
            # TODO: check closed main class then exit
            continue

        # Done
        if index is None:
            break

        pbar.update(1)

        # Done
        if pbar.n == pbar.total:
            break

    pbar.close()
    # manager.shutdown()


def _batch(seq, workers=None):
    n = np.clip(int(len(seq) // (workers or os.cpu_count() or 1)), 1, 300)
    for i in range(0, len(seq), n):
        yield seq[i : i + n]
