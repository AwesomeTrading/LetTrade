import pandas as pd

from .data import DataFeed


class CSVDataFeed(DataFeed):
    """Implement help to load DataFeed from csv file"""

    def __init__(
        self,
        path: str,
        delimiter: str = ",",
        index_col: int = 0,
        header: int = 0,
        *args: list,
        **kwargs: dict,
    ) -> None:
        """_summary_

        Args:
            path (str): Path of csv file
            delimiter (str, optional): _description_. Defaults to ",".
            index_col (int, optional): _description_. Defaults to 0.
            header (int, optional): _description_. Defaults to 0.
            *args (list): [DataFeed](./data.md#lettrade.data.data.DataFeed) list parameters
            **kwargs (dict): [DataFeed](./data.md#lettrade.data.data.DataFeed) dict parameters
        """
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
