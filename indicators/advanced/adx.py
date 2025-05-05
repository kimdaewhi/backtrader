import pandas as pd

def ADX(high, low, close, period=14):
    """ADX 계산"""
    """ high: 고가 시계열 데이터 """
    """ low: 저가 시계열 데이터 """
    """ close: 종가 시계열 데이터 """
    """ period: ADX 계산 기간(일반적으로 14일 사용) """
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)

    plus_dm = high.diff()
    minus_dm = low.diff().abs()

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(window=period).mean()

    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    dx = (abs(plus_di - minus_di)/ (plus_di + minus_di)) * 100
    adx = dx.rolling(window=period).mean()

    return adx