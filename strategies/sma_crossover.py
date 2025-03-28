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
def calculate_sma_score(sma_short, sma_long, sensitivity=1000, sma_weight=0.4, max_spread=0.05, bonus=0.5):
    if len(sma_short) < 6 or sma_short[-5] == 0 or np.isnan(sma_short[-1]) or np.isnan(sma_short[-5]):
        return 0

    # 1. 기울기 계산
    slope = (sma_short[-1] - sma_short[-5]) / sma_short[-5]
    slope_scaled = slope * sensitivity

    # 2. 스프레드 계산
    spread = (sma_short[-1] - sma_long[-1]) / sma_long[-1]

    # 3. 크로스 여부 체크
    if crossover(sma_short, sma_long):
        score = (np.clip(slope_scaled / 25, 0, 4) * sma_weight) + bonus
        print(f"👑 [골든크로스] slope: {slope:.5f} | score: {score:.2f}")
    elif crossover(sma_long, sma_short):
        score = (np.clip(slope_scaled / 25, -4, 0) * sma_weight) - bonus
        print(f"☠️ [데드크로스] slope: {slope:.5f} | score: {score:.2f}")
    else:
        # ✨ 선형 스프레드 점수화
        spread_score_raw = spread / max_spread  # 예: 0.03/0.05 = 0.6
        spread_score = np.clip(spread_score_raw, -1, 1) * 4 * sma_weight
        score = spread_score
        # print(f"📈 [No Cross] spread: {spread:.5f} | score: {score:.2f}")

    return score




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
    n1 = 5  # 단기 이동평균 기간
    n2 = 20  # 중기 이동평균 기간

    # Score 임계값 설정
    buy_threshold = 2.0
    sell_threshold = -1.5

    sma_weight = 0.4  # SMA Crossover 가중치(최대 4점)
    bb_weight = 0.3  # 볼린저 밴드 가중치(최대 3점)
    # rsi_weight = 0.2  # RSI 가중치(최대 2점)
    # volume_weight = 0.1  # 거래량 가중치(최대 1점)

    def init(self):
        """ 초기화 """
        self.sma1 = self.I(SMA, self.data.Close, self.n1, overlay=True)   # 단기 이동평균
        self.sma2 = self.I(SMA, self.data.Close, self.n2, overlay=True)   # 중기 이동평균
        self.bb_mid, self.bb_upper, self.bb_lower = self.I(BollingerBands, self.data.Close, overlay=True) # 볼린저 밴드 중심선 및 상/하단 밴드 
        self.rsi = self.I(RSI, self.data.Close, overlay=False)  # RSI 계산
    

    def calculate_score(self):
        """ 매수/매도 판단을 위한 스코어링 엔진 - 각 지표의 Signal을 Score로 계산 """
        """ SMA Crossover, 볼린저 밴드, RSI, Volume을 종합하여 종목별 점수 산출 """
        """ Score Scale 기준 : -10 ~ 10점 """
        """ 가중치 : SMA Crossover(40%), 볼린저 밴드(30%), RSI(20%), Volume(10%) """

        score = 0           # 총합 Score
        sma_score = 0       # SMA Crossover Score
        bb_score = 0        # Bolinger Band Score
        rsi_score = 0       # RSI Score
        volume_score = 0    # Volume Score

        # ✅ 1. SMA Crossover 점수 계산(가중치 40%)
        sma_sentivity = 800  # ⭐ 변화율 가중치
        sma_score = calculate_sma_score(self.sma1, self.sma2, sma_sentivity, self.sma_weight)
        score += sma_score


        # ✅ 2. 볼린저 밴드 점수 계산(가중치 30%)
        bb_score_row = calculate_bb_score_z(self.data.Close[-1], self.bb_mid[-1], self.bb_upper[-1], self.bb_lower[-1])
        bb_score += bb_score_row * self.bb_weight
        score += bb_score


        # ✅ 3. RSI 점수 계산(가중치 20%)
        # RSI 20 이하 -> -2점, RSI 80 이상 -> -2점
        rsi_value = self.rsi[-1]
        if rsi_value < 20:
            rsi_score = 2.0
        elif rsi_value < 30:
            rsi_score = 1.0
        elif rsi_value > 80:
            rsi_score = -2.0
        elif rsi_value > 70:
            rsi_score = -1.0
        else:
            rsi_score = 0.0

        score += rsi_score


        # ✅ 4. 거래량 점수 계산(가중치 10%)
        volume = self.data.Volume[-1]
        avg_volume = pd.Series(self.data.Volume).rolling(window=20).mean().iloc[-1] # 20일 평균 거래량 계산
        
        if avg_volume == 0:
            volume_score = 0
        else:
            volume_ratio = (volume - avg_volume) / avg_volume # 평균 거래량 대비 거래량 비율
            volume_score = np.clip(volume_ratio * 10, -1, 1)  # 최대 1점, 최소 -1점
        score += volume_score

        # 최종 스코어링 결과 출력
        print(
            f"📅 [{self.data.index[-1].strftime('%Y.%m.%d')}] | "
            f"SMA: {sma_score:>5.2f} | "
            f"BB: {bb_score:>5.2f} | "
            f"RSI: {rsi_score:>5.2f} | "
            f"VOL: {volume_score:>5.2f} | "
            f"TOTAL: {score:>5.2f}"
        )

        return score

    
    
    
    # def next(self):
    #     # 현재 포지션의 평균 매수가 계산 (포지션이 있을 경우)
    #     if self.position:
    #         avg_entry_price = (self.position.pl + self.position.size * self.data.Close[-1]) / self.position.size
    #     else:
    #         avg_entry_price = None

    #     # ✅ 매수 조건:
    #     # 1) SMA 20이 SMA 50을 상향 돌파 OR 볼린저 밴드 하단 근처
    #     # 2) 현재 가격이 볼린저 밴드 하단보다 5% 이내 거리
    #     if (crossover(self.sma1, self.sma2) or self.data.Close[-1] < self.bb_lower[-1] * 1.05):
    #         max_size = int(self._broker._cash / self.data.Close[-1])  # 최대 구매 가능 수량
    #         size = min(max_size, 5)  # 최대 5주까지 매수
    #         if size >= 1:  # ✅ 최소 1주 이상 매수 보장
    #             self.buy(size=size)
    #             print(f"🔴 [매수] {self.data.index[-1]} | 가격: {self.data.Close[-1]:.2f}, "
    #                   f"매수 수량: {size}, 잔여 현금: {self._broker._cash:.2f}")

    #     # ✅ 매도 조건:
    #     # 1) SMA 20이 SMA 50을 하향 돌파 OR 볼린저 밴드 상단 근처
    #     # 2) 현재 가격이 볼린저 밴드 상단보다 5% 이내 거리
    #     if self.position.size > 0:  # ✅ 보유 주식이 있을 때만 매도
    #         if (crossover(self.sma2, self.sma1) or self.data.Close[-1] > self.bb_upper[-1] * 0.95):
    #             size = max(int(self.position.size * 0.07), 1)  # ✅ 최소 1주 보장
    #             size = min(size, self.position.size)  # ✅ 포지션보다 많이 매도하지 않도록 제한
    #             if size >= 1:  # ✅ 최소 1주 이상 매도 보장
    #                 self.sell(size=size)
    #                 print(f"🔵 [매도] {self.data.index[-1]} | 가격: {self.data.Close[-1]:.2f}, "
    #                       f"매도 수량: {size}, 잔여 현금: {self._broker._cash:.2f}")

    #     # ✅ 손절 (-7%) 및 익절 (+15%)
    #     if self.position and avg_entry_price:
    #         if self.data.Close[-1] / avg_entry_price < 0.93:  # 손절 기준
    #             size = max(int(self.position.size), 1)  # ✅ 최소 1주 보장
    #             self.sell(size=size)  # 보유 주식 전량 매도
    #             print(f"⚠️ [손절] {self.data.index[-1]} | 가격: {self.data.Close[-1]:.2f} | 보유 주식 전량 매도")

    #         if self.data.Close[-1] / avg_entry_price > 1.15:  # 익절 기준
    #             size = max(int(self.position.size), 1)  # ✅ 최소 1주 보장
    #             self.sell(size=size)  # 보유 주식 전량 매도
    #             print(f"✅ [익절] {self.data.index[-1]} | 가격: {self.data.Close[-1]:.2f} | 보유 주식 전량 매도")

    def next(self):
        score = self.calculate_score()