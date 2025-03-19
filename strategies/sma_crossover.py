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
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):  # 매수 신호
            if not self.position:
                size = int(self._broker._cash * 0.1 / self.data.Close[-1])  # 정수 변환
                if size > 0:  # size가 양수인지 확인
                    self.buy(size=size)
                    print(f"🔴 [매수] 일자: {self.data.index[-1]}, 금액: {self.data.Close[-1]:.2f}, "
                          f"보유 현금: {self._broker._cash:.2f}, 보유 주식 수량: {self.position.size:.2f}")
        elif crossover(self.sma2, self.sma1):  # 매도 신호
            if self.position:
                size = int(self.position.size * 0.07)  # 보유 주식의 7%만 매도 (정수 변환)
                if size > 0:  # size가 양수인지 확인
                    self.sell(size=size)
                    print(f"🔵 [매도] 일자: {self.data.index[-1]}, 금액: {self.data.Close[-1]:.2f}, "
                          f"보유 현금: {self._broker._cash:.2f}, 보유 주식 수량: {self.position.size:.2f}")
