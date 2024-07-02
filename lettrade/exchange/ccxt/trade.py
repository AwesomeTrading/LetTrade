import logging
from typing import Any

import pandas as pd

from lettrade import (
    OrderResult,
    OrderResultError,
    OrderState,
    OrderType,
    PositionResult,
    PositionResultError,
    PositionState,
    TradeSide,
)
from lettrade.exchange.live import (
    LetLiveOrderInvalidException,
    LiveDataFeed,
    LiveExchange,
    LiveExecution,
    LiveOrder,
    LivePosition,
)

from .api import CCXTAPI

logger = logging.getLogger(__name__)


class CCXTExecution(LiveExecution):
    """Execution for CCXT"""

    @classmethod
    def from_raw(
        cls,
        raw,
        exchange: "LiveExchange",
        api: CCXTAPI = None,
    ) -> "CCXTExecution":
        """Building new CCXTExecution from live api raw object

        Args:
            raw (_type_): _description_
            exchange (LiveExchange): _description_

        Returns:
            CCXTExecution: _description_
        """

        return cls(
            exchange=exchange,
            id=raw.ticket,
            # TODO: Fix by get data from symbol
            data=exchange.data,
            # TODO: size and type from raw.type
            size=raw.volume,
            price=raw.price,
            # TODO: set bar time
            at=None,
            order_id=raw.order,
            position_id=raw.position_id,
            tag=raw.comment,
            api=api,
            raw=raw,
        )


class CCXTOrder(LiveOrder):
    """Order for CCXT"""

    exchange: "LiveExchange"

    def __init__(self, is_real: bool = True, **kwargs):
        super().__init__(**kwargs)

        self.is_real: bool = is_real
        """Flag to check `Order` is real, cannot duplicate id, cannot recall from history"""

    def place(self) -> OrderResult:
        """_summary_

        Raises:
            RuntimeError: _description_

        Returns:
            OrderResult: _description_
        """
        if self.state != OrderState.Pending:
            raise RuntimeError(f"Order {self.id} state {self.state} is not Pending")

        try:
            result = self._api.order_open(self)

            self.raw = result
            self.id = result.order

            # TODO: get current order time
            return super(LiveOrder, self).place(at=self.data.l.index[0], raw=result)
        except LetLiveOrderInvalidException as e:
            error = OrderResultError(
                error=e.message,
                order=self,
                raw=e.raw,
            )
            logger.error("Place order %s", str(error))
            self.exchange.on_notify(error=error)
            return error

    def update(
        self,
        limit_price: float | None = None,
        stop_price: float | None = None,
        sl: float | None = None,
        tp: float | None = None,
        caller: float | None = None,
        **kwargs,
    ) -> OrderResult:
        """_summary_

        Args:
            limit_price (float | None, optional): _description_. Defaults to None.
            stop_price (float | None, optional): _description_. Defaults to None.
            sl (float | None, optional): _description_. Defaults to None.
            tp (float | None, optional): _description_. Defaults to None.
            caller (float | None, optional): _description_. Defaults to None.

        Raises:
            RuntimeError: _description_

        Returns:
            OrderResult: _description_
        """
        if caller is self:
            raise RuntimeError(f"Order recusive update {self}")

        if self.parent is None:
            result = self._api.order_update(
                order=self,
                limit_price=limit_price,
                stop_price=stop_price,
                sl=sl,
                tp=tp,
                **kwargs,
            )
            return super(LiveOrder, self).update(
                limit_price=result.limit_price,
                stop_price=result.stop_price,
                sl=result.sl,
                tp=result.tp,
            )
        else:
            # SL/TP Order just a virtual order
            if caller is not self.parent:
                if self.is_sl_order:
                    self.parent.update(sl=stop_price, caller=self)
                elif self.is_tp_order:
                    self.parent.update(tp=limit_price, caller=self)
                else:
                    raise RuntimeError(f"Abandon order {self}")

            return super(LiveOrder, self).update(
                limit_price=limit_price,
                stop_price=stop_price,
            )

    def cancel(self, **kwargs) -> OrderResult:
        """Cancel order

        Returns:
            OrderResult: _description_
        """
        if not self.parent:
            # Abandon order
            result = self._api.order_close(order=self, **kwargs)
        else:
            # Virtual SL/TP order of trade
            result = None

        return super(LiveOrder, self).cancel(raw=result)

    @classmethod
    def from_raw(
        cls,
        raw: Any,
        exchange: "LiveExchange",
        api: CCXTAPI | None = None,
    ) -> "CCXTOrder | None":
        """_summary_

        Args:
            raw (Any): _description_.
            exchange (LiveExchange): _description_.
            api (CCXTAPI | None, optional): _description_. Defaults to None.

        Raises:
            NotImplementedError: _description_

        Returns:
            CCXTOrder: _description_
        """
        # DataFeed
        data = None
        for d in exchange.datas:
            if d.symbol == raw.symbol:
                data = d
                break
        if data is None:
            logger.warning("Raw order %s is not handling %s", raw.symbol, raw)
            return

        # Prices & Side & Type
        limit_price = None
        stop_price = None
        match raw.type:
            case MT5.ORDER_TYPE_BUY:
                side = TradeSide.Buy
                type = OrderType.Market
            case MT5.ORDER_TYPE_SELL:
                side = TradeSide.Sell
                type = OrderType.Market
            case MT5.ORDER_TYPE_BUY_LIMIT:
                side = TradeSide.Buy
                type = OrderType.Limit
                limit_price = raw.price_open
            case MT5.ORDER_TYPE_SELL_LIMIT:
                side = TradeSide.Sell
                type = OrderType.Limit
                limit_price = raw.price_open
            case MT5.ORDER_TYPE_BUY_STOP:
                side = TradeSide.Buy
                type = OrderType.Stop
                stop_price = raw.price_open
            case MT5.ORDER_TYPE_SELL_STOP:
                side = TradeSide.Sell
                type = OrderType.Stop
                stop_price = raw.price_open
            # case MT5.ORDER_TYPE_BUY_STOP_LIMIT:
            #     side = TradeSide.Buy
            #     type = OrderType.StopLimit
            #     # TODO
            #     limit_price = raw.price_open
            #     stop_price = raw.price_open
            # case MT5.ORDER_TYPE_SELL_STOP_LIMIT:
            #     side = TradeSide.Sell
            #     type = OrderType.StopLimit
            #     # TODO
            #     limit_price = raw.price_open
            #     stop_price = raw.price_open
            # case MT5.ORDER_TYPE_CLOSE_BY:
            case _:
                raise NotImplementedError(
                    f"Order type {raw.type} is not implement",
                    raw,
                )
        # State
        match raw.state:
            case MT5.ORDER_STATE_STARTED:
                state = OrderState.Pending
            case MT5.ORDER_STATE_PLACED:
                state = OrderState.Placed
            case MT5.ORDER_STATE_CANCELED:
                state = OrderState.Canceled
            case MT5.ORDER_STATE_PARTIAL:
                state = OrderState.Partial
            case MT5.ORDER_STATE_FILLED:
                state = OrderState.Filled
            case MT5.ORDER_STATE_REJECTED:
                state = OrderState.Canceled
            case MT5.ORDER_STATE_EXPIRED:
                state = OrderState.Canceled
            case MT5.ORDER_STATE_REQUEST_ADD:
                state = OrderState.Placed
            case MT5.ORDER_STATE_REQUEST_MODIFY:
                state = OrderState.Placed
            case MT5.ORDER_STATE_REQUEST_CANCEL:
                state = OrderState.Canceled
            case _:
                raise NotImplementedError(
                    f"Raw order state {raw.state} is not implement"
                )

        order = cls(
            exchange=exchange,
            id=raw.ticket,
            state=state,
            data=data,
            size=side * (raw.volume_current or raw.volume_initial),
            type=type,
            limit_price=limit_price,
            stop_price=stop_price,
            sl_price=raw.sl or None,
            tp_price=raw.tp or None,
            tag=raw.comment,
            placed_at=pd.to_datetime(raw.time_setup_msc, unit="ms", utc=True),
            api=api,
            raw=raw,
        )

        if hasattr(raw, "time_done_msc"):
            order.filled_price = raw.price_current
            order.filled_at = pd.to_datetime(raw.time_done_msc, unit="ms", utc=True)

        return order

    @classmethod
    def from_position(
        cls,
        position: "CCXTPosition",
        sl: float | None = None,
        tp: float | None = None,
    ) -> "CCXTOrder":
        """_summary_

        Args:
            position (CCXTPosition): _description_
            sl (float | None, optional): _description_. Defaults to None.
            tp (float | None, optional): _description_. Defaults to None.

        Raises:
            RuntimeError: _description_

        Returns:
            CCXTOrder: _description_
        """
        if not sl and not tp:
            raise RuntimeError("not sl and not tp")
        return cls(
            id=f"{position.id}-{'sl' if sl else 'tp'}",
            exchange=position.exchange,
            data=position.data,
            state=OrderState.Placed,
            type=OrderType.Stop if sl else OrderType.Limit,
            size=-position.size,
            limit_price=tp,
            stop_price=sl,
            parent=position,
            placed_at=position.entry_at,
            is_real=False,
        )


class CCXTPosition(LivePosition):
    """Position for CCXT"""

    exchange: "LiveExchange"

    def update(
        self,
        sl: float | None = None,
        tp: float | None = None,
        caller: float | None = None,
        **kwargs,
    ) -> PositionResult:
        """_summary_

        Args:
            sl (float | None, optional): _description_. Defaults to None.
            tp (float | None, optional): _description_. Defaults to None.
            caller (float | None, optional): _description_. Defaults to None.

        Raises:
            RuntimeError: _description_

        Returns:
            PositionResult: _description_
        """
        if not sl and not tp:
            raise RuntimeError("Update sl=None and tp=None")
        if caller is self:
            raise RuntimeError(f"Position recusive update {self}")

        result = self._api.position_update(position=self, sl=sl, tp=tp)
        if result.code != 0:
            logger.error("Update position %s", str(result))
            error = PositionResultError(
                error=result.error,
                position=self,
                raw=result,
            )
            self.exchange.on_notify(error=error)
            return error

        if sl is not None:
            if self.sl_order:
                if caller is not self.sl_order:
                    self.sl_order.update(stop_price=sl, caller=self)
            else:
                self.sl_order = self.exchange._order_cls.from_position(
                    position=self, sl=sl
                )

        if tp is not None:
            if self.tp_order:
                if caller is not self.tp_order:
                    self.tp_order.update(limit_price=tp, caller=self)
            else:
                self.tp_order = self.exchange._order_cls.from_position(
                    position=self, tp=tp
                )

        return super(LivePosition, self).update(raw=result)

    def exit(self) -> PositionResult:
        """_summary_

        Returns:
            PositionResult: _description_
        """
        result = self._api.position_close(position=self)
        if result.code != 0:
            logger.error("Update position %s", str(result))
            error = PositionResultError(
                error=result.error,
                position=self,
                raw=result,
            )
            self.exchange.on_notify(error=error)
            return error

        execution_raw = self._api.execution_get(id=result.execution_id)

        # TODO: execution object and event
        result.execution_raw = execution_raw

        return super(LivePosition, self).exit(
            price=result.price,
            at=pd.to_datetime(execution_raw.time_msc, unit="ms", utc=True),
            pl=execution_raw.profit,
            fee=execution_raw.fee + execution_raw.swap + execution_raw.commission,
            raw=result,
        )

    @classmethod
    def from_raw(
        cls,
        raw,
        exchange: "LiveExchange",
        state: PositionState = PositionState.Open,
        data: "LiveDataFeed" = None,
        api: CCXTAPI = None,
    ) -> "CCXTPosition":
        """_summary_

        Args:
            raw (_type_): _description_
            exchange (LiveExchange): _description_
            data (LiveDataFeed, optional): _description_. Defaults to None.
            api (CCXTAPI, optional): _description_. Defaults to None.

        Raises:
            NotImplementedError: _description_

        Returns:
            CCXTPosition: _description_
        """
        # DataFeed
        if data is None:
            for d in exchange.datas:
                if d.symbol == raw.symbol:
                    data = d
                    break
            if data is None:
                logger.warning("Raw position %s is not handling %s", raw.symbol, raw)
                return

        # Side
        match raw.type:
            case MT5.POSITION_TYPE_BUY:
                side = TradeSide.Buy
            case MT5.POSITION_TYPE_SELL:
                side = TradeSide.Sell
            case _:
                raise NotImplementedError(
                    f"Position type {raw.type} is not implement",
                    raw,
                )

        position = cls(
            exchange=exchange,
            id=raw.ticket,
            data=data,
            state=state,
            size=side * raw.volume,
            entry_price=raw.price_open,
            entry_fee=raw.swap,
            entry_at=pd.to_datetime(raw.time_msc, unit="ms", utc=True),
            parent=None,
            tag=raw.comment,
            api=api,
            raw=raw,
        )

        # SL
        if raw.sl > 0.0:
            position.sl_order = exchange._order_cls.from_position(
                position=position, sl=raw.sl
            )
            exchange.on_order(position.sl_order)

        # TP
        if raw.tp > 0.0:
            position.tp_order = exchange._order_cls.from_position(
                position=position, tp=raw.tp
            )
            exchange.on_order(position.tp_order)

        return position

    # @classmethod
    # def from_id(
    #     cls,
    #     id: str,
    #     exchange: "LiveExchange",
    #     data: LiveDataFeed = None,
    #     api: CCXTAPI = None,
    # ) -> "CCXTPosition":
    #     if api is None:
    #         api = exchange._api

    #     raws = api.positions_get(id=id)
    #     return cls.from_raw(
    #         raw=raws[0],
    #         exchange=exchange,
    #         data=data,
    #         api=api,
    #     )
