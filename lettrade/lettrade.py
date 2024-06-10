import logging
from concurrent.futures import ProcessPoolExecutor
from typing import Optional, Type

from lettrade.account import Account
from lettrade.bot import LetTradeBot
from lettrade.commander import Commander
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange
from lettrade.plot import BotPlotter, OptimizePlotter, Plotter
from lettrade.stats import BotStatistic
from lettrade.strategy import Strategy

logger = logging.getLogger(__name__)


class LetTrade:
    """Building new bot object and handle multiprocessing"""

    _plotter: Plotter = None
    """Plot graphic results"""
    _stats: BotStatistic = None
    _bot: LetTradeBot = None

    _kwargs: dict

    def __init__(
        self,
        strategy: Type[Strategy],
        datas: DataFeed | list[DataFeed] | str | list[str],
        feeder: Type[DataFeeder],
        exchange: Type[Exchange],
        account: Type[Account],
        commander: Optional[Type[Commander]] = None,
        plotter: Optional[Type[Plotter]] = None,
        stats: Optional[Type[BotStatistic]] = None,
        name: Optional[str] = None,
        bot: Optional[Type[LetTradeBot]] = LetTradeBot,
        **kwargs,
    ) -> None:
        self._kwargs = kwargs
        self._kwargs["strategy_cls"] = strategy
        self._kwargs["feeder_cls"] = feeder
        self._kwargs["exchange_cls"] = exchange
        self._kwargs["account_cls"] = account
        self._kwargs["commander_cls"] = commander
        self._kwargs["plotter_cls"] = plotter
        self._kwargs["stats_cls"] = stats
        self._kwargs["bot_cls"] = bot
        self._kwargs["name"] = name

        self._kwargs["datas"] = self._init_datafeeds(datas)

    def _datafeed(self, data: DataFeed, **kwargs) -> DataFeed:
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

    def _init_datafeeds(self, datas) -> list[DataFeed] | list[list[DataFeed]]:
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

    def start(self, force: bool = False):
        if force and self._bot is not None:
            self._bot = None

        self._bot = self._bot_cls.start_bot(bot=self._bot, **self._kwargs)

    def run(self, worker: Optional[int] = None, **kwargs):
        """Run strategy in single or multiple processing

        Args:
            worker (Optional[int], optional): Number of processing. Defaults to None.
        """
        if worker or isinstance(self.data, list):
            if not isinstance(self.data, list):
                # self.data = self.datas
                self.datas = [self.data]

            worker = self._max_workers(worker)

            self._multiprocess()

            datas_source = self._kwargs.pop("datas")
            with ProcessPoolExecutor(max_workers=worker) as executor:
                futures = [
                    executor.submit(
                        self._bot_cls.run_bot,
                        datas=datas,
                        id=i,
                        result="str",
                        **self._kwargs,
                    )
                    for i, datas in enumerate(datas_source)
                ]
                for future in futures:
                    result = future.result()
                    print(result)
        else:
            self._bot = self._bot_cls.run_bot(
                bot=self._bot,
                result="bot",
                **self._kwargs,
            )
            print(str(self._bot.stats))

    def _max_workers(self, worker):
        if not worker:
            worker = len(self.datas)
        elif worker > len(self.datas):
            logger.warning(
                "Worker size %s is more then datas size %s",
                worker,
                len(self.datas),
            )
            worker = len(self.datas)
        return worker

    def _multiprocess(self, **kwargs):
        if self._bot is not None:
            logger.warning("Remove exist bot when running in multiprocessing")
            self._bot = None

        if self._commander_cls:
            # Impletement commander dependencies and save to commander_kwargs
            commander_kwargs = self._kwargs.setdefault("commander_kwargs", {})
            self._commander_cls.multiprocess(
                kwargs=commander_kwargs,
                # self_kwargs=self._kwargs,
                **kwargs,
            )

    # def reset(self):
    #     self._bot = None
    #     self.datas = self._init_datafeeds(datas)
    #     self.data = self.datas[0]

    def stop(self):
        """Stop strategy"""
        if self._bot is not None:
            return self._bot.stop()
        if self.stats:
            self.stats.stop()

    @property
    def stats(self) -> BotStatistic:
        if self._stats:
            return self._stats
        if self._bot is not None:
            return self._bot.stats

    # Plotter
    @property
    def plotter(self) -> BotPlotter | OptimizePlotter:
        if self._plotter is not None:
            return self._plotter
        if self._bot is not None:
            return self._bot.plotter
        raise RuntimeError("Plotter is not defined")

    def plot(self, *args, jump: Optional[dict] = None, **kwargs):
        """Plot strategy result"""
        if __debug__:
            from .utils.docs import is_docs_session

            if is_docs_session():
                return

        self.plotter.plot(*args, jump=jump, **kwargs)

    # Bot kwargs properties
    @property
    def name(self) -> Type[LetTradeBot]:
        return self._kwargs.get("name", None)

    @property
    def datas(self) -> list[DataFeed]:
        return self._kwargs.get("datas", None)

    @property
    def data(self) -> DataFeed:
        return self.datas[0]

    @property
    def _bot_cls(self) -> Type[LetTradeBot]:
        return self._kwargs.get("bot_cls", None)

    # @bot_cls.setter
    # def bot_cls(self, value):
    #     self._kwargs["bot_cls"] = value

    @property
    def _commander_cls(self) -> Type[Commander]:
        return self._kwargs.get("commander_cls", None)

    @_commander_cls.setter
    def _commander_cls(self, value):
        self._kwargs["commander_cls"] = value

    @property
    def _stats_cls(self) -> Type[BotStatistic]:
        return self._kwargs.get("stats_cls", None)

    # @_stats_cls.setter
    # def _stats_cls(self, value):
    #     self._kwargs["stats_cls"] = value

    @property
    def _plotter_cls(self) -> Type["Plotter"]:
        return self._kwargs.get("plotter_cls", None)

    @_plotter_cls.setter
    def _plotter_cls(self, value):
        self._kwargs["plotter_cls"] = value
