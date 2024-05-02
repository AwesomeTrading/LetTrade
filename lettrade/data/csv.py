import pandas as pd

from .data import DataFeed


class CSVDataFeed(DataFeed):
    def __init__(
        self,
        path: str,
        delimiter=",",
        index_col=0,
        header=0,
        *args,
        **kwargs,
    ) -> None:
        df = pd.read_csv(
            path,
            index_col=index_col,
            parse_dates=["datetime"],
            delimiter=delimiter,
            header=header,
        )
        # df.reset_index(inplace=True)
        # TODO: validate data

        super().__init__(data=df, name=path, *args, **kwargs)
