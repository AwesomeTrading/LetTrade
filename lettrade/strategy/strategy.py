from abc import ABCMeta, abstractmethod
from itertools import chain, compress, product, repeat
from numbers import Number
from typing import Callable, Optional

import numpy as np
import pandas as pd

from ..data import DataFeed
from ..exchange import Exchange

# from ..indicator import Indicator


# # TODO: Remove
# def _as_str(value) -> str:
#     if isinstance(value, (Number, str)):
#         return str(value)
#     if isinstance(value, pd.DataFrame):
#         return "df"
#     name = str(getattr(value, "name", "") or "")
#     if name in ("Open", "High", "Low", "Close", "Volume"):
#         return name[:1]
#     if callable(value):
#         name = getattr(value, "__name__", value.__class__.__name__).replace(
#             "<lambda>", "λ"
#         )
#     if len(name) > 10:
#         name = name[:9] + "…"
#     return name


# def try_(lazy_func, default=None, exception=Exception):
#     try:
#         return lazy_func()
#     except exception:
#         return default


class Strategy(metaclass=ABCMeta):
    def __init__(self, exchange, params):
        self._indicators = []
        self._exchange: Exchange = exchange
        self._params = self._check_params(params)

    def __repr__(self):
        return "<Strategy " + str(self) + ">"

    def __str__(self):
        return f"{self.__class__.__name__}{self._params}"

    def _check_params(self, params):
        for k, v in params.items():
            if not hasattr(self, k):
                raise AttributeError(
                    f"Strategy '{self.__class__.__name__}' is missing parameter '{k}'."
                    "Strategy class should define parameters as class variables before they "
                    "can be optimized or run with."
                )
            setattr(self, k, v)
        return params

    # def I(
    #     self,  # noqa: E743
    #     func: Callable,
    #     *args,
    #     name=None,
    #     plot=True,
    #     overlay=None,
    #     color=None,
    #     scatter=False,
    #     data: DataFeed = None,
    #     **kwargs,
    # ) -> np.ndarray:
    #     """
    #     Declare an indicator. An indicator is just an array of values,
    #     but one that is revealed gradually in
    #     `backtesting.backtesting.Strategy.next` much like
    #     `backtesting.backtesting.Strategy.data` is.
    #     Returns `np.ndarray` of indicator values.

    #     `func` is a function that returns the indicator array(s) of
    #     same length as `backtesting.backtesting.Strategy.data`.

    #     In the plot legend, the indicator is labeled with
    #     function name, unless `name` overrides it.

    #     If `plot` is `True`, the indicator is plotted on the resulting
    #     `backtesting.backtesting.Backtest.plot`.

    #     If `overlay` is `True`, the indicator is plotted overlaying the
    #     price candlestick chart (suitable e.g. for moving averages).
    #     If `False`, the indicator is plotted standalone below the
    #     candlestick chart. By default, a heuristic is used which decides
    #     correctly most of the time.

    #     `color` can be string hex RGB triplet or X11 color name.
    #     By default, the next available color is assigned.

    #     If `scatter` is `True`, the plotted indicator marker will be a
    #     circle instead of a connected line segment (default).

    #     Additional `*args` and `**kwargs` are passed to `func` and can
    #     be used for parameters.

    #     For example, using simple moving average function from TA-Lib:

    #         def init():
    #             self.sma = self.I(ta.SMA, self.data.close, self.n_sma)
    #     """
    #     if name is None:
    #         params = ",".join(filter(None, map(_as_str, chain(args, kwargs.values()))))
    #         func_name = _as_str(func)
    #         name = f"{func_name}({params})" if params else f"{func_name}"
    #     else:
    #         name = name.format(
    #             *map(_as_str, args),
    #             **dict(zip(kwargs.keys(), map(_as_str, kwargs.values()))),
    #         )

    #     if data is None:
    #         data = self.data

    #     try:
    #         value = func(*args, **kwargs)
    #     except Exception as e:
    #         raise RuntimeError(f'Indicator "{name}" error') from e

    #     if isinstance(value, pd.DataFrame):
    #         value = value.values.T

    #     if value is not None:
    #         value = try_(lambda: np.asarray(value, order="C"), None)
    #     is_arraylike = bool(value is not None and value.shape)

    #     # Optionally flip the array if the user returned e.g. `df.values`
    #     if is_arraylike and np.argmax(value.shape) == 0:
    #         value = value.T

    #     if (
    #         not is_arraylike
    #         or not 1 <= value.ndim <= 2
    #         or value.shape[-1] != len(data.close)
    #     ):
    #         raise ValueError(
    #             "Indicators must return (optionally a tuple of) numpy.arrays of same "
    #             f'length as `data` (data shape: {data.close.shape}; indicator "{name}" '
    #             f'shape: {getattr(value, "shape" , "")}, returned value: {value})'
    #         )

    #     if plot and overlay is None and np.issubdtype(value.dtype, np.number):
    #         x = value / data.close
    #         # By default, overlay if strong majority of indicator values
    #         # is within 30% of Close
    #         with np.errstate(invalid="ignore"):
    #             overlay = ((x < 1.4) & (x > 0.6)).mean() > 0.6

    #     value = Indicator(
    #         value,
    #         name=name,
    #         plot=plot,
    #         overlay=overlay,
    #         color=color,
    #         scatter=scatter,
    #         # _Indicator.s Series accessor uses this:
    #         index=data.index,
    #     )
    #     self._indicators.append(value)
    #     return value

    @abstractmethod
    def init(self):
        """ """

    def indicators(self):
        pass

    @abstractmethod
    def next(self):
        """ """

    @abstractmethod
    def end(self):
        """ """

    def buy(
        self,
        *,
        size: float,
        limit: Optional[float] = None,
        stop: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        tag: object = None,
    ):
        """
        Place a new long order. For explanation of parameters, see `Order` and its properties.

        See `Position.close()` and `Trade.close()` for closing existing positions.

        See also `Strategy.sell()`.
        """
        assert (
            0 < size < 1 or round(size) == size
        ), "size must be a positive fraction of equity, or a positive whole number of units"
        return self._exchange.new_order(size, limit, stop, sl, tp, tag)

    def sell(
        self,
        *,
        size: float,
        limit: Optional[float] = None,
        stop: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        tag: object = None,
    ):
        """
        Place a new short order. For explanation of parameters, see `Order` and its properties.

        See also `Strategy.buy()`.

        .. note::
            If you merely want to close an existing long position,
            use `Position.close()` or `Trade.close()`.
        """
        assert (
            0 < size < 1 or round(size) == size
        ), "size must be a positive fraction of equity, or a positive whole number of units"
        return self._exchange.new_order(-size, limit, stop, sl, tp, tag)

    @property
    def equity(self) -> float:
        return 0.0

    @property
    def exchange(self) -> Exchange:
        return self._exchange

    @property
    def data(self) -> DataFeed:
        return self._exchange.data

    @property
    def datas(self) -> list[DataFeed]:
        return self._exchange.datas

    @property
    def position(self) -> "Position":
        return None

    @property
    def orders(self) -> "Tuple[Order, ...]":
        return ()

    @property
    def trades(self) -> "Tuple[Trade, ...]":
        return ()

    @property
    def closed_trades(self) -> "Tuple[Trade, ...]":
        return ()
