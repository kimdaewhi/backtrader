import pandas as pd

def CCI(high, low, close, window=14):
    """
    CCI (Commodity Channel Index) 계산
    :param high: 고가 시리즈
    :param low: 저가 시리즈
    :param close: 종가 시리즈
    :param window: 윈도우 크기 (기본값: 14)
    가격이 평균에서 얼마나 벗어났는지를 나타내는 지표로, 과매수/과매도 상태를 판단하는 데 사용됨
    주로 추세가 시작될 때나 과열/과매도 상태를 판단하는 데 유용함
    :return: CCI 시리즈
    """
    tp = (high + low + close) / 3
    sma = pd.Series(tp).rolling(window=window).mean()
    mean_dev = (pd.Series(tp) - sma).abs().rolling(window=window).mean()
    cci = (tp - sma) / (0.015 * mean_dev)
    
    return cci
