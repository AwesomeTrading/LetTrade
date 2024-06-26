"""Module help LetTrade send notify and receive command from Telegram Bot

# Example

Example:
    ```python
    --8<-- "example/commander/telegram_mt5.py"
    ```
"""

import asyncio
import logging
import time
from collections.abc import Callable, Coroutine
from functools import partial, wraps
from multiprocessing import Manager, Queue
from multiprocessing.managers import BaseManager
from threading import Thread
from typing import Any

from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.constants import MessageLimit, ParseMode
from telegram.error import BadRequest, NetworkError, TelegramError
from telegram.ext import (
    Application,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
)
from telegram.helpers import escape_markdown

from lettrade.plot import BotPlotter
from lettrade.stats import BotStatistic

from .commander import Commander

logger = logging.getLogger(__name__)


def authorized_only(command_handler: Callable[..., Coroutine[Any, Any, None]]):
    """Decorator to check if the message comes from the correct chat_id

    Args:
        command_handler (Callable[..., Coroutine[Any, Any, None]]): Telegram CommandHandler
    """

    @wraps(command_handler)
    async def wrapper(self: "TelegramCommander", *args, **kwargs):
        """Decorator logic"""
        update = kwargs.get("update") or args[0]

        # Reject unauthorized messages
        if update.callback_query:
            cchat_id = int(update.callback_query.message.chat.id)
        else:
            cchat_id = int(update.message.chat_id)

        if cchat_id != self._chat_id:
            logger.info(f"Rejected unauthorized message from: {update.message.chat_id}")
            return wrapper

        logger.debug(
            "Executing handler: %s for chat_id: %s",
            command_handler.__name__,
            self._chat_id,
        )
        try:
            return await command_handler(self, *args, **kwargs)
        except Exception as e:
            await self._send_msg(str(e))
            # except BaseException:
            logger.exception("Exception occurred within Telegram module", exc_info=e)

    return wrapper


class TelegramAPI:
    """Singleton object communicate across multipprocessing"""

    _app: Application
    _loop: asyncio.AbstractEventLoop
    _bots_queue: dict[str, Queue]
    _bot_selected: str

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_singleton"):
            cls._singleton = object.__new__(cls)
            cls._singleton.__init__(*args, **kwargs)
        return cls._singleton

    def __init__(self, token: str, chat_id: int, *args, **kwargs) -> None:
        self._token: str = token
        self._chat_id: int = int(chat_id)
        self._bots_queue = dict()
        self._bot_selected = None

    def start(self, pname: str, action_queue: Queue):
        """Start"""
        if pname in self._bots_queue:
            logger.warning("Process name %s override existed action queue", pname)
        self._bots_queue[pname] = action_queue

        logger.info("New join process: %s", pname)

        # TODO: Lock for safe multipleprocessing
        if hasattr(self, "_keyboard"):
            return

        self._init_keyboard()
        self._start_thread()

    def _action(self, action: str, pname: str | None = None):
        if pname is None:
            pname = list(self._bots_queue.keys())
        elif isinstance(pname, str):
            pname = [pname]

        for name in pname:
            q: Queue = self._bots_queue[name]
            q.put(action)

    def send_message(self, msg: str, pname: str, **kwargs) -> None:
        """Send message to Telegram Bot

        Args:
            msg (str): Message

        Returns:
            _type_: `None`
        """
        msg = f"*[Process: {pname}]*\n\n{escape_markdown(msg)}"
        asyncio.run_coroutine_threadsafe(self._send_msg(msg, **kwargs), self._loop)

    async def _cleanup_telegram(self) -> None:
        if self._app.updater:
            await self._app.updater.stop()
        await self._app.stop()
        await self._app.shutdown()

    def cleanup(self) -> None:
        """Stops all running telegram threads."""
        # This can take up to `timeout` from the call to `start_polling`.
        asyncio.run_coroutine_threadsafe(self._cleanup_telegram(), self._loop)
        self._thread.join()

    def _start_thread(self):
        """
        Creates and starts the polling thread
        """
        self._thread = Thread(target=self._init, name="TelegramAPI")
        self._thread.start()

    def _init_keyboard(self) -> None:
        """
        Validates the keyboard configuration from telegram config
        section.
        """
        self._keyboard: list[list[str | KeyboardButton]] = [
            ["/help", "/bots", "/bot"],
            ["/stats", "/plot", "/status"],
            ["/count"],
        ]

    def _init_telegram_app(self):
        return Application.builder().token(self._token).connection_pool_size(50).build()

    def _init(self) -> None:
        """
        Initializes this module with the given config,
        registers all known command handlers
        and starts polling for message updates
        Runs in a separate thread.
        """
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

        self._app = self._init_telegram_app()

        # Register command handler and start telegram message polling
        handles = [
            CommandHandler("help", self._cmd_help),
            CommandHandler("bots", self._cmd_bots),
            CommandHandler("bot", self._cmd_bot),
            CommandHandler("status", self._cmd_status),
            CommandHandler("stats", self._cmd_stats),
            CommandHandler("plot", self._cmd_plot),
            # CommandHandler("balance", self._balance),
            # CommandHandler("start", self._start),
            # CommandHandler("stop", self._stop),
            # CommandHandler(["forcesell", "forceexit", "fx"], self._force_exit),
            # CommandHandler("reload_trade", self._reload_trade_from_exchange),
            # CommandHandler("trades", self._trades),
            # CommandHandler("delete", self._delete_trade),
            # CommandHandler(["coo", "cancel_open_order"], self._cancel_open_order),
            # CommandHandler("performance", self._performance),
            # CommandHandler(["buys", "entries"], self._enter_tag_performance),
            # CommandHandler(["sells", "exits"], self._exit_reason_performance),
            # CommandHandler("mix_tags", self._mix_tag_performance),
            # CommandHandler("daily", self._daily),
            # CommandHandler("weekly", self._weekly),
            # CommandHandler("monthly", self._monthly),
            # CommandHandler("count", self._count),
            # CommandHandler("locks", self._locks),
            # CommandHandler(["unlock", "delete_locks"], self._delete_locks),
            # CommandHandler(["reload_config", "reload_conf"], self._reload_config),
            # CommandHandler(["show_config", "show_conf"], self._show_config),
            # CommandHandler(["stopbuy", "stopentry"], self._stopentry),
            # CommandHandler("whitelist", self._whitelist),
            # CommandHandler("blacklist", self._blacklist),
            # CommandHandler(["blacklist_delete", "bl_delete"], self._blacklist_delete),
            # CommandHandler("logs", self._logs),
            # CommandHandler("edge", self._edge),
            # CommandHandler("health", self._health),
            # CommandHandler("version", self._version),
            # CommandHandler("marketdir", self._changemarketdir),
            # CommandHandler("order", self._order),
            # CommandHandler("list_custom_data", self._list_custom_data),
        ]
        callbacks = [
            # CallbackQueryHandler(self._status_table, pattern="update_status_table"),
            # CallbackQueryHandler(self._daily, pattern="update_daily"),
            # CallbackQueryHandler(self._weekly, pattern="update_weekly"),
            # CallbackQueryHandler(self._monthly, pattern="update_monthly"),
            # CallbackQueryHandler(self._profit, pattern="update_profit"),
            # CallbackQueryHandler(self._balance, pattern="update_balance"),
            # CallbackQueryHandler(self._performance, pattern="update_performance"),
            # CallbackQueryHandler(
            #     self._enter_tag_performance, pattern="update_enter_tag_performance"
            # ),
            # CallbackQueryHandler(
            #     self._exit_reason_performance, pattern="update_exit_reason_performance"
            # ),
            # CallbackQueryHandler(
            #     self._mix_tag_performance, pattern="update_mix_tag_performance"
            # ),
            # CallbackQueryHandler(self._count, pattern="update_count"),
            # CallbackQueryHandler(self._force_exit_inline, pattern=r"force_exit__\S+"),
            CallbackQueryHandler(self._run_cmd, pattern=r"cmd:\S+"),
        ]
        for handle in handles:
            self._app.add_handler(handle)

        for callback in callbacks:
            self._app.add_handler(callback)

        logger.info(
            "Telegram commander is listening for following commands: %s",
            [[x for x in sorted(h.commands)] for h in handles],
        )
        self._loop.run_until_complete(self._startup_telegram())

    async def _startup_telegram(self) -> None:
        await self._app.initialize()
        await self._app.start()
        if self._app.updater:
            await self._app.updater.start_polling(
                bootstrap_retries=-1,
                timeout=20,
                # read_latency=60,  # Assumed transmission latency
                drop_pending_updates=True,
                # stop_signals=[],  # Necessary as we don't run on the main thread
            )
            while True:
                await asyncio.sleep(10)
                if not self._app.updater.running:
                    break

    async def _send_msg(
        self,
        msg: str,
        parse_mode: str = ParseMode.MARKDOWN,
        disable_notification: bool = False,
        keyboard: list[list[InlineKeyboardButton]] | None = None,
        callback_path: str = "",
        reload_able: bool = False,
        query: CallbackQuery | None = None,
    ) -> None:
        """
        Send given markdown message
        :param msg: message
        :param bot: alternative bot
        :param parse_mode: telegram parse mode
        :return: None
        """
        reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup
        # if query:
        #     await self._update_msg(
        #         query=query,
        #         msg=msg,
        #         parse_mode=parse_mode,
        #         callback_path=callback_path,
        #         reload_able=reload_able,
        #     )
        #     return
        # if reload_able and self._config["telegram"].get("reload", True):
        #     reply_markup = InlineKeyboardMarkup(
        #         [[InlineKeyboardButton("Refresh", callback_data=callback_path)]]
        #     )
        # else:
        if keyboard is not None:
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            reply_markup = ReplyKeyboardMarkup(self._keyboard, resize_keyboard=True)
        try:
            try:
                await self._app.bot.send_message(
                    self._chat_id,
                    text=msg,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup,
                    disable_notification=disable_notification,
                )
            except NetworkError as network_err:
                # Sometimes the telegram server resets the current connection,
                # if this is the case we send the message again.
                logger.warning(
                    "Telegram NetworkError: %s! Trying one more time.",
                    network_err.message,
                )
                await self._app.bot.send_message(
                    self._chat_id,
                    text=msg,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup,
                    disable_notification=disable_notification,
                )
        except TelegramError as telegram_err:
            logger.warning(
                "TelegramError: %s! Giving up on that message.", telegram_err.message
            )

    ##### COMMAND #####
    @authorized_only
    async def _cmd_help(self, update: Update, context: CallbackContext) -> None:
        """Handler for /help.
        Show commands of the bot

        Args:
            update (Update): message update
            context (CallbackContext): Telegram context
        """
        msg = (
            "_Bots Control_\n"
            "*/bots:* `Show list of bot`\n"
            "*/bot <bot_index>:* `Select a bot`\n"
            "\n_Bot Control_\n"
            "------------\n"
            "*/balance:* `Show bot managed balance per currency`\n"
            "*/logs [limit]:* `Show latest logs - defaults to 10` \n"
            "*/count:* `Show number of active trades compared to allowed number of trades`\n"
            "*/health* `Show latest process timestamp - defaults to 1970-01-01 00:00:00` \n"
            "\n_Statistics_\n"
            "------------\n"
            "*/status <trade_id>|[table]:* `Lists all open trades`\n"
            "*/trades [limit]:* `Lists last closed trades (limited to 10 by default)`\n"
            "*/profit [<n>]:* `Lists cumulative profit from all finished trades`\n"
            "*/stats:* `Shows Wins / losses by Sell reason as well as "
            "Avg. holding durations for buys and sells.`\n"
            "*/help:* `This help message`\n"
            "*/version:* `Show version`\n"
        )

        await self._send_msg(msg, parse_mode=ParseMode.MARKDOWN)

    @authorized_only
    async def _cmd_status(self, update: Update, context: CallbackContext) -> None:
        """Handler for /status.
        Returns the current Trade status

        Args:
            update (Update): message update
            context (CallbackContext): Telegram context
        """
        lines = ["Hello", "LetTrade"]
        r = dict()

        msg = ""
        for line in lines:
            if line:
                # if (len(msg) + len(line) + 1) < MAX_MESSAGE_LENGTH:
                msg += line + "\n"
                # # else:
                # await self._send_msg(msg.format(**r))
                # msg = "*Trade ID:* `{trade_id}` - continued\n" + line + "\n"

        await self._send_msg(msg.format(**r))

    @authorized_only
    async def _cmd_bots(self, update: Update, context: CallbackContext) -> None:
        """Handler for /bots
        Returns the current Strategy Statistic

        Args:
            update (Update): message update
            context (CallbackContext): Telegram context
        """
        msg = "_Listening Bots_"
        keyboard = []
        for i, name in enumerate(list(self._bots_queue.keys())):
            msg += f"\n*{i}*: [*{escape_markdown(name,2)}*](/bot {i})"
            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f"/bot {i} {name}",
                        callback_data=f"cmd:/bot {i}",
                    )
                ]
            )

        # print("Telegram: bots:\n", msg, keyboard)
        await self._send_msg(msg, parse_mode=ParseMode.MARKDOWN_V2, keyboard=keyboard)

    @authorized_only
    async def _cmd_bot(self, update: Update, context: CallbackContext) -> None:
        """Handler for /bot
        Returns the current Strategy Statistic

        Args:
            update (Update): message update
            context (CallbackContext): Telegram context
        """
        if (
            not context.args
            or not len(context.args) >= 1
            or not context.args[0].isnumeric()
        ):
            msg = (
                "*/bot <bot_index>*: to select a bot"
                "\n*/bots*: to get list of bot index"
            )
        else:
            bot_index = int(context.args[0])
            names = list(self._bots_queue.keys())

            if bot_index < 0 or bot_index >= len(names):
                msg = f"_Error select bot: {bot_index} "
                msg += f"is out of range {len(names)}_"
            else:
                bot_name = names[bot_index]
                self._bot_selected = bot_name
                msg = "_Success select bot_"

        if self._bot_selected is not None:
            msg += f"\n------\nSelected bot: *{self._bot_selected}*"
            keyboard = [
                [
                    InlineKeyboardButton(
                        text=f"/plot {self._bot_selected}",
                        callback_data=f"cmd:/plot {self._bot_selected}",
                    )
                ]
            ]
        else:
            keyboard = None

        await self._send_msg(msg, keyboard=keyboard)

    @authorized_only
    async def _cmd_stats(self, update: Update, context: CallbackContext) -> None:
        """Handler for /stats
        Returns the current Strategy Statistic

        Args:
            update (Update): message update
            context (CallbackContext): Telegram context
        """
        # stats: Statistic = self.bot.stats
        # stats.compute()
        # await self._send_msg(stats.result.to_string())

        self._action("stats")

    def on_stats(self, stats: str, pname: str):
        self.send_message(stats, pname=pname)

    @authorized_only
    async def _cmd_plot(self, update: Update, context: CallbackContext) -> None:
        """Handler for /plot
        Returns the current Strategy Statistic

        Args:
            update (Update): message update
            context (CallbackContext): Telegram context
        """
        # plot: Statistic = self.bot.plot
        # plot.compute()
        # await self._send_msg(plot.result.to_string())

        self._action("plot", pname=self._bot_selected)

    def on_plot(self, plot: str, pname: str):
        self.send_message(plot, pname=pname)

    @authorized_only
    async def _run_cmd(self, update: Update, context: CallbackContext) -> None:
        if not update.callback_query:
            return

        query = update.callback_query
        if not query or not query.data or not query.data.startswith("cmd:"):
            return

        datas = query.data.split("cmd:", 1)[1].split(" ")

        logger.info("Run command: %s", datas)

        context.args = datas[1:]
        match datas[0]:
            case "/bot":
                await self._cmd_bot(update=update, context=context)
            case "/plot":
                await self._cmd_plot(update=update, context=context)


class TelegramCommander(Commander):
    """Send notify and receive command from Telegram Bot"""

    _api: TelegramAPI
    _is_running: bool

    @classmethod
    def multiprocess(cls, kwargs, **other_kwargs):
        BaseManager.register("TelegramAPI", TelegramAPI)
        manager = BaseManager()
        manager.start()
        kwargs["api"] = manager.TelegramAPI(**kwargs)

    def __init__(
        self,
        token: str,
        chat_id: int,
        api: TelegramAPI | None = None,
        *args,
        **kwargs,
    ) -> None:
        """_summary_

        Args:
            token (str): Telegram Bot token
            chat_id (int): Telegram chat_id
        """
        super().__init__(*args, **kwargs)
        self._api = api or TelegramAPI(token=token, chat_id=chat_id)
        self._is_running = True

    def start(self):
        """Start"""
        logger.info("TelegramCommander start %s", self._name)
        q = self._t_action()
        self._api.start(pname=self._name, action_queue=q)

    def stop(self):
        """Stop"""
        logger.info("TelegramCommander stop %s", self._name)
        self._api.cleanup()
        self._is_running = False

    def send_message(self, msg: str, **kwargs) -> None:
        self._api.send_message(msg=msg, pname=self._name, **kwargs)

    def _t_action(self) -> Queue:
        manager = Manager()
        q = manager.Queue(maxsize=1_000)
        t = Thread(target=self._on_action, kwargs=dict(q=q))
        t.start()
        return q

    def _on_action(self, q: Queue):
        while self._is_running:
            try:
                action = q.get()

                match action:
                    case "stats":
                        self._on_action_stats()
                    case "plot":
                        self._on_action_plot()
            except (BrokenPipeError, EOFError) as e:
                # logger.error("Action", exc_info=e)
                self._is_running = False
                raise e
            except Exception as e:
                logger.error("Action", exc_info=e)
                time.sleep(5)

    def _on_action_stats(self):
        stats: BotStatistic = self.bot.stats
        stats.compute()
        self._api.on_stats(stats=stats.result.to_string(), pname=self._name)

    def _on_action_plot(self):
        plotter: BotPlotter = self.bot.plotter
        plotter.load()
        plotter.plot()
        # self._api.on_plot(plot=plot.result.to_string(), pname=self._name)
