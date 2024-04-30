import pandas as pd

from .data import DataFeed


class CSVDataFeed(DataFeed):
    def __init__(self, path: str, *args, **kwargs) -> None:
        df = pd.read_csv(path, index_col=0, parse_dates=["datetime"])
        df.reset_index(inplace=True)
        # df.set_index(pd.DatetimeIndex(df["datetime"]), inplace=True)

        # TODO: validate data

        super().__init__(data=df, name=path, *args, **kwargs)
