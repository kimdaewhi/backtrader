from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd

def SMA(values, window):
    """단순 이동평균 계산"""
    return pd.Series(values).rolling(window=window).mean()

class SmaCross(Strategy):
    n1 = 10  # 단기 이동평균 기간
    n2 = 50  # 장기 이동평균 기간

    def init(self):
        # SMA 지표 등록
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        # 교차점을 기준으로 매수/매도 신호 생성
        # 점선의 시작점은 매수 시점, 끝점은 매도 시점을 나타냄
        if crossover(self.sma1, self.sma2):
            print("🔴매수 신호 발생")
            self.buy(size=5)
        elif crossover(self.sma2, self.sma1):
            print("🔵매도 신호 발생")
            self.sell(size=5)
