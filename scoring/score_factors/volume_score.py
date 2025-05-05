import numpy as np

def calc_volume_score(volume, avg_volume, sensitivity=10):
    """ 거래량 점수 계산 """
    """ volume: 현재 거래량 """
    """ avg_volume: 평균 거래량 """
    """ sensitivity: 민감도 조정 """
    if avg_volume == 0:
        volume_score = 0
    else:
        volume_ratio = (volume - avg_volume) / avg_volume # 평균 거래량 대비 거래량 비율
        volume_score = np.clip(volume_ratio * 10, -1, 1)  # 최대 1점, 최소 -1점

    return volume_score