from market_regime import MarketRegime
from indicators.base import SMA, EMA
from indicators.advanced import MACD_and_signal, CCI, ROC, ADX

class MarketRegimeEvaluator:
    """
    이 클래스는 시장 레짐을 평가하는 데 사용됩니다.
    MarketRegimeEvaluator는 주어진 데이터를 기반으로 시장 레짐을 평가하는 기능을 제공합니다.
    """

    def __init__(self, indicators: dict):
        """
        indicators: {
            'ema_fast': pd.Series,
            'ema_slow': pd.Series,
            'macd': pd.Series,
            'cci': pd.Series,
            'roc': pd.Series,
            'adx': pd.Series,
            'macd_histogram': pd.Series,
            'macd_signal_cross': pd.Series
        }
        """
        self.indicators = indicators
    

    def score_direction(self, date) -> int:
        """
        방향성 점수 계산
        :param date: 평가할 날짜
        :return: 방향성 점수 (0: 약세, 1: 중립, 2: 강세)
        """
        ema_fast = self.indicators['ema_fast'].loc[date]
        ema_slow = self.indicators['ema_slow'].loc[date]

        if ema_fast > ema_slow:
            return 2