import asyncio
import logging
from functools import partial, wraps
from threading import Thread
from typing import Any, Callable, Coroutine, Dict, List, Literal, Optional, Union

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

from lettrade.stats import Statistic

from .commander import Commander

logger = logging.getLogger(__name__)


def authorized_only(command_handler: Callable[..., Coroutine[Any, Any, None]]):
    """
    Decorator to check if the message comes from the correct chat_id
    :param command_handler: Telegram CommandHandler
    :return: decorated function
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


class TelegramCommander(Commander):
    def __init__(self, token, chat_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._token: str = token
        self._chat_id: int = int(chat_id)

        self._app: Application
        self._loop: asyncio.AbstractEventLoop

    def start(self):
        self._init_keyboard()
        self._start_thread()

    def stop(self):
        self.cleanup()

    def send_message(self, msg: str, **kwargs):
        return self._send_msg(msg, **kwargs)

    async def _cleanup_telegram(self) -> None:
        if self._app.updater:
            await self._app.updater.stop()
        await self._app.stop()
        await self._app.shutdown()

    def cleanup(self) -> None:
        """
        Stops all running telegram threads.
        :return: None
        """
        # This can take up to `timeout` from the call to `start_polling`.
        asyncio.run_coroutine_threadsafe(self._cleanup_telegram(), self._loop)
        self._thread.join()

    def _start_thread(self):
        """
        Creates and starts the polling thread
        """
        self._thread = Thread(target=self._init, name="TelegramCommander")
        self._thread.start()

    def _init_keyboard(self) -> None:
        """
        Validates the keyboard configuration from telegram config
        section.
        """
        self._keyboard: List[List[Union[str, KeyboardButton]]] = [
            ["/stats", "/profit", "/balance"],
            ["/status", "/status table", "/performance"],
            ["/count", "/start", "/stop", "/help"],
        ]

    def _init_telegram_app(self):
        return Application.builder().token(self._token).build()

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
            CommandHandler("status", self._cmd_status),
            # CommandHandler("profit", self._profit),
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
            CommandHandler("stats", self._cmd_stats),
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
            CommandHandler("help", self._cmd_help),
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
            # CallbackQueryHandler(self._force_enter_inline, pattern=r"force_enter__\S+"),
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
        keyboard: Optional[List[List[InlineKeyboardButton]]] = None,
        callback_path: str = "",
        reload_able: bool = False,
        query: Optional[CallbackQuery] = None,
    ) -> None:
        """
        Send given markdown message
        :param msg: message
        :param bot: alternative bot
        :param parse_mode: telegram parse mode
        :return: None
        """
        reply_markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]
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

    @authorized_only
    async def _cmd_help(self, update: Update, context: CallbackContext) -> None:
        """
        Handler for /help.
        Show commands of the bot
        :param bot: telegram bot
        :param update: message update
        :return: None
        """

        msg = (
            "_Bot Control_\n"
            "------------\n"
            "*/balance:* `Show bot managed balance per currency`\n"
            "*/logs [limit]:* `Show latest logs - defaults to 10` \n"
            "*/count:* `Show number of active trades compared to allowed number of trades`\n"
            "*/health* `Show latest process timestamp - defaults to 1970-01-01 00:00:00` \n"
            "_Statistics_\n"
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
        """
        Handler for /status.
        Returns the current TradeThread status
        :param bot: telegram bot
        :param update: message update
        :return: None
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
    async def _cmd_stats(self, update: Update, context: CallbackContext) -> None:
        stats: Statistic = self.lettrade.stats
        stats.compute()
        await self._send_msg(stats.result.to_string())
