from indicators.base.ema import EMA

def MACD(close, fast=12, slow=26):
    """MACD 본체 계산"""
    return EMA(close, fast) - EMA(close, slow)


def MACD_and_signal(close, fast=12, slow=26, signal_period=9):
    """MACD + Signal line 반환"""
    macd = MACD(close, fast, slow)
    signal = EMA(macd, signal_period)
    return macd, signal
