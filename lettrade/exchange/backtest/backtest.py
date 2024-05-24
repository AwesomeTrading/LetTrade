import logging
import os
import queue
import threading
from concurrent.futures import Future, ProcessPoolExecutor
from itertools import product, repeat
from multiprocessing import Manager, Queue
from multiprocessing.managers import SyncManager
from typing import Any, Callable, Optional, Type

import numpy as np
import pandas as pd

from lettrade import (
    Account,
    Commander,
    DataFeed,
    DataFeeder,
    Exchange,
    LetTrade,
    LetTradeBot,
    Statistic,
    Strategy,
)
from lettrade.plot.plotly import PlotlyPlotter, Plotter

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


class LetTradeBackTestBot(LetTradeBot):

    def _init(self, optimize=None, **kwargs):
        strategy_kwargs = self._kwargs.setdefault("strategy_kwargs", {})
        strategy_kwargs.update(is_optimize=optimize is not None)

        super()._init()

        if not optimize:
            return

        # Set optimize params
        for param in optimize:
            attr, val = param
            setattr(self.strategy, attr, val)


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
        if self.data.index.start != 0:
            # TODO: Can drop unnecessary columns by snapshort data.columns from init time
            raise RuntimeError(
                "Optimize datas is not clean, don't run() backtest before optimize()"
            )

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
        workers: int = None,
    ):
        results = []
        # If multiprocessing start method is 'fork' (i.e. on POSIX), use
        # a pool of processes to compute results in parallel.
        # Otherwise (i.e. on Windows), sequential computation will be "faster".
        if multiprocessing == "fork" or (
            multiprocessing == "auto" and os.name == "posix"
        ):
            optimizes_batches = list(_batch(optimizes, workers=workers))

            # Set max workers
            if workers is None or workers > len(optimizes_batches):
                workers = len(optimizes_batches)
                logger.info("Set optimize workers to %d", workers)

            with ProcessPoolExecutor(max_workers=workers) as executor:
                futures: list[Future] = []
                index = 0
                for optimizes in optimizes_batches:
                    future = executor.submit(
                        self._optimizes_run,
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

            result = self._optimizes_run(
                optimizes=optimizes,
                multiprocess=None,
                q=processbar_queue,
            )
            results.extend(result)
        return results

    def _optimizes_run(
        self,
        optimizes: list[dict],
        index: int = 0,
        **kwargs,
    ):
        results = []
        for i, optimize in enumerate(optimizes):
            result = self._optimize_run(
                datas=[d.copy(deep=True) for d in self.datas],
                optimize=optimize,
                index=index + i,
                **kwargs,
            )
            if result is not None:
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
            bot = self._run_bot(
                datas=datas,
                multiprocess=multiprocess,
                bot_kwargs=dict(
                    is_optimize=True,
                    optimize=optimize,
                    **kwargs,
                ),
            )

            if q is not None:
                q.put(index)
            return bot.stats.result
        except Exception as e:
            logger.error("Optimize %d", index, exc_info=e)
            raise e

    # Create optimize model environment
    def optimize_model(
        self,
        params_parser: Callable[[Any], list[set[str, Any]]],
        result_parser: Callable[[Statistic], float],
        fork_data: bool = False,
    ) -> float | Any:
        """Optimize function help to integrated with external optimizer

        Args:
            params_parser (Callable[[Any], list[set[str, Any]]]): Function help to parse external parameters to LetTrade optimize parameters. Example return: `[('ema_period', 21)]`
            result_parser (Callable[[Statistic], float]): Function help to get/calculate `score` from LetTrade `Statistic` result
            fork_data (bool, optional): Flag to reset data everytime rerun optimize function. Defaults to False.

        Returns:
            float | Any: Return score and more for external optimizer
        """
        if self.data.index.start != 0:
            raise RuntimeError(
                "Optimize datas is not clean, don't run() backtest before optimize()"
            )

        self._opt_params_parser = params_parser
        self._opt_result_parser = result_parser
        self._opt_fork_data = fork_data

        # Disable logging
        logging_filter_optimize()

        # Disable commander
        if self._commander_cls:
            self._commander_cls = None

        # Disable Plotter
        if self._plotter_cls:
            self._plotter_cls = None

        return self._optimize_model

    def _optimize_model(self, *args, **kwargs):
        # Check data didn't reload by multiprocessing
        if self.data.index.start != 0:
            raise RuntimeError(
                "Optimize model data changed, set fork_data=True to reload"
            )

        if self._opt_fork_data:
            datas = [d.copy(deep=True) for d in self.datas]
        else:
            datas = None

        # Load optimize parameters
        if self._opt_params_parser:
            optimize = self._opt_params_parser(*args, **kwargs)
        else:
            optimize = kwargs

        # Run
        result = self._optimize_run(
            datas=datas,
            optimize=optimize,
            index=0,
            multiprocess=None,
        )
        if self._opt_result_parser:
            result = self._opt_result_parser(result)

        return result


def let_backtest(
    strategy: Type[Strategy],
    datas: DataFeed | list[DataFeed] | str | list[str],
    feeder: Type[DataFeeder] = BackTestDataFeeder,
    exchange: Type[Exchange] = BackTestExchange,
    account: Type[Account] = BackTestAccount,
    commander: Optional[Type[Commander]] = BackTestCommander,
    plotter: Optional[Type["Plotter"]] = PlotlyPlotter,
    stats: Optional[Type[Statistic]] = Statistic,
    cash: Optional[float] = 1_000,
    commission: Optional[float] = 0.002,
    leverage: Optional[float] = 20,
    bot: Optional[Type[LetTradeBackTestBot]] = LetTradeBackTestBot,
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
        plotter (Optional[Type[Plotter]], optional): _description_. Defaults to PlotlyPlotter.

    Raises:
        RuntimeError: The validate parameter error

    Returns:
        LetTradeBackTest: The LetTrade backtesting object
    """
    account_kwargs: dict = kwargs.setdefault("account_kwargs", {})
    account_kwargs.update(
        cash=cash,
        commission=commission,
        leverage=leverage,
    )

    return LetTradeBackTest(
        strategy=strategy,
        datas=datas,
        feeder=feeder,
        exchange=exchange,
        commander=commander,
        account=account,
        plotter=plotter,
        stats=stats,
        bot=bot,
        **kwargs,
    )


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
