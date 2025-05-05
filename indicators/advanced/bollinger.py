import pandas as pd
from indicators.base.sma import SMA

def BollingerBands(values, window=20, num_std=2):
    """볼린저밴드 계산"""
    """ values: 종가 시계열 데이터 """
    """ window: 이동평균 기간(일반적으로 20일선 사용) """
    """ num_std: 표준편차 배수 """
    sma = SMA(values, window)
    std = pd.Series(values).rolling(window=window).std()
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    return sma, upper_band, lower_band