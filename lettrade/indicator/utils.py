from typing import Callable, Literal

import talib as ta
import talib.abstract as taa


def talib_ma_mode(
    name: Literal["sma", "ema", "wma", "dema", "tema", "trima", "kama", "mama", "t3"]
) -> int:
    """Helper Function that returns the Enum value for TA Lib's MA Type"""
    if isinstance(name, str) and len(name) > 1:
        name = name.lower()
        if name == "sma":
            return ta.MA_Type.SMA  # 0
        elif name == "ema":
            return ta.MA_Type.EMA  # 1
        elif name == "wma":
            return ta.MA_Type.WMA  # 2
        elif name == "dema":
            return ta.MA_Type.DEMA  # 3
        elif name == "tema":
            return ta.MA_Type.TEMA  # 4
        elif name == "trima":
            return ta.MA_Type.TRIMA  # 5
        elif name == "kama":
            return ta.MA_Type.KAMA  # 6
        elif name == "mama":
            return ta.MA_Type.MAMA  # 7
        elif name == "t3":
            return ta.MA_Type.T3  # 8
    return 0  # Default: SMA -> 0


def talib_ma(
    name: Literal["sma", "ema", "wma", "dema", "tema", "trima", "kama", "mama", "t3"]
) -> Callable:
    """Helper Function that returns the Enum value for TA Lib's MA Type"""
    if isinstance(name, str) and len(name) > 1:
        name = name.lower()
        if name == "sma":
            return taa.SMA
        elif name == "ema":
            return taa.EMA
        elif name == "wma":
            return taa.WMA
        elif name == "dema":
            return taa.DEMA
        elif name == "tema":
            return taa.TEMA
        elif name == "trima":
            return taa.TRIMA
        elif name == "kama":
            return taa.KAMA
        elif name == "mama":
            return taa.MAMA
        elif name == "t3":
            return taa.T3
    return taa.SMA
