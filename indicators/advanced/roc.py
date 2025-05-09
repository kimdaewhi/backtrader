import pandas as pd

def ROC(close, window=14):
    """
    ROC (Rate of Change) 계산
    :param close: 종가 시리즈
    :param window: 윈도우 크기 (기본값: 14)
    현재 가격과 n일 전 가격의 비율을 계산하여 주가의 변동성을 나타냄(모멘텀 기반 방향성 지표)
    :return: ROC 시리즈
    """
    close = pd.Series(close)
    # 현재 가격과 n일 전 가격의 비율 계산
    roc = (close - close.shift(window)) / close.shift(window) * 100
    
    return roc