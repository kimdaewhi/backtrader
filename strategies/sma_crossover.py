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


@staticmethod
def calculate_bb_score_z(current_price, bb_mid, bb_upper, bb_lower, num_std=2):
    """볼린저 밴드 점수 계산"""
    """ current_price: 현재 가격 """
    """ bb_upper: 볼린저 밴드 상단 """
    """ bb_lower: 볼린저 밴드 하단 """
    """ z-score를 이용한 점수 계산 """
    """ 최종적으로 산출된 z-score와 B.B 가중치를 곱하여 -3 ~ 3점으로 변환 """
    bb_width = bb_upper - bb_lower
    if bb_width == 0:
        return 0
    
    std = bb_width / (2 * num_std) # 표준편차 계산
    z = (current_price - bb_mid) / std

    return float(np.clip(z * 3, -3, 3)) # 과매도 최대 3점, 과매수 최소 -3점


class SmaBollingerStrategy(Strategy):
    n1 = 20  # 단기 이동평균 기간(1개월)
    n2 = 60  # 중기 이동평균 기간(3개월(분기))

    # Score 임계값 설정
    buy_threshold = 1.5
    sell_threshold = -1.0

    sma_weight = 0.4  # SMA Crossover 가중치(최대 4점)
    rsi_weight = 0.2  # RSI 가중치(최대 2점)
    bb_weight = 0.3  # 볼린저 밴드 가중치(최대 3점)
    volume_weight = 0.1  # 거래량 가중치(최대 1점)

    def init(self):
        self.sma1 = self.I(SMA, self.data.Close, self.n1)   # 단기 이동평균
        self.sma2 = self.I(SMA, self.data.Close, self.n2)   # 중기 이동평균
        self.bb_mid, self.bb_upper, self.bb_lower = self.I(BollingerBands, self.data.Close) # 볼린저 밴드 중심선 및 상/하단 밴드 
        self.rsi = self.I(RSI, self.data.Close)  # RSI 계산
    
    def calculate_score(self):
        score = 0 # 10점 만점

        # 1. SMA Crossover 점수 계산(가중치 40%)
        # 골든 크로스 -> + 1점, 데드 크로스 -> -1점
        if crossover(self.sma1, self.sma2):  # 골든 크로스(score 범위 : 0 ~ 4)
            if self.sma1[-5] != 0:
                slope = (self.sma1[-1] - self.sma1[-5]) / self.sma1[-5]
                score += np.clip(slope * 100, 0, 4) * self.sma_weight  # 최대 4점 (가중치 반영)

        elif crossover(self.sma2, self.sma1):  # 데드 크로스(score 범위 : -4 ~ 0)
            if self.sma1[-5] != 0:
                slope = (self.sma1[-1] - self.sma1[-5]) / self.sma1[-5]
                score += np.clip(slope * 100, -4, 0) * self.sma_weight  # 최소 -4점


        # 2. 볼린저 밴드 점수 계산(가중치 30%)
        bb_score = calculate_bb_score_z(self.data.Close[-1], self.bb_mid[-1], self.bb_upper[-1], self.bb_lower[-1])
        score += bb_score * self.bb_weight

    
    
    
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
