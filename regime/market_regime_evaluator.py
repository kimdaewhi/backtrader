import pandas as pd

class MarketRegimeEvaluator:
    """
    이 클래스는 시장 레짐을 평가하는 데 사용됩니다.
    MarketRegimeEvaluator는 주어진 데이터를 기반으로 시장 레짐을 평가하는 기능을 제공합니다.
    """

    def __init__(self, indicators: dict):
        self.indicators = indicators
        self._prepare_noise_stats()

    
    def _prepare_noise_stats(self):
        """
        노이즈 통계치를 준비합니다.
        """
        # ATR 시리즈가 없으면 초기화
        atr = self.indicators.get('atr')
        if atr is None:
            raise ValueError("ATR 시리즈를 찾을 수 없습니다.")
        
        self.atr_stats = {
            'mean': atr.mean(),
            'std': atr.std(),
            '90pct': atr.quantile(0.9),
            'zscore_threshold': atr.apply(lambda x: (x - atr.mean()) / atr.std()).quantile(0.9)
        }
    

    # Noise Filtering
    # 급등락 시에는 ATR이 급격히 증가하고, 그에 따라 atr σ와 z-score도 같이 증가함.
    # 때문에 σ와 z-score만을 기준으로 Volatile 판단을 하게 되면
    # 급등락이 발생한 시점에 Volatile로 판단하게 됨. >> 이 경우에는 어떻게??
    def score_noise(
            self, 
            date, 
            window=14) -> tuple[int, float, float, float]:
        """
        주어진 날짜에 대한 노이즈 점수를 계산합니다.
        노이즈 점수는 ATR 기반 표준편차 + z-score를 사용하여 계산됩니다.
        특정 시점에서 ATR의 절대값 및 z-score를 기준으로 노이즈를 판단합니다.

        Returns:
            1: 노이즈가 감지된 경우(VOLATILE 가능성)
            0: 노이즈가 감지되지 않은 경우(안정적 판단 가능)
        """
        atr_series = self.indicators['atr']

        if atr_series is None or date not in atr_series.index:
            return 0, 0.0, 0.0, 0.0, 0.0, 0.0

        idx = atr_series.index.get_loc(date)
        if idx < window:
            return 0, 0.0, 0.0, 0.0, 0.0, 0.0

        atr_until_now = atr_series.iloc[:idx+1]  # ✅ 현재 일자까지 누적된 ATR
        atr_window = atr_series.iloc[idx - window + 1: idx + 1]
        latest_atr = float(atr_window.iloc[-1])

        mean = float(atr_window.mean())
        std = float(atr_window.std())
        z_score = float((latest_atr - mean) / std if std != 0 else 0)

        # ✅ 기준 동적 계산
        dynamic_std_threshold = float(atr_until_now.quantile(0.9))
        dynamic_zscore_threshold = float(
            ((atr_until_now - atr_until_now.mean()) / atr_until_now.std()).quantile(0.9)
        )

        is_noise = int(
            latest_atr >= dynamic_std_threshold or abs(z_score) >= dynamic_zscore_threshold
        )

        return (
            is_noise,
            latest_atr,
            std,
            z_score,
            dynamic_std_threshold,
            dynamic_zscore_threshold,
        )