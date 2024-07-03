import logging
from concurrent.futures import ProcessPoolExecutor
from typing import TYPE_CHECKING

from lettrade.account import Account
from lettrade.bot import LetTradeBot
from lettrade.commander import Commander
from lettrade.data import DataFeed, DataFeeder
from lettrade.exchange import Exchange
from lettrade.plot import BotPlotter, Plotter
from lettrade.stats import BotStatistic
from lettrade.strategy import Strategy

if TYPE_CHECKING:
    from lettrade.exchange.backtest import OptimizePlotter

logger = logging.getLogger(__name__)


class LetTrade:
    """Building new bot object and handle multiprocessing"""

    _plotter: Plotter | None = None
    """Plot graphic results"""
    _stats: BotStatistic | None = None
    _bot: LetTradeBot | None = None

    _kwargs: dict

    def __init__(
        self,
        datas: DataFeed | list[DataFeed] | str | list[str],
        strategy: type[Strategy],
        feeder: type[DataFeeder],
        exchange: type[Exchange],
        account: type[Account],
        commander: type[Commander] | None = None,
        stats: type[BotStatistic] = BotStatistic,
        plotter: type[Plotter] | None = None,
        name: str | None = None,
        bot: type[LetTradeBot] = LetTradeBot,
        **kwargs,
    ) -> None:
        """_summary_

        Args:
            datas (DataFeed | list[DataFeed] | str | list[str]): _description_
            strategy (type[Strategy]): _description_
            feeder (type[DataFeeder]): _description_
            exchange (type[Exchange]): _description_
            account (type[Account]): _description_
            commander (type[Commander] | None, optional): _description_. Defaults to None.
            stats (type[BotStatistic], optional): _description_. Defaults to BotStatistic.
            plotter (type[Plotter] | None, optional): _description_. Defaults to None.
            name (str | None, optional): _description_. Defaults to None.
            bot (type[LetTradeBot], optional): _description_. Defaults to LetTradeBot.
        """
        self._kwargs = kwargs
        self._kwargs["strategy_cls"] = strategy
        self._kwargs["feeder_cls"] = feeder
        self._kwargs["exchange_cls"] = exchange
        self._kwargs["account_cls"] = account
        self._kwargs["commander_cls"] = commander
        self._kwargs["stats_cls"] = stats
        self._kwargs["plotter_cls"] = plotter
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
        feeds: list[list[DataFeed]] | list[DataFeed]
        if isinstance(datas[0], list):
            feeds = []
            for i, data in enumerate(datas):
                data_feeds: list[DataFeed] = []
                for j, d in enumerate(data):
                    df = self._datafeed(data=d, index=i * j)
                    data_feeds.append(df)
                feeds.append(data_feeds)
        else:
            feeds = [self._datafeed(data=data, index=i) for i, data in enumerate(datas)]
        return feeds

    def start(self, force: bool = False):
        """Start LetTrade by init bot object and loading datafeeds

        Args:
            force (bool, optional): _description_. Defaults to False.
        """
        if force and self._bot is not None:
            self._bot = None

        self._bot = self._bot_cls.start_bot(bot=self._bot, **self._kwargs)

    def run(self, worker: int | None = None, **kwargs):
        """Run LetTrade in single or multiple processing

        Args:
            worker (int | None, optional): Number of processing. Defaults to None.
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
            logger.warning("Removed exist bot when running in multiprocessing")
            self._bot = None

        if self._commander_cls:
            # Implement commander dependencies and save to commander_kwargs
            commander_kwargs = self._kwargs.setdefault("commander_kwargs", {})
            self._commander_cls.multiprocess(
                kwargs=commander_kwargs,
                # self_kwargs=self._kwargs,
                **kwargs,
            )

    def stop(self):
        """Stop LetTrade"""
        if self._bot is not None:
            return self._bot.stop()
        if self.stats:
            self.stats.stop()

    @property
    def stats(self) -> BotStatistic | None:
        if self._stats:
            return self._stats
        if self._bot is not None:
            return self._bot.stats
        return None

    # Plotter
    @property
    def plotter(self) -> "Plotter | BotPlotter | OptimizePlotter | None":
        if self._plotter is not None:
            return self._plotter
        if self._bot is not None:
            return self._bot.plotter
        raise RuntimeError("Plotter is not defined")

    def plot(self, *args, jump: dict | None = None, **kwargs):
        """Plot strategy/optimize result

        BotPlotter:
            Miror of [BotPlotter.plot()](site:/reference/plot/bot/#lettrade.plot.bot.BotPlotter.plot).
            Plotly implement [PlotlyBotPlotter.plot()](site:/reference/plot/plotly/plotly/#lettrade.plot.plotly.plotly.PlotlyBotPlotter.plot).

            Args:
                `jump` (dict | None, optional): Miror of [BotPlotter.jump()](site:/reference/plot/bot/#lettrade.plot.bot.BotPlotter.jump)

            Example:
                Jump to position_id
                    ```python
                    lt.plot(
                        jump=dict(position_id=1, range=300),
                        layout=dict(height=2000),
                    )
                    ```

        OptimizePlotter:
            Miror of [OptimizePlotter.plot()](site:/reference/plot/optimize/#lettrade.plot.optimize.OptimizePlotter.plot).
            Plotly implement [PlotlyOptimizePlotter.plot()](site:/reference/exchange/backtest/plotly/optimize/#lettrade.exchange.backtest.plotly.optimize.PlotlyOptimizePlotter.plot).

            Example:
                    ```python
                    lt.plot(layout=dict(height=2000))
                    ```
        """
        if __debug__:
            from .utils.docs import is_docs_session

            if is_docs_session():
                return

        self.plotter.plot(*args, jump=jump, **kwargs)

    # Bot kwargs properties
    @property
    def name(self) -> type[LetTradeBot]:
        return self._kwargs.get("name", None)

    @property
    def datas(self) -> list[DataFeed]:
        return self._kwargs.get("datas", None)

    @datas.setter
    def datas(self, value: list[DataFeed]) -> None:
        self._kwargs["datas"] = value

    @property
    def data(self) -> DataFeed:
        return self.datas[0]

    @property
    def _bot_cls(self) -> type[LetTradeBot]:
        return self._kwargs.get("bot_cls", None)

    @property
    def _commander_cls(self) -> type[Commander]:
        return self._kwargs.get("commander_cls", None)

    @_commander_cls.setter
    def _commander_cls(self, value):
        self._kwargs["commander_cls"] = value

    @property
    def _stats_cls(self) -> type[BotStatistic]:
        return self._kwargs.get("stats_cls", None)

    @property
    def _plotter_cls(self) -> type["Plotter"]:
        return self._kwargs.get("plotter_cls", None)

    @_plotter_cls.setter
    def _plotter_cls(self, value):
        self._kwargs["plotter_cls"] = value
