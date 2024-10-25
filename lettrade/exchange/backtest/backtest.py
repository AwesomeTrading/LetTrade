import logging
import os
from collections.abc import Callable
from concurrent.futures import Future, ProcessPoolExecutor
from itertools import product, repeat
from multiprocessing import Queue
from typing import Any, Literal

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
    Strategy,
)

from .account import BackTestAccount
from .commander import BackTestCommander
from .data import BackTestDataFeed, CSVBackTestDataFeed
from .exchange import BackTestExchange
from .feeder import BackTestDataFeeder
from .plot import OptimizePlotter
from .stats import OptimizeStatistic

logger = logging.getLogger(__name__)


def logging_filter_optimize():
    # logging.getLogger("lettrade.exchange.backtest.backtest").setLevel(logging.WARNING)
    logging.getLogger("lettrade.exchange.backtest.commander").setLevel(logging.WARNING)
    logging.getLogger("lettrade.exchange.backtest.exchange").setLevel(logging.WARNING)
    logging.getLogger("lettrade.exchange.order").setLevel(logging.WARNING)
    logging.getLogger("lettrade.stats.stats").setLevel(logging.WARNING)
    logging.getLogger("lettrade.bot").setLevel(logging.WARNING)


class LetTradeBackTestBot(LetTradeBot):
    """LetTradeBot for backtest"""

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
    _stats: OptimizeStatistic = None

    @property
    def _optimize_stats_cls(self) -> type["OptimizeStatistic"]:
        return self._kwargs.get("optimize_stats_cls", None)

    @property
    def _optimize_plotter_cls(self) -> type["OptimizePlotter"]:
        return self._kwargs.get("optimize_plotter_cls", None)

    @_optimize_plotter_cls.setter
    def _optimize_plotter_cls(self, value):
        self._kwargs["optimize_plotter_cls"] = value

    @property
    def _strategy_cls(self) -> type[Strategy]:
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
        self._stats = self._optimize_stats_cls(
            plotter=self._plotter,
            total=total,
            **self._kwargs.get("optimize_plotter_kwargs", {}),
        )

        # Optimize stats queue
        self._kwargs["queue"] = self._stats.queue

        # Optimize cache dir
        if cache is not None:
            cache = _optimize_cache_dir(cache, self._strategy_cls)
            self._kwargs["cache"] = cache

    # --- Optimize: Grid search
    def optimize(
        self,
        multiprocessing: Literal["auto", "fork"] = "auto",
        workers: int | None = None,
        process_bar: bool = True,
        cache: str = "data/optimize",
        **kwargs,
    ):
        """Backtest optimization

        Args:
            multiprocessing (str | None, optional): _description_. Defaults to "auto".
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

        self.optimize_done()

    def _optimizes_multiproccess(
        self,
        optimizes: list[set],
        multiprocessing: Literal["auto", "fork"],
        workers: int | None = None,
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

    # --- Optimize: model for external optimizer
    # Create optimize model environment
    _opt_main_pid: int = None
    _opt_params_parser: Callable[[Any], list[set[str, Any]]] = None
    _opt_result_parser: Callable[[pd.Series], float] = None
    _opt_kwargs: dict = None

    def optimize_model(
        self,
        params_parser: Callable[[Any], list[set[str, Any]]] = None,
        result_parser: Callable[[pd.Series], float] = None,
        total: int = 0,
        cache: str = "data/optimize",
        process_bar: bool = False,
        dumper: Callable[[dict, "LetTradeBackTest"], None] | None = None,
    ) -> Callable[[Any], Any]:
        """Optimize function help to integrated with external optimize trainer

        Args:
            params_parser (Callable[[Any], list[set[str, Any]]], optional): Parse external parameters to bot parameters dict. Defaults to None.
            result_parser (Callable[[pd.Series], float], optional): Parse bot result to external score. Defaults to None.
            total (int, optional): Total number of optimize if possible. Defaults to 0.
            cache (str, optional): Cache directory to store optimize result. Defaults to "data/optimize".
            process_bar (bool, optional): Enable/Disable process bar. Defaults to False.

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
        optimizer_kwargs = dict(
            main_pid=os.getpid(),
            params_parser=params_parser,
            result_parser=result_parser,
            kwargs=self._kwargs,
        )

        if dumper is not None:
            dumper(optimizer_kwargs, self)
        else:
            self.__class__._optimize_model_kwargs(optimizer_kwargs)

        return self.__class__._optimize_model

    @classmethod
    def _optimize_model_kwargs(cls, kwargs: dict):
        for key, value in kwargs.items():
            setattr(cls, f"_opt_{key}", value)

    @classmethod
    def _optimize_model(cls, optimize: dict[str, Any], optimizer_kwargs=None, **kwargs):
        """Model to run bot in singleprocessing or multiprocessing

        Args:
            optimize (list[set[str, Any]]): _description_

        Raises:
            RuntimeError: _description_

        Returns:
            _type_: _description_
        """
        # Optimizer loader
        if optimizer_kwargs is not None:
            cls._optimize_model_kwargs(optimizer_kwargs)

        # Load optimize parameters
        if cls._opt_params_parser:
            optimize = cls._opt_params_parser(optimize)

        # Load cache here to skip copy kwargs and data data
        cache = cls._opt_kwargs.get("cache", None)
        if cache is not None:
            cached = _optimize_cache_get(dir=cache, optimize=optimize)
            if cached is not None:
                result = cached["result"]

                # Put result to stats
                queue = cls._opt_kwargs.get("queue", None)
                if queue is not None:
                    queue.put(dict(index=None, optimize=optimize, result=result))

                # Prepare model result
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

    # --- Optimize: load cached optimize result
    def optimize_cache(self, cache: str = "data/optimize"):
        """Load optimize results from cache

        Args:
            cache (str, optional): Cache directory. Defaults to "data/optimize".
        """
        import json

        self._optimize_init(cache=cache, total=0, process_bar=False)
        cache_dir = self._kwargs["cache"]
        queue = self._kwargs["queue"]

        logger.info("Load caches from: %s", cache)

        for cache_file in os.listdir(cache_dir):
            if cache_file == "info.json":
                continue

            try:
                cache_path = f"{cache_dir}/{cache_file}"
                data = json.load(open(cache_path, encoding="utf-8"))

                queue.put(
                    dict(
                        index=cache_file,
                        optimize=data["optimize"],
                        result=data["result"],
                    )
                )
            except Exception as e:
                logger.warning("Loading cache %s error %s", cache_path, e)

        logger.info("Loaded %s caches", len(self._stats.results))

    def optimize_done(self):
        """Clean and close optimize handlers"""
        self._stats.done()

    # --- Optimize: run
    @classmethod
    def _optimize_run(
        cls,
        datas: list[DataFeed],
        optimize: dict[str, Any],
        bot_cls: type[LetTradeBot],
        index: int = 0,
        queue: "Queue | None" = None,
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
                        queue.put(dict(index=index, optimize=optimize, result=result))

                    # logger.info("Optimize load cache: %s", cached["path"])
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
                queue.put(dict(index=index, optimize=optimize, result=result))

            return result
        except Exception as e:
            logger.error("Optimize %d", index, exc_info=e)
            raise e


def _batch(seq, workers=None):
    n = np.clip(int(len(seq) // (workers or os.cpu_count() or 1)), 1, 300)
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def _md5_dict(d: dict):
    import hashlib
    import json

    return hashlib.md5(json.dumps(d, sort_keys=True).encode("utf-8")).hexdigest()


def _optimize_cache_dir(dir: str, strategy_cls: type[Strategy]) -> str:
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
        # Get disassembly code of class
        import dis
        import io
        from contextlib import redirect_stdout

        with redirect_stdout(io.StringIO()) as f:
            dis.dis(strategy_cls)
            asm = f.getvalue()

        info.update(
            strategy_hash=hashlib.md5(asm.encode("utf-8")).hexdigest(),
        )

    cache_dir = Path(f"{dir}/{_md5_dict(info)}")
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Strategy information
    with open(f"{cache_dir}/info.json", "w", encoding="utf-8") as f:
        json.dump(info, f)

    logger.info("Optimize cache directory: %s %s", cache_dir, info)
    return cache_dir.absolute()


def _optimize_cache_get(dir: str, optimize: dict) -> str | None:
    import json

    try:
        hash = _md5_dict(optimize)
        path = f"{dir}/{hash}.json"

        data = json.load(open(path, encoding="utf-8"))
        data["path"] = path
        data["result"] = pd.Series(data["result"])
        return data
    except FileNotFoundError:
        return None


def _optimize_cache_set(dir: str, optimize: dict, result: pd.Series):
    import json

    hash = _md5_dict(optimize)
    path = f"{dir}/{hash}.json"
    with open(path, "w+", encoding="utf-8") as f:
        json.dump(
            dict(
                optimize=optimize,
                result=json.loads(result.to_json()),
            ),
            f,
        )


def let_backtest(
    datas: DataFeed | list[DataFeed] | str | list[str],
    strategy: type[Strategy],
    *,
    feeder: type[DataFeeder] = BackTestDataFeeder,
    exchange: type[Exchange] = BackTestExchange,
    account: type[Account] = BackTestAccount,
    commander: type[Commander] | Commander | None = BackTestCommander,
    stats: type[BotStatistic] | None = BotStatistic,
    optimize_stats: type[OptimizeStatistic] | None = OptimizeStatistic,
    plotter: type[BotPlotter] | None = "PlotlyBotPlotter",
    optimize_plotter: type[OptimizePlotter] | None = "PlotlyOptimizePlotter",
    bot: type[LetTradeBackTestBot] | None = LetTradeBackTestBot,
    name: str | None = None,
    # Account kwargs
    balance: float | None = 10_000,
    commission: float | None = 0.2,
    leverage: float | None = 20,
    **kwargs,
) -> "LetTradeBackTest":
    """Complete `lettrade` backtest depenencies

    Args:
        datas (DataFeed | list[DataFeed] | str | list[str]): _description_
        strategy (type[Strategy]): The Strategy implement class
        feeder (type[DataFeeder], optional): _description_. Defaults to BackTestDataFeeder.
        exchange (type[Exchange], optional): _description_. Defaults to BackTestExchange.
        account (type[Account], optional): _description_. Defaults to BackTestAccount.
        commander (type[Commander] | Commander | None, optional): _description_. Defaults to BackTestCommander.
        stats (type[BotStatistic] | None, optional): _description_. Defaults to BotStatistic.
        optimize_stats (type[OptimizeStatistic] | None, optional): _description_. Defaults to OptimizeStatistic.
        plotter (type[BotPlotter] | None, optional): _description_. Defaults to "PlotlyBotPlotter".
        optimize_plotter (type[OptimizePlotter] | None, optional): _description_. Defaults to "PlotlyOptimizePlotter".
        bot (type[LetTradeBackTestBot] | None, optional): _description_. Defaults to LetTradeBackTestBot.
        name (str | None, optional): _description_. Defaults to None.
        balance (float | None, optional): _description_. Defaults to 10_000.
        commission (float | None, optional): _description_. Defaults to 0.2.
        leverage (float | None, optional): _description_. Defaults to 20.

    Returns:
        LetTradeBackTest: The LetTrade backtesting object
    """

    account_kwargs: dict = kwargs.setdefault("account_kwargs", {})
    account_kwargs.update(
        balance=balance,
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
        name=name,
        # Backtest
        optimize_stats_cls=optimize_stats,
        optimize_plotter_cls=optimize_plotter,
        **kwargs,
    )
