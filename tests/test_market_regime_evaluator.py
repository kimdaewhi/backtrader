import pandas as pd
import pytest
from regime.market_regime_evaluator import MarketRegimeEvaluator
from utils.data_loader import get_stock_data

# 에러나면 PYTHONPATH 설정(Windows)
# set PYTHONPATH=.
# pytest tests/


@pytest.fixture
def evaluator():
    # Sample data for testing
    df = get_stock_data("AAPL", start="2022-01-01", end="2024-12-31")
    evaluator = MarketRegimeEvaluator(df)
    return evaluator


def test_indicators_exist(evaluator):
    # Check if all indicators are calculated
    expected_keys = {
        'ema_fast', 'ema_slow', 'macd', 'cci', 'roc', 
        'adx', 'macd_histogram', 'macd_signal_cross'
    }
    assert set(evaluator.indicators.keys()) == expected_keys, "Not all indicators are calculated."


@pytest.mark.parametrize("key", [
    'ema_fast', 'ema_slow', 'macd', 'cci', 'roc', 
    'adx', 'macd_histogram', 'macd_signal_cross'
])
def test_indicator_is_series(evaluator, key):
    # Check if each indicator is a pandas Series
    assert isinstance(evaluator.indicators[key], pd.Series), f"{key} is not a pandas Series."


@pytest.mark.parametrize("key", [
    'ema_fast', 'ema_slow', 'macd', 'cci', 'roc', 
    'adx', 'macd_histogram', 'macd_signal_cross'
])
def test_indicator_not_all_nan(evaluator, key):
    series = evaluator.indicators[key]
    assert series.notna().any(), f"{key} contains all NaN values."