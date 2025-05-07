import pandas as pd
from market_regime import MarketRegime
from indicators.base import SMA, EMA
from indicators.advanced import MACD_and_signal, MACD_signal_crossover, CCI, ROC, ADX

class MarketRegimeEvaluator:
    """
    이 클래스는 시장 레짐을 평가하는 데 사용됩니다.
    MarketRegimeEvaluator는 주어진 데이터를 기반으로 시장 레짐을 평가하는 기능을 제공합니다.
    """

    def __init__(
        self, 
        df: pd.DataFrame,
        ema_fast_period: int = 12,
        ema_slow_period: int = 26,
        cci_window: int = 14,
        adx_period: int = 14,
        roc_window: int = 14,
        macd_signal_period: int = 9,
    ):
        self.df = df
        self.ema_fast_period = ema_fast_period
        self.ema_slow_period = ema_slow_period
        self.cci_window = cci_window
        self.adx_period = adx_period
        self.roc_window = roc_window
        self.macd_signal_period = macd_signal_period

        self.indicators = self._calculate_indicators()
    

    def _calculate_indicators(self):
        # OHLC
        open = self.df["Open"]
        high = self.df["High"]
        low = self.df["Low"]
        close = self.df["Close"]
        volume = self.df["Volume"]

        ema_fast = EMA(close, self.ema_fast_period)
        ema_slow = EMA(close, self.ema_slow_period)
        macd, signal = MACD_and_signal(close, self.ema_fast_period, self.ema_slow_period, self.macd_signal_period)
        cci = CCI(high, low, close, self.cci_window)
        roc = ROC(close, self.roc_window)
        adx = ADX(high, low, close, self.adx_period)
        macd_histogram = macd - signal
        macd_signal_cross = MACD_signal_crossover(close, self.ema_fast_period, self.ema_slow_period, self.macd_signal_period)


        return {
            'ema_fast': ema_fast,
            'ema_slow': ema_slow,
            'macd': macd,
            'cci': cci,
            'roc': roc,
            'adx': adx,
            'macd_histogram': macd_histogram,
            'macd_signal_cross': macd_signal_cross,
        }
    
    
    
    
    
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