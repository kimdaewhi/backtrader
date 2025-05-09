import pandas as pd

def ATR(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """
    ATR (Average True Range) 계산
    :param high: 고가 시리즈
    :param low: 저가 시리즈
    :param close: 종가 시리즈
    :param window: ATR 계산 윈도우 (기본값 14)
    :return: ATR 값 시리즈
    """
    # 이전 종가
    prev_close = close.shift(1)

    # True Range 계산
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # ATR = TR의 이동 평균
    atr = tr.rolling(window=window, min_periods=1).mean()
    return atr
