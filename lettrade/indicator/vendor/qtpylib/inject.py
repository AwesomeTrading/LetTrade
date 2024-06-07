from .qtpylib import *


def inject_indicators():
    from pandas.core.base import PandasObject

    PandasObject.session = session
    PandasObject.atr = atr
    PandasObject.bollinger_bands = bollinger_bands
    PandasObject.cci = cci
    PandasObject.crossed = crossed
    PandasObject.crossed_above = crossed_above
    PandasObject.crossed_below = crossed_below
    PandasObject.heikinashi = heikinashi
    PandasObject.hull_moving_average = hull_moving_average
    PandasObject.ibs = ibs
    PandasObject.implied_volatility = implied_volatility
    PandasObject.keltner_channel = keltner_channel
    PandasObject.log_returns = log_returns
    PandasObject.macd = macd
    PandasObject.returns = returns
    PandasObject.roc = roc
    PandasObject.rolling_max = rolling_max
    PandasObject.rolling_min = rolling_min
    PandasObject.rolling_mean = rolling_mean
    PandasObject.rolling_std = rolling_std
    PandasObject.rsi = rsi
    PandasObject.stoch = stoch
    PandasObject.zscore = zscore
    PandasObject.pvt = pvt
    PandasObject.chopiness = chopiness
    PandasObject.tdi = tdi
    PandasObject.true_range = true_range
    PandasObject.mid_price = mid_price
    PandasObject.typical_price = typical_price
    PandasObject.vwap = vwap
    PandasObject.rolling_vwap = rolling_vwap
    PandasObject.weighted_bollinger_bands = weighted_bollinger_bands
    PandasObject.rolling_weighted_mean = rolling_weighted_mean

    PandasObject.sma = sma
    PandasObject.wma = wma
    PandasObject.ema = wma
    PandasObject.hma = hma

    PandasObject.zlsma = zlsma
    PandasObject.zlwma = zlema
    PandasObject.zlema = zlema
    PandasObject.zlhma = zlhma
    PandasObject.zlma = zlma
