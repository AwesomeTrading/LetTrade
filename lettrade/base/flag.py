if __debug__:
    validate_strategy_trade: bool = False
    """Flag to validate trading object is not writing attribute from strategy"""
    validate_data_getitem_pointer: bool = False
    """Flag to validate `DataFeed` get data by pointer but doesn't has prefix `DataFeed.l.`"""
