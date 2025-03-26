from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np

def SMA(values, window):
    """단순 이동평균 계산"""
    return pd.Series(values).rolling(window=window).mean()

def BollingerBands(values, window=20, num_std=2):
    """볼린저밴드 계산"""
    """ values: 종가 시계열 데이터 """
    """ window: 이동평균 기간(일반적으로 20일선 사용) """
    """ num_std: 표준편차 배수 """
    sma = SMA(values, window)
    std = pd.Series(values).rolling(window=window).std()
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    return sma, upper_band, lower_band

def RSI(values, window=14):
    """RSI 계산"""
    """ values: 종가 시계열 데이터 """
    """ window: RSI 계산 기간(일반적으로 14일 사용) """
    delta = pd.Series(values).diff()    # 종가 차이 계산
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))
    avg_gain = gain.rolling(window=window).mean()   # 직전 window일간의 평균 상승폭
    avg_loss = loss.rolling(window=window).mean()   # 직전 window일간의 평균 하락폭
    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))   # RSI 계산

class SmaBollingerStrategy(Strategy):
    n1 = 20  # 단기 이동평균 기간(1개월)
    n2 = 60  # 장기 이동평균 기간(반기)

    def init(self):
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)
        self.bb_mid, self.bb_upper, self.bb_lower = self.I(BollingerBands, self.data.Close)

    def next(self):
        # 현재 포지션의 평균 매수가 계산 (포지션이 있을 경우)
        if self.position:
            avg_entry_price = (self.position.pl + self.position.size * self.data.Close[-1]) / self.position.size
        else:
            avg_entry_price = None

        # ✅ 매수 조건:
        # 1) SMA 20이 SMA 50을 상향 돌파 OR 볼린저 밴드 하단 근처
        # 2) 현재 가격이 볼린저 밴드 하단보다 5% 이내 거리
        if (crossover(self.sma1, self.sma2) or self.data.Close[-1] < self.bb_lower[-1] * 1.05):
            max_size = int(self._broker._cash / self.data.Close[-1])  # 최대 구매 가능 수량
            size = min(max_size, 5)  # 최대 5주까지 매수
            if size >= 1:  # ✅ 최소 1주 이상 매수 보장
                self.buy(size=size)
                print(f"🔴 [매수] {self.data.index[-1]} | 가격: {self.data.Close[-1]:.2f}, "
                      f"매수 수량: {size}, 잔여 현금: {self._broker._cash:.2f}")

        # ✅ 매도 조건:
        # 1) SMA 20이 SMA 50을 하향 돌파 OR 볼린저 밴드 상단 근처
        # 2) 현재 가격이 볼린저 밴드 상단보다 5% 이내 거리
        if self.position.size > 0:  # ✅ 보유 주식이 있을 때만 매도
            if (crossover(self.sma2, self.sma1) or self.data.Close[-1] > self.bb_upper[-1] * 0.95):
                size = max(int(self.position.size * 0.07), 1)  # ✅ 최소 1주 보장
                size = min(size, self.position.size)  # ✅ 포지션보다 많이 매도하지 않도록 제한
                if size >= 1:  # ✅ 최소 1주 이상 매도 보장
                    self.sell(size=size)
                    print(f"🔵 [매도] {self.data.index[-1]} | 가격: {self.data.Close[-1]:.2f}, "
                          f"매도 수량: {size}, 잔여 현금: {self._broker._cash:.2f}")

        # ✅ 손절 (-7%) 및 익절 (+15%)
        if self.position and avg_entry_price:
            if self.data.Close[-1] / avg_entry_price < 0.93:  # 손절 기준
                size = max(int(self.position.size), 1)  # ✅ 최소 1주 보장
                self.sell(size=size)  # 보유 주식 전량 매도
                print(f"⚠️ [손절] {self.data.index[-1]} | 가격: {self.data.Close[-1]:.2f} | 보유 주식 전량 매도")

            if self.data.Close[-1] / avg_entry_price > 1.15:  # 익절 기준
                size = max(int(self.position.size), 1)  # ✅ 최소 1주 보장
                self.sell(size=size)  # 보유 주식 전량 매도
                print(f"✅ [익절] {self.data.index[-1]} | 가격: {self.data.Close[-1]:.2f} | 보유 주식 전량 매도")
