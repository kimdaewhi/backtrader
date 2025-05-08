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


def test_score_noise_across_dates(evaluator):
    """
    score_noise 함수 테스트
    - 최근 10일간 날짜별 노이즈 점수 출력
    - ATR / std / z-score를 기반으로 판단된 결과를 확인
    """
    # 테스트할 날짜 리스트 (가장 최근 10개)
    dates = evaluator.df.index[0:60]

    print("\n🧪 [score_noise 테스트 - 최근 10일]")

    for date in dates:
        score = evaluator.score_noise(date)
        print(f"{date.date()} ➤ 노이즈 점수: {score}")

    # assert로 최소 하나 이상은 0 또는 1 나오는지 확인 (완전 실패 방지용)
    scores = [evaluator.score_noise(date) for date in dates]
    assert any(score in [0, 1] for score in scores)
