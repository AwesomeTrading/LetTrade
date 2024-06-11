import logging
import os
from concurrent.futures import Future, ProcessPoolExecutor
from itertools import product, repeat
from multiprocessing import Queue
from typing import Any, Callable, Literal, Optional, Type

import numpy as np
import pandas as pd

from lettrade import (
    Account,
    BotPlotter,
    BotStatistic,
    Commander,
    DataFeed,
    DataFeeder,
    Exchange,
    LetTrade,
    LetTradeBot,
    OptimizePlotter,
    Strategy,
)

from .account import BackTestAccount
from .commander import BackTestCommander
from .data import BackTestDataFeed, CSVBackTestDataFeed
from .exchange import BackTestExchange
from .feeder import BackTestDataFeeder
from .stats import OptimizeStatistic

logger = logging.getLogger(__name__)


def logging_filter_optimize():
    # logging.getLogger("lettrade.exchange.backtest.backtest").setLevel(logging.WARNING)
    logging.getLogger("lettrade.exchange.backtest.commander").setLevel(logging.WARNING)
    logging.getLogger("lettrade.exchange.backtest.exchange").setLevel(logging.WARNING)
    logging.getLogger("lettrade.exchange.order").setLevel(logging.WARNING)
    logging.getLogger("lettrade.stats.stats").setLevel(logging.WARNING)
    logging.getLogger("lettrade.bot").setLevel(logging.WARNING)


def _md5_dict(d: dict):
    import hashlib
    import json

    return hashlib.md5(json.dumps(d, sort_keys=True).encode("utf-8")).hexdigest()


def _optimize_cache_dir(dir: str, strategy_cls: Type[Strategy]) -> str:
    import hashlib
    import inspect
    import json
    from importlib.metadata import version
    from pathlib import Path

    info = dict(
        lettrade=version("lettrade"),
        strategy=str(strategy_cls),
    )

    try:
        strategy_file = inspect.getfile(strategy_cls)
        info.update(
            strategy_file=strategy_file,
            strategy_hash=hashlib.md5(open(strategy_file, "rb").read()).hexdigest(),
        )
    except OSError:
        import pickle

        info.update(
            strategy_hash=hashlib.md5(pickle.dumps(strategy_cls)).hexdigest(),
        )

    cache_dir = f"{dir}/{_md5_dict(info)}"

    Path(cache_dir).mkdir(parents=True, exist_ok=True)

    # Strategy information
    with open(f"{cache_dir}/info.json", "w", encoding="utf-8") as f:
        json.dump(info, f)

    logger.info("Optimize cache directory: %s %s", cache_dir, info)
    return cache_dir


def _optimize_cache_get(dir: str, optimize: dict) -> str | None:
    import json

    try:
        hash = _md5_dict(optimize)
        path = f"{dir}/{hash}.json"

        data = json.load(open(path, "r", encoding="utf-8"))
        data["path"] = path
        data["result"] = pd.Series(data["result"])
        return data
    except FileNotFoundError:
        return None


def _optimize_cache_set(dir: str, optimize: dict, result: pd.Series):
    import json

    hash = _md5_dict(optimize)
    path = f"{dir}/{hash}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            dict(
                optimize=optimize,
                result=json.loads(result.to_json()),
            ),
            f,
        )


class LetTradeBackTestBot(LetTradeBot):
    def init(self, optimize: dict[str, Any] = None, **kwargs):
        strategy_kwargs = self._kwargs.setdefault("strategy_kwargs", {})
        strategy_kwargs.update(is_optimize=optimize is not None)

        super().init()

        # Optimize
        if not optimize:
            return

        # Set optimize params
        for attr, value in optimize.items():
            setattr(self.strategy, attr, value)


class LetTradeBackTest(LetTrade):

    _optimize_stats: OptimizeStatistic = None

    @property
    def _optimize_stats_cls(self) -> Type["OptimizeStatistic"]:
        return self._kwargs.get("optimize_stats_cls", None)

    @property
    def _optimize_plotter_cls(self) -> Type["OptimizePlotter"]:
        return self._kwargs.get("optimize_plotter_cls", None)

    @_optimize_plotter_cls.setter
    def _optimize_plotter_cls(self, value):
        self._kwargs["optimize_plotter_cls"] = value

    @property
    def _strategy_cls(self) -> Type[Strategy]:
        return self._kwargs.get("strategy_cls", None)

    def _datafeed(
        self,
        data: str | DataFeed | BackTestDataFeed | pd.DataFrame,
        index: int,
        **kwargs,
    ):
        match data:
            case str():
                data = CSVBackTestDataFeed(path=data)
            case BackTestDataFeed():
                pass
            case DataFeed():
                data = BackTestDataFeed(name=data.name, data=data)
            case pd.DataFrame():
                data = BackTestDataFeed(name=f"data_{index}", data=data)
            case _:
                raise RuntimeError(f"Data {data} type is invalid")

        return super()._datafeed(data, index=index, **kwargs)

    def start(self, force: bool = False):
        # Load plotly here just for backtest to improve performance
        if self._plotter_cls == "PlotlyBotPlotter":
            from lettrade.plot.plotly import PlotlyBotPlotter

            self._plotter_cls = PlotlyBotPlotter

        return super().start(force)

    def run(self, worker: int | None = None, **kwargs):
        # Load plotly here just for backtest to improve performance
        if self._plotter_cls == "PlotlyBotPlotter":
            from lettrade.plot.plotly import PlotlyBotPlotter

            self._plotter_cls = PlotlyBotPlotter

        return super().run(worker, **kwargs)

    def optimize(
        self,
        multiprocessing: Literal["auto", "fork"] = "auto",
        workers: Optional[int] = None,
        process_bar: bool = True,
        cache: str = "data/optimize",
        **kwargs,
    ):
        """Backtest optimization

        Args:
            multiprocessing (Optional[str], optional): _description_. Defaults to "auto".
        """
        if self.data.l.pointer != 0:
            # TODO: Can drop unnecessary columns by snapshort data.columns from init time
            raise RuntimeError(
                "Optimize datas is not clean, don't run() backtest before optimize()"
            )

        # optimizes = list(product(*(zip(repeat(k), v) for k, v in kwargs.items())))
        optimizes = list(
            dict(zip(kwargs.keys(), values)) for values in product(*kwargs.values())
        )

        self._optimize_init(cache=cache, total=len(optimizes), process_bar=process_bar)

        # Run optimize in multiprocessing
        self._optimizes_multiproccess(
            optimizes=optimizes,
            multiprocessing=multiprocessing,
            workers=workers,
        )

        # queue None mean Done
        try:
            queue = self._kwargs["queue"]
            queue.put(None)
        except Exception:
            pass

    def _optimize_init(self, cache: str, total: int, process_bar: bool):
        # Disable logging
        logging_filter_optimize()

        # Disable commander
        if self._commander_cls:
            self._commander_cls = None

        # Disable Bot Plotter
        if self._plotter_cls:
            self._plotter_cls = None

        # Enable Optimize plotter
        if self._optimize_plotter_cls == "PlotlyOptimizePlotter":
            from .plotly import PlotlyOptimizePlotter

            self._optimize_plotter_cls = PlotlyOptimizePlotter

        if self._optimize_plotter_cls is not None:
            self._plotter = self._optimize_plotter_cls(
                total=total,
                process_bar=process_bar,
                **self._kwargs.get("optimize_plotter_kwargs", {}),
            )

        # Enable Optimize stats
        self._optimize_stats = self._optimize_stats_cls(
            plotter=self._plotter,
            total=total,
            **self._kwargs.get("optimize_plotter_kwargs", {}),
        )

        # Optimize stats queue
        queue = self._optimize_stats.queue
        self._kwargs["queue"] = queue

        # Optimize cache dir
        if cache is not None:
            cache = _optimize_cache_dir(cache, self._strategy_cls)
            self._kwargs["cache"] = cache

    def _optimizes_multiproccess(
        self,
        optimizes: list[set],
        multiprocessing: Literal["auto", "fork"],
        workers: Optional[int] = None,
    ):
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
                        self.__class__._optimizes_run,
                        optimizes=optimizes,
                        index=index,
                        **self._kwargs,
                    )
                    futures.append(future)
                    index += len(optimizes)

                for future in futures:
                    future.result()
        else:
            if os.name == "posix":
                logger.warning(
                    "For multiprocessing support in `optimize()` "
                    "set multiprocessing='fork'."
                )

            self.__class__._optimizes_run(
                optimizes=optimizes,
                **self._kwargs,
            )

    # Create optimize model environment
    # TODO: Move to classmethod to skip copy Self across multiprocessing
    def optimize_model(
        self,
        params_parser: Callable[[Any], list[set[str, Any]]] = None,
        result_parser: Callable[[BotStatistic], float] = None,
        total: int = 0,
        cache: str = "data/optimize",
        process_bar: bool = False,
    ) -> Callable[[Any], Any]:
        """Optimize function help to integrated with external optimizer

        Args:
            params_parser (Callable[[Any], list[set[str, Any]]], optional): _description_. Defaults to None.
            result_parser (Callable[[BotStatistic], float], optional): _description_. Defaults to None.
            total (int, optional): _description_. Defaults to 0.
            process_bar (bool, optional): _description_. Defaults to False.

        Raises:
            RuntimeError: _description_

        Returns:
            Callable[[Any], Any]: Optimize model function
        """
        if self.data.l.pointer != 0:
            raise RuntimeError(
                "Optimize datas is not clean, don't run() backtest before optimize()"
            )

        self._optimize_init(cache=cache, total=total, process_bar=process_bar)

        # Optimize parameters
        self.__class__._opt_main_pid = os.getpid()
        self.__class__._opt_params_parser = params_parser
        self.__class__._opt_result_parser = result_parser
        self.__class__._opt_kwargs = self._kwargs

        return self.__class__._optimize_model

    @classmethod
    def _optimize_model(cls, optimize: dict[str, Any], **kwargs):
        """Model to run bot in singleprocessing or multiprocessing

        Args:
            optimize (list[set[str, Any]]): _description_

        Raises:
            RuntimeError: _description_

        Returns:
            _type_: _description_
        """
        # Load optimize parameters
        if cls._opt_params_parser:
            optimize = cls._opt_params_parser(optimize)

        # Load cache
        cache = cls._opt_kwargs.get("cache", None)
        if cache is not None:
            cached = _optimize_cache_get(dir=cache, optimize=optimize)
            if cached is not None:
                result = cached["result"]

                # Put result to stats
                queue = cls._opt_kwargs.get("queue", None)
                if queue is not None:
                    queue.put((None, optimize, result))

                if cls._opt_result_parser:
                    result = cls._opt_result_parser(result)

                logger.info("Optimize load cache: %s", cached["path"])
                return result

        # If models run in singleprocessing, copy kwargs for bot to not overrite main kwargs
        if os.getpid() == cls._opt_main_pid:
            opt_kwargs = cls._opt_kwargs.copy()
        else:
            opt_kwargs = cls._opt_kwargs

        # Check data didn't reload by multiprocessing
        datas = opt_kwargs.pop("datas")
        data = datas[0]
        if data.l.pointer != 0:
            print(data.l.pointer, data.l)
            raise RuntimeError(
                "Optimize model data changed, set fork_data=True to reload"
            )

        datas = [d.copy(deep=True) for d in datas]

        # Run
        result = cls._optimize_run(
            datas=datas,
            optimize=optimize,
            **opt_kwargs,
        )
        if cls._opt_result_parser:
            result = cls._opt_result_parser(result)

        return result

    @classmethod
    def _optimizes_run(
        cls,
        datas: list[DataFeed],
        optimizes: list[dict[str, Any]],
        index: int = 0,
        **kwargs,
    ):
        """Run optimize in class method to not copy whole LetTradeBackTest self object

        Args:
            datas (list[DataFeed]): _description_
            optimizes (list[dict]): _description_
            index (int, optional): _description_. Defaults to 0.

        Returns:
            _type_: _description_
        """
        results = []
        for i, optimize in enumerate(optimizes):
            result = cls._optimize_run(
                datas=[d.copy(deep=True) for d in datas],
                optimize=optimize,
                index=index + i,
                **kwargs,
            )
            if result is not None:
                results.append(result)
        return results

    @classmethod
    def _optimize_run(
        cls,
        datas: list[DataFeed],
        optimize: dict[str, Any],
        bot_cls: Type[LetTradeBot],
        index: int = 0,
        queue: Optional[Queue] = None,
        cache: str = None,
        **kwargs,
    ):

        try:
            # Load cache
            # TODO: load cache at beginning of caller
            if cache is not None:
                cached = _optimize_cache_get(dir=cache, optimize=optimize)
                if cached is not None:
                    result = cached["result"]

                    # Put result to stats
                    if queue is not None:
                        queue.put((index, optimize, result))

                    logger.info("Optimize load cache: %s", cached["path"])
                    return result

            # Load bot
            if datas:
                kwargs["datas"] = datas

            bot = bot_cls.run_bot(
                optimize=optimize,
                id=index,
                init_kwargs=dict(optimize=optimize),
                result="bot",
                **kwargs,
            )
            result = bot.stats.result

            if cache is not None:
                _optimize_cache_set(dir=cache, optimize=optimize, result=result)

            if queue is not None:
                queue.put((index, optimize, result))

            return result
        except Exception as e:
            logger.error("Optimize %d", index, exc_info=e)
            raise e


def let_backtest(
    strategy: Type[Strategy],
    datas: DataFeed | list[DataFeed] | str | list[str],
    feeder: Type[DataFeeder] = BackTestDataFeeder,
    exchange: Type[Exchange] = BackTestExchange,
    account: Type[Account] = BackTestAccount,
    commander: Optional[Type[Commander]] = BackTestCommander,
    stats: Optional[Type[BotStatistic]] = BotStatistic,
    optimize_stats: Optional[Type[OptimizeStatistic]] = OptimizeStatistic,
    plotter: Optional[Type[BotPlotter]] = "PlotlyBotPlotter",
    optimize_plotter: Optional[Type[OptimizePlotter]] = "PlotlyOptimizePlotter",
    cash: Optional[float] = 1_000,
    commission: Optional[float] = 0.2,
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
        plotter (Optional[Type[Plotter]], optional): _description_. Defaults to PlotlyBotPlotter.

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
        stats=stats,
        plotter=plotter,
        bot=bot,
        # Backtest
        optimize_stats_cls=optimize_stats,
        optimize_plotter_cls=optimize_plotter,
        **kwargs,
    )


def _batch(seq, workers=None):
    n = np.clip(int(len(seq) // (workers or os.cpu_count() or 1)), 1, 300)
    for i in range(0, len(seq), n):
        yield seq[i : i + n]
