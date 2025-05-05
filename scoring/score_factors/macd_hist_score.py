import numpy as np

def calc_macd_hist_score(macd, signal) -> float:
    """
    MACD 히스토그램 기반 스코어 계산
    - 결과 점수는 -2 ~ +2 범위로 고정
    """
    hist = macd[-1] - signal[-1]
    hist_score = np.clip(hist * 10, -2, 2)  # 민감도 10배
    return float(hist_score)