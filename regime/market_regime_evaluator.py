import pandas as pd

class MarketRegimeEvaluator:
    """
    이 클래스는 시장 레짐을 평가하는 데 사용됩니다.
    MarketRegimeEvaluator는 주어진 데이터를 기반으로 시장 레짐을 평가하는 기능을 제공합니다.
    """

    def __init__(self, indicators: dict):
        self.indicators = indicators
    

    # Noise Filtering
    # Noise란 뭘까...?? 뭘로 정의할까...??
    # 예측할 수 없는 변동성인데... 이걸 어떤 지표로 잡아낼 수 있을까...??
    # ATR? ATR 표준편차? z-score?
    def score_noise(
            self, 
            date, 
            window=14, 
            std_threshold=1.5, 
            z_score_threshold=1.5) -> tuple[int, float, float, float]:
        """
        주어진 날짜에 대한 노이즈 점수를 계산합니다.
        노이즈 점수는 ATR 기반 표준편차 + z-score를 사용하여 계산됩니다.
        특정 시점에서 ATR의 절대값 및 z-score를 기준으로 노이즈를 판단합니다.

        Returns:
            1: 노이즈가 감지된 경우(VOLATILE 가능성)
            0: 노이즈가 감지되지 않은 경우(안정적 판단 가능)
        """
        is_noise = 0            # 노이즈 감지 여부
        
        # 1. ATR 시리즈 가져오기
        atr_series = self.indicators['atr']

        if atr_series is None:
            raise ValueError("ATR 시리즈를 찾을 수 없습니다.")
        
        if len(atr_series) < window or date not in atr_series.index:
            return 0, 0.0, 0.0, 0.0    # 판단 불가 -> 일단 안정으로 간주
        
        idx = atr_series.index.get_loc(date)
        if idx < window:
            return 0, 0.0, 0.0, 0.0    # 데이터 부족 -> 판단 불가
        
        # 직전 N일간 ATR 시리즈
        atr_window = atr_series.iloc[idx - window + 1 : idx + 1]
        latest_atr = float(atr_window.iloc[-1])

        # 3. ATR 표준편차 & z-score 계산
        mean = float(atr_window.mean())
        std = float(atr_window.std())
        z_score = float((latest_atr - mean) / std if std != 0 else 0)

        # 4. 노이즈 판단(sigma 임계치보다 크거나 z-score 임계치보다 크면 노이즈로 판단)
        is_noise = int(latest_atr >= std_threshold or abs(z_score) >= z_score_threshold)
        
        return is_noise, float(latest_atr), float(std), float(z_score)