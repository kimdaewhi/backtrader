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
        # 매수 조건: SMA 10이 SMA 50을 상향 돌파할 때 추가적으로 매수 가능
        if crossover(self.sma1, self.sma2):
            size = min(int(self._broker._cash / self.data.Close[-1]), 5)  # 최대 5주 추가 매수
            if size > 0:
                self.buy(size=size)
                print(f"🔴 [매수] 일자: {self.data.index[-1]}, 금액: {self.data.Close[-1]:.2f}, "
                    f"매수 수량: {size}, 잔여 현금: {self._broker._cash:.2f}, "
                    f"보유 주식 수량: {self.position.size:.2f}")

        # 매도 조건: SMA 10이 SMA 50을 하향 돌파할 때 한 번만 매도
        if crossover(self.sma2, self.sma1):
            size = max(int(self.position.size * 0.07), 1)  # 최소 거래 단위 설정
            if size > 0:
                self.sell(size=size)
                print(f"🔵 [매도] 일자: {self.data.index[-1]}, 금액: {self.data.Close[-1]:.2f}, "
                    f"매도 수량: {size}, 잔여 현금: {self._broker._cash:.2f}, "
                    f"보유 주식 수량: {self.position.size:.2f}")

