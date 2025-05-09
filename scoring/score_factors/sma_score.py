import numpy as np
from utils.logger_xl import write_log, file_score_log
from backtesting.lib import crossover

def calc_sma_score(sma_short, sma_long, sensitivity=1000, sma_weight=0.4, max_spread=0.05, bonus=0.5):
    if len(sma_short) < 6 or sma_short[-5] == 0 or np.isnan(sma_short[-1]) or np.isnan(sma_short[-5]):
        return 0

    # 1. 기울기 계산
    slope = (sma_short[-1] - sma_short[-5]) / sma_short[-5]
    slope_scaled = slope * sensitivity

    # 2. 스프레드 계산
    spread = (sma_short[-1] - sma_long[-1]) / sma_long[-1]

    # 3. 크로스 여부 체크
    if crossover(sma_short, sma_long):
        score = (np.clip(slope_scaled / 25, 0, 4) * sma_weight) + bonus
        write_log(f"👑 [골든크로스] slope: {slope:.5f} | score: {score:.2f}", file_score_log)
    elif crossover(sma_long, sma_short):
        score = (np.clip(slope_scaled / 25, -4, 0) * sma_weight) - bonus
        write_log(f"☠️ [데드크로스] slope: {slope:.5f} | score: {score:.2f}", file_score_log)
    else:
        # ✨ 선형 스프레드 점수화
        spread_score_raw = spread / max_spread  # 예: 0.03/0.05 = 0.6
        spread_score = np.clip(spread_score_raw, -1, 1) * 4 * sma_weight
        score = spread_score
        # print(f"📈 [No Cross] spread: {spread:.5f} | score: {score:.2f}")

    return score