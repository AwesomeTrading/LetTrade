import logging
from datetime import timezone
from pathlib import Path

import pandas as pd
from pandas.core.base import PandasObject

logger = logging.getLogger(__name__)


def csv_export(
    dataframe: pd.DataFrame,
    path: str | Path = "data/data.csv",
    tz: timezone = None,
    round: int = 5,
    **kwargs,
) -> pd.DataFrame:
    """Dump DataFeed to csv file. Inject function `pandas.DataFrame.let_to_csv()`

    Args:
        dataframe (pd.DataFrame): _description_
        path (str | Path, optional): _description_. Defaults to "data/data.csv".
        tz (timezone, optional): _description_. Defaults to None.
        round (int, optional): _description_. Defaults to 5.

    Returns:
        pd.DataFrame: _description_
    """
    dataframe = dataframe.astype(
        dtype={
            "open": "float",
            "high": "float",
            "low": "float",
            "close": "float",
            "volume": "float",
        }
    )

    if not isinstance(dataframe.index, pd.DatetimeIndex):
        dataframe = dataframe.set_index("datetime")

    if tz is not None:
        dataframe.index = dataframe.index.tz_convert(tz)

    if round > 0:
        dataframe = dataframe.round(round)

    if not isinstance(path, Path):
        path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(path, **kwargs)

    logger.info("Saved data to %s", path)
    return dataframe


PandasObject.let_to_csv = csv_export
