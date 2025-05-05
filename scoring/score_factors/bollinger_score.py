import numpy as np

def calc_bb_score_z(current_price, bb_mid, bb_upper, bb_lower, num_std=2):
    """볼린저 밴드 점수 계산"""
    """ current_price: 현재 가격 """
    """ bb_upper: 볼린저 밴드 상단 """
    """ bb_lower: 볼린저 밴드 하단 """
    """ z-score를 이용한 점수 계산 """
    """ 최종적으로 산출된 z-score와 B.B 가중치를 곱하여 -3 ~ 3점으로 변환 """
    bb_width = bb_upper - bb_lower
    if bb_width == 0:
        return 0
    
    std = bb_width / (2 * num_std) # 표준편차 계산
    z = (current_price - bb_mid) / std

    return float(np.clip(z * 3, -3, 3)) # 과매도 최대 3점, 과매수 최소 -3점
