import logging
import os
from concurrent.futures import ProcessPoolExecutor
from typing import Optional, Type

from lettrade.account import Account
from lettrade.brain import Brain
from lettrade.commander import Commander
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange
from lettrade.stats import Statistic
from lettrade.strategy import Strategy

logger = logging.getLogger(__name__)


class LetTrade:
    """Help to load and connect module"""

    datas: list[DataFeed]
    """DataFeed list for bot"""
    data: DataFeed
    """Main DataFeed for bot"""

    brain: Brain
    """Brain of bot"""
    feeder: DataFeeder
    """DataFeeder help to handle `datas`"""
    exchange: Exchange
    """Trading exchange and events"""
    account: Account
    """Trading account handler"""
    strategy: Strategy
    """Strategy"""
    commander: Commander = None
    """Control the bot"""
    plotter: "Plotter" = None
    """Plot graphic results"""
    _stats: Statistic = None

    _strategy_cls: Type[Strategy]
    _feeder_cls: Type[DataFeeder]
    _exchange_cls: Type[Exchange]
    _account_cls: Type[Account]
    _commander_cls: Type[Commander]
    _plotter_cls: Type["Plotter"]
    _stats_cls: Type["Statistic"]
    _kwargs: dict
    _name: str

    def __init__(
        self,
        strategy: Type[Strategy],
        datas: DataFeed | list[DataFeed] | str | list[str],
        feeder: Type[DataFeeder],
        exchange: Type[Exchange],
        account: Type[Account],
        commander: Optional[Type[Commander]] = None,
        plotter: Optional[Type["Plotter"]] = None,
        stats: Optional[Type["Statistic"]] = None,
        **kwargs,
    ) -> None:
        self._strategy_cls = strategy
        self._feeder_cls = feeder
        self._exchange_cls = exchange
        self._account_cls = account
        self._commander_cls = commander
        self._plotter_cls = plotter
        self._stats_cls = stats
        self._kwargs = kwargs

        # DataFeeds
        self.datas = self._init_datafeeds(datas)
        self.data = self.datas[0]

    def _init(self, is_optimize=False):
        # Feeder
        self.feeder = self._feeder_cls(**self._kwargs.get("feeder_kwargs", {}))
        self.feeder.init(self.datas)

        # Account
        self.account = self._account_cls(**self._kwargs.get("account_kwargs", {}))

        # Exchange
        self.exchange = self._exchange_cls(**self._kwargs.get("exchange_kwargs", {}))

        # Commander
        if self._commander_cls:
            self.commander = self._commander_cls(
                **self._kwargs.get("commander_kwargs", {})
            )

        # Strategy
        self.strategy = self._strategy_cls(
            feeder=self.feeder,
            exchange=self.exchange,
            account=self.account,
            commander=self.commander,
            is_optimize=is_optimize,
            **self._kwargs.get("strategy_kwargs", {}),
        )

        # Brain
        self.brain = Brain(
            strategy=self.strategy,
            exchange=self.exchange,
            feeder=self.feeder,
            commander=self.commander,
            **self._kwargs.get("brain_kwargs", {}),
        )

        # Init
        if self.commander:
            self.commander.init(
                lettrade=self,
                brain=self.brain,
                exchange=self.exchange,
                strategy=self.strategy,
            )
        self.exchange.init(
            brain=self.brain,
            feeder=self.feeder,
            account=self.account,
            commander=self.commander,
        )

    def _datafeed(self, data: DataFeed, *args, **kwargs) -> DataFeed:
        """Init and validate DataFeed

        Args:
            data (DataFeed): DataFeed or config of it

        Raises:
            RuntimeError: Validate error

        Returns:
            DataFeed: The DataFeed
        """
        match data:
            case DataFeed():
                return data
            case _:
                raise RuntimeError(f"data {data} is invalid")

    def _init_datafeeds(self, datas) -> None:
        # Support single and multiple data
        if not isinstance(datas, list):
            datas = [datas]

        # Check data
        if isinstance(datas[0], list):
            feeds = []
            for i, data in enumerate(datas):
                data_feeds = []
                for j, d in enumerate(data):
                    d = self._datafeed(data=d, index=i * j)
                    data_feeds.append(d)
                feeds.append(data_feeds)
        else:
            feeds = [self._datafeed(data=data, index=i) for i, data in enumerate(datas)]
        return feeds

    def run(self, worker: Optional[int] = None, *args, **kwargs):
        """Run strategy in single or multiple processing

        Args:
            worker (Optional[int], optional): Number of processing. Defaults to None.
        """
        if worker or isinstance(self.data, list):
            if not isinstance(self.data, list):
                self.data = self.datas
                self.datas = [self.data]

            if not worker:
                worker = len(self.datas)
            elif worker > len(self.datas):
                logger.warning(
                    "Worker size %s is more then datas size %s",
                    worker,
                    len(self.datas),
                )
                worker = len(self.datas)

            self._multiprocess("main")
            with ProcessPoolExecutor(max_workers=worker) as executor:
                futures = [
                    executor.submit(
                        self._run,
                        datas=datas,
                        index=i,
                        multiprocess="sub",
                    )
                    for i, datas in enumerate(self.datas)
                ]
                for future in futures:
                    result = future.result()
                    print(result)
        else:
            return self._run(*args, **kwargs)

    def _run(
        self,
        datas: Optional[list[DataFeed]] = None,
        index: Optional[int] = None,
        multiprocess: Optional[str] = None,
        name=None,
        *args,
        **kwargs,
    ):
        if datas is not None:
            self.datas = datas
            self.data = datas[0]

        # Set name for current processing
        if name is None:
            name = f"{index}-{os.getpid()}-{self.data.name}"
        self._name = name

        # Run inside a subprocess
        if multiprocess == "sub":
            if __debug__:
                logger.info(
                    "[%s] Running %s in subprocess: %s %s",
                    self._name,
                    [d.name for d in datas],
                    index,
                    os.getpid(),
                )

        self._multiprocess(multiprocess)

        # Init objects
        self._init(**kwargs.pop("init_kwargs", {}))

        if self.commander:
            self.commander.start()

        self.brain.run(*args, **kwargs)

        if self.commander:
            self.commander.stop()

        # Only show stats when backtest data
        if self._stats_cls:
            self.stats.compute()
            self.stats.show()

    def _multiprocess(self, process, **kwargs):
        if process == "main":
            if self._commander_cls:
                # Impletement commander dependencies and save to commander_kwargs
                commander_kwargs = self._kwargs.setdefault("commander_kwargs", {})
                self._commander_cls.multiprocess(
                    process,
                    kwargs=commander_kwargs,
                    self_kwargs=self._kwargs,
                    **kwargs,
                )

    def stop(self):
        """Stop strategy"""
        self.brain.stop()
        if self.plotter is not None:
            self.plotter.stop()

    @property
    def stats(self) -> Statistic:
        """Get Statistic object"""
        if self._stats_cls is None:
            raise RuntimeError("Statistic class is not defined")

        if self._stats is None:
            self._stats = self._stats_cls(
                feeder=self.feeder,
                exchange=self.exchange,
                strategy=self.strategy,
            )
        return self._stats

    def plot(self, *args, **kwargs):
        """Plot strategy result"""
        if not hasattr(self, "feeder"):
            logger.warning("Plot in multiprocessing is not implement yet")
            return

        if __debug__:
            from .utils.docs import is_docs_session

            if is_docs_session():
                return

        if self.plotter is None:
            if self._plotter_cls is None:
                raise RuntimeError("Plotter class is None")

            self.plotter = self._plotter_cls(
                feeder=self.feeder,
                exchange=self.exchange,
                account=self.account,
                strategy=self.strategy,
            )

        self.plotter.plot(*args, **kwargs)
