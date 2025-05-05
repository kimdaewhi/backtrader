import numpy as np

def calc_ema_adx_score(ema_short, ema_long, adx_values, sensitivity=800):
    """
    EMA 간 스프레드 + ADX 추세 강도 기반 스코어 계산
    - EMA 점수 (60%), ADX 점수 (40%) 합산
    - 최종 점수는 -4 ~ 4 범위로 조정
    """
    if (
        len(ema_short) < 1 or len(ema_long) < 1 or len(adx_values) < 1 or
        np.isnan(ema_short[-1]) or np.isnan(ema_long[-1]) or np.isnan(adx_values[-1])
    ):
        return 0.0

    # ✅ EMA 스프레드 계산
    spread = (ema_short[-1] - ema_long[-1]) / ema_long[-1]
    spread_scaled = spread * sensitivity
    ema_score = np.clip(spread_scaled, -2.4, 2.4)

    # ✅ ADX 점수 계산
    adx_value = adx_values[-1]
    if adx_value >= 25:
        adx_score = 1.6
    elif adx_value <= 15:
        adx_score = -1.6
    else:
        normalized = (adx_value - 15) / 10
        adx_score = (normalized * 3.2) - 1.6

    total_score = ema_score + adx_score
    return float(np.clip(total_score, -4.0, 4.0))
