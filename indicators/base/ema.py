import pandas as pd

def EMA(values, window):
    """지수 이동평균 계산"""
    return pd.Series(values).ewm(span=window, adjust=False).mean()