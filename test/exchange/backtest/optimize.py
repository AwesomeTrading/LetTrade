import pytest

from lettrade.exchange.backtest import LetTradeBackTest

from .backtest import lt


@pytest.fixture
def backtest_lt(lt: LetTradeBackTest):
    lt: LetTradeBackTest = lt()
    lt.run()
    return lt


def test_optimize(lt: LetTradeBackTest, backtest_lt: LetTradeBackTest):
    lt = lt()
    lt.optimize(
        ema1_window=[9, 12, 15],
        ema2_window=[20, 21],
        cache=None,
    )
    results = lt.stats.results

    assert len(results) == 6

    for result in results:
        if (
            result["optimize"]["ema1_window"] == backtest_lt._bot.strategy.ema1_window
            and result["optimize"]["ema2_window"]
            == backtest_lt._bot.strategy.ema2_window
        ):
            backtest_result = backtest_lt.stats.result
            result = result["result"]
            assert result.start == backtest_result.start
            assert result.end == backtest_result.end
            assert result.positions == backtest_result.positions
            assert result.equity == backtest_result.equity
            assert result.duration == backtest_result.duration

            return

    assert False
