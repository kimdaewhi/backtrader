import pandas as pd
from regime.market_regime import MarketRegime
from indicators.base import EMA, ATR
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
        """
        Private like 메서드
        입력된 yfinance 데이터(df)를 기반으로 시장 레짐 판단에 필요한 보조지표들을 계산하여 반환합니다.
        반환값: dict 형태의 지표 결과
        {
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
        # OHLCV
        open = self.df["Open"]
        high = self.df["High"]
        low = self.df["Low"]
        close = self.df["Close"]
        volume = self.df["Volume"]

        # 방향성 및 추세 판단용 보조지표 계산
        ema_fast = EMA(close, self.ema_fast_period) # 단기 EMA(12일)
        ema_slow = EMA(close, self.ema_slow_period) # 장기 EMA(26일)
        
        # MACD 계산: 추세 전환 및 방향 감지
        macd, signal = MACD_and_signal(close, self.ema_fast_period, self.ema_slow_period, self.macd_signal_period)

        # CCI 계산: 평균 가격과의 괴리로 과열/과매도 판단 + 방향성 감지
        cci = CCI(high, low, close, self.cci_window)

        # ROC 계산: 가격 변화율로 모멘텀 판단 + 방향성 감지
        roc = ROC(close, self.roc_window)

        # ADX 계산: 추세 강도 판단(방향성 x, 순수 추세 강도)
        adx = ADX(high, low, close, self.adx_period)

        # MACD 히스토그램 계산: MACD - Signal -> 추세 강도 시각화
        macd_histogram = macd - signal

        # MACD 시그널 라인 크로스오버: 추세 전환 시점 포착 (1: 골든크로스, -1: 데드크로스)
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
    

    # Noise Filtering
    # Noise란 뭘까...?? 뭘로 정의할까...??
    # 예측할 수 없는 변동성인데... 이걸 어떤 지표로 잡아낼 수 있을까...??
    # ATR? ATR 표준편차? z-score?
    def score_noise(self, date, window=14, std_threshold=1.5, z_score_threshold=1.5) -> int:
        """
        주어진 날짜에 대한 노이즈 점수를 계산합니다.
        노이즈 점수는 ATR 기반 표준편차 + z-score를 사용하여 계산됩니다.
        특정 시점에서 ATR의 절대값 및 z-score를 기준으로 노이즈를 판단합니다.

        Returns:
            1: 노이즈가 감지된 경우(VOLATILE 가능성)
            0: 노이즈가 감지되지 않은 경우(안정적 판단 가능)
        """
        is_noise = 0            # 노이즈 감지 여부
        high = self.df["High"]
        low = self.df["Low"]
        close = self.df["Close"]

        # 1. ATR 계산
        atr_series = ATR(high, low, close, window)

        # 2. ATR 슬라이스
        if len(atr_series) < window or date not in atr_series.index:
            return 0    # 판단 불가 -> 일단 안정으로 간주
        
        idx = atr_series.index.get_loc(date)
        if idx < window:
            return 0    # 데이터 부족 -> 판단 불가
        
        atr_window = atr_series.iloc[idx - window + 1 : idx + 1]
        latest_atr = atr_window.iloc[-1]

        # 3. ATR 표준편차 & z-score 계산
        mean = atr_window.mean()
        std = atr_window.std()
        z_score = (latest_atr - mean) / std if std != 0 else 0

        # 4. 노이즈 판단
        if latest_atr >= std_threshold or abs(z_score) >= z_score_threshold:
            is_noise = 1
        
        return is_noise, latest_atr, std, z_score