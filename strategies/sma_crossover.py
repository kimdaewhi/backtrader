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
            if not self.position:  # 포지션이 없을 때만 매수
                size = min(int(self._broker._cash / self.data.Close[-1]), 10)  # 최대 10주 매수
                self.buy(size=size)
                print(f"🔴 [매수] 일자: {self.data.index[-1]}, 금액: {self.data.Close[-1]:.2f}, "
                    f"매수 수량: {size}, 잔여 현금: {self._broker._cash:.2f}, "
                    f"보유 주식 수량: {self.position.size:.2f}")
        elif crossover(self.sma2, self.sma1):  # 매도 신호
            if self.position:  # 포지션이 있을 때만 매도
                size = max(int(self.position.size * 0.07), 1)  # 최소 거래 단위 설정
                self.sell(size=size)
                print(f"🔵 [매도] 일자: {self.data.index[-1]}, 금액: {self.data.Close[-1]:.2f}, "
                    f"매도 수량: {size}, 잔여 현금: {self._broker._cash:.2f}, "
                    f"보유 주식 수량: {self.position.size:.2f}")

