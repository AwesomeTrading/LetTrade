from typing import Literal

import pandas as pd
import talib.abstract as ta


def keltner_channel(
    df: pd.DataFrame,
    # high: str = "high",
    # low: str = "low",
    # close: str = "close",
    ma_period: int = 20,
    ma_mode: Literal["ema", "sma"] = "ema",
    atr: int = 20,
    shift: float = 1.6,
    suffix="",
) -> list[pd.Series]:
    ma_fn = ta.SMA if ma_mode == "sma" else ta.EMA
    i_basis = ma_fn(df, timeperiod=ma_period)
    i_atr = ta.ATR(df, timeperiod=atr)
    i_upper = i_basis + shift * i_atr
    i_lower = i_basis - shift * i_atr

    suffix = f"_{suffix}" if suffix else ""
    i_lower.name = f"kc_lower{suffix}"
    i_basis.name = f"kc_basis{suffix}"
    i_upper.name = f"kc_upper{suffix}"

    return i_lower, i_basis, i_upper
