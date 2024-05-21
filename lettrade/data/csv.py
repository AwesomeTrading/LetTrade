import pandas as pd

from .data import DataFeed


class CSVDataFeed(DataFeed):
    """Implement help to load DataFeed from csv file"""

    def __init__(
        self,
        path: str = None,
        name: str = None,
        delimiter: str = ",",
        index_col: int = 0,
        header: int = 0,
        meta: dict = None,
        data: DataFeed = None,
        *args: list,
        **kwargs: dict,
    ) -> None:
        """_summary_

        Args:
            name (str): Path to csv file
            delimiter (str, optional): _description_. Defaults to ",".
            index_col (int, optional): _description_. Defaults to 0.
            header (int, optional): _description_. Defaults to 0.
            *args (list): [DataFeed](./data.md#lettrade.data.data.DataFeed) list parameters
            **kwargs (dict): [DataFeed](./data.md#lettrade.data.data.DataFeed) dict parameters
        """
        if name is None:
            name = path

        if data is None:
            data = pd.read_csv(
                path,
                index_col=index_col,
                parse_dates=["datetime"],
                delimiter=delimiter,
                header=header,
            )
        # df.reset_index(inplace=True)

        super().__init__(name=name, data=data, meta=meta, *args, **kwargs)
