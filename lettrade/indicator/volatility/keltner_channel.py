from typing import Literal

import pandas as pd
import talib.abstract as ta


def keltner_channel(
    df: pd.DataFrame,
    # high: str = "high",
    # low: str = "low",
    # close: str = "close",
    ma: int = 20,
    ma_mode: Literal["ema", "sma"] = "ema",
    atr: int = 20,
    shift: float = 1.6,
    suffix: str = "",
) -> tuple[pd.Series]:
    """_summary_

    Args:
        df (pd.DataFrame): _description_
        ma (int, optional): _description_. Defaults to 20.
        ma_mode (Literal[&quot;ema&quot;, &quot;sma&quot;], optional): _description_. Defaults to "ema".
        atr (int, optional): _description_. Defaults to 20.
        shift (float, optional): _description_. Defaults to 1.6.
        suffix (str, optional): _description_. Defaults to "".

    Returns:
        tuple[pd.Series]: upper, middle, lower
    """
    ma_fn = ta.SMA if ma_mode == "sma" else ta.EMA

    i_basis = ma_fn(df, timeperiod=ma)

    i_atr = ta.ATR(df, timeperiod=atr)
    i_upper = i_basis + shift * i_atr
    i_lower = i_basis - shift * i_atr

    i_upper.name = f"kc_upper{suffix}"
    i_basis.name = f"kc_basis{suffix}"
    i_lower.name = f"kc_lower{suffix}"

    return i_upper, i_basis, i_lower
