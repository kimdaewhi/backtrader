import pandas as pd

def golden_cross(short, long):
    """
    골든 크로스: 단기선이 장기선을 아래에서 위로 돌파
    :return: 골든 크로스 1, 크로스 없음 0
    """
    crossover = pd.Series(0, index=short.index)
    crossover[(short.shift(1) < long.shift(1)) & (short > long)] = 1
    return crossover

def dead_cross(short, long):
    """
    데드 크로스: 단기선이 장기선을 위에서 아래로 돌파
    :return: 데드 크로스 -1, 크로스 없음 0
    """
    crossover = pd.Series(0, index=short.index)
    crossover[(short.shift(1) > long.shift(1)) & (short < long)] = -1
    return crossover