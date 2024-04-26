import pandas as pd

from .data import DataFeed


class CSVDataFeed(DataFeed):
    def __init__(self, path: str, *args, **kwargs) -> None:
        dataframe = pd.read_csv(path, index_col=0)
        # TODO: Remove invalid data

        super().__init__(data=dataframe, name=path, *args, **kwargs)
