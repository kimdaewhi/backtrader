from indicators.base.ema import EMA
import pandas as pd

def MACD(close, fast=12, slow=26):
    """MACD 본체 계산"""
    return EMA(close, fast) - EMA(close, slow)


def MACD_and_signal(close, fast=12, slow=26, signal_period=9):
    """MACD + Signal line 반환"""
    macd = MACD(close, fast, slow)
    signal = EMA(macd, signal_period)
    return macd, signal


def MACD_histogram(close, fast=12, slow=26, signal_period=9):
    """MACD 히스토그램 반환"""
    macd, signal = MACD_and_signal(close, fast, slow, signal_period)
    return macd - signal

def MACD_signal_crossover(close, fast=12, slow=26, signal_period=9):
    """
    MACD와 Signal line의 크로스오버 포인트 반환
    0 : 크로스오버 없음
    1 : 골든 크로스  (Signal line을 아래에서 위로 상향 돌파)
    -1 : 데드 크로스 (Signal line을 위에서 아래로 하향 돌파)
    """
    macd, signal = MACD_and_signal(close, fast, slow, signal_period)
    crossover = pd.Series(0, index=close.index)
    crossover[(macd.shift(1) < signal.shift(1)) & (macd > signal)] = 1  # Bullish crossover
    crossover[(macd.shift(1) > signal.shift(1)) & (macd < signal)] = -1 # Bearish crossover
    
    return crossover