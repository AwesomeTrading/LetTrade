from lettrade.exchange.backtest import LetTradeBackTest

from .backtest import lt


def test_optimize(lt: LetTradeBackTest):
    lt.optimize(
        ema1_period=[12, 15],
        ema2_period=[20, 21],
        cache=None,
    )
    results = lt.stats.results
    assert len(results) == 4
