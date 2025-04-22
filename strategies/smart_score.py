from backtesting import Strategy
from backtesting.lib import crossover
from utils.logger import write_log, write_log_xlsx
from config.config import PathConfig, backtesting_config
import pandas as pd
import numpy as np

file_score_log = f"{backtesting_config.SYMBOL}_{PathConfig.XLSX_SCORE_LOG}"
file_trading_log = f"{backtesting_config.SYMBOL}_{PathConfig.XLSX_TRADING_LOG}"


score_log_record = []   # 스코어 로그 기록용 DataFrame
trading_log_record = [] # 거래 로그 기록용 DataFrame


def SMA(values, window):
    """단순 이동평균 계산"""
    return pd.Series(values).rolling(window=window).mean()

def EMA(values, window):
    """지수 이동평균 계산"""
    return pd.Series(values).ewm(span=window, adjust=False).mean()

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

def ADX(high, low, close, period=14):
    """ADX 계산"""
    """ high: 고가 시계열 데이터 """
    """ low: 저가 시계열 데이터 """
    """ close: 종가 시계열 데이터 """
    """ period: ADX 계산 기간(일반적으로 14일 사용) """
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)

    plus_dm = high.diff()
    minus_dm = low.diff().abs()

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(window=period).mean()

    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    dx = (abs(plus_di - minus_di)/ (plus_di + minus_di)) * 100
    adx = dx.rolling(window=period).mean()

    return adx


def MACD_and_signal(close):
    """MACD 및 시그널 계산"""
    """ close: 종가 시계열 데이터 """
    macd = EMA(close, 12) - EMA(close, 26)
    signal = EMA(macd, 9)
    return macd, signal



@staticmethod
def calc_sma_score(sma_short, sma_long, sensitivity=1000, sma_weight=0.4, max_spread=0.05, bonus=0.5):
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
        write_log(f"👑 [골든크로스] slope: {slope:.5f} | score: {score:.2f}", file_score_log)
    elif crossover(sma_long, sma_short):
        score = (np.clip(slope_scaled / 25, -4, 0) * sma_weight) - bonus
        write_log(f"☠️ [데드크로스] slope: {slope:.5f} | score: {score:.2f}", file_score_log)
    else:
        # ✨ 선형 스프레드 점수화
        spread_score_raw = spread / max_spread  # 예: 0.03/0.05 = 0.6
        spread_score = np.clip(spread_score_raw, -1, 1) * 4 * sma_weight
        score = spread_score
        # print(f"📈 [No Cross] spread: {spread:.5f} | score: {score:.2f}")

    return score


@staticmethod
def calc_bb_score_z(current_price, bb_mid, bb_upper, bb_lower, num_std=2):
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


@staticmethod
def calc_rsi_score(rsi_value):
    """ RSI 점수 계산 """
    """ rsi_value: RSI 값 """
    """ RSI 20 이하 -> -2점, RSI 80 이상 -> -2점 """
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

    return rsi_score


@staticmethod
def calc_volume_score(volume, avg_volume, sensitivity=10):
    """ 거래량 점수 계산 """
    """ volume: 현재 거래량 """
    """ avg_volume: 평균 거래량 """
    """ sensitivity: 민감도 조정 """
    if avg_volume == 0:
        volume_score = 0
    else:
        volume_ratio = (volume - avg_volume) / avg_volume # 평균 거래량 대비 거래량 비율
        volume_score = np.clip(volume_ratio * 10, -1, 1)  # 최대 1점, 최소 -1점

    return volume_score


@staticmethod
def calc_ema_adx_score(ema_short, ema_long, adx_values, sensitivity=800):
    """
    EMA 간 스프레드 + ADX 추세 강도 기반 스코어 계산
    - EMA 점수 (60%), ADX 점수 (40%) 합산
    - 최종 점수는 -4 ~ 4 범위로 조정
    """
    if (
        len(ema_short) < 1 or len(ema_long) < 1 or len(adx_values) < 1 or
        np.isnan(ema_short[-1]) or np.isnan(ema_long[-1]) or np.isnan(adx_values[-1])
    ):
        return 0.0

    # ✅ EMA 스프레드 계산
    spread = (ema_short[-1] - ema_long[-1]) / ema_long[-1]
    spread_scaled = spread * sensitivity
    ema_score = np.clip(spread_scaled, -2.4, 2.4)  # EMA는 전체의 60%

    # ✅ ADX 점수 계산
    adx_value = adx_values[-1]
    if adx_value >= 25:
        adx_score = 1.6  # 40% of 4
    elif adx_value <= 15:
        adx_score = -1.6
    else:
        normalized = (adx_value - 15) / 10  # 0~1 범위
        adx_score = (normalized * 3.2) - 1.6  # -1.6 ~ +1.6

    # ✅ 최종 스코어: -4 ~ +4
    total_score = ema_score + adx_score
    return float(np.clip(total_score, -4.0, 4.0))



@staticmethod
def calc_macd_hist_score(macd, signal) -> float:
    """
    MACD 히스토그램 기반 스코어 계산
    - 결과 점수는 -2 ~ +2 범위로 고정
    """
    hist = macd[-1] - signal[-1]
    hist_score = np.clip(hist * 10, -2, 2)  # 민감도 10배
    return float(hist_score)


class SmartScore(Strategy):
    n1 = 12  # 단기 이동평균 기간
    n2 = 26  # 중기 이동평균 기간

    # Score 임계값 설정
    buy_threshold = 1.5
    sell_threshold = -1.5

    # sma_weight = 0.4  # SMA Crossover 가중치(최대 4점)
    # bb_weight = 0.3  # 볼린저 밴드 가중치(최대 3점)
    # rsi_weight = 0.2  # RSI 가중치(최대 2점)
    # volume_weight = 0.1  # 거래량 가중치(최대 1점)

    def init(self):
        """ 초기화 """
        # self.sma1 = self.I(SMA, self.data.Close, self.n1, overlay=True)   # 단기 이동평균
        # self.sma2 = self.I(SMA, self.data.Close, self.n2, overlay=True)   # 중기 이동평균
        # self.bb_mid, self.bb_upper, self.bb_lower = self.I(BollingerBands, self.data.Close, overlay=True)
        self.ema1 = self.I(EMA, self.data.Close, self.n1, overlay=True)                         # 단기 EMA(12일선)
        self.ema2 = self.I(EMA, self.data.Close, self.n2, overlay=True)                         # 중기 EMA(26일선)
        self.adx = self.I(ADX, self.data.High, self.data.Low, self.data.Close, overlay=False)   # ADX 계산
        self.rsi = self.I(RSI, self.data.Close, overlay=False)                                  # RSI 계산
        self.macd, self.signal = self.I(MACD_and_signal, self.data.Close, name='MACD', overlay=False)  # MACD 계산
    

    def calculate_score(self):
        """ 매수/매도 판단을 위한 스코어링 엔진 - 각 지표의 Signal을 Score로 계산 """
        """ SMA Crossover, 볼린저 밴드, RSI, Volume을 종합하여 종목별 점수 산출 """
        """ Score Scale 기준 : -10 ~ 10점 """
        """ 가중치 : SMA Crossover(40%), 볼린저 밴드(30%), RSI(20%), Volume(10%) """

        score = 0           # 총합 Score
        ema_adx_score = 0   # EMA Crossover + ADX Score
        macd_score = 0      # MACD Score
        rsi_score = 0       # RSI Score
        volume_score = 0    # Volume Score

        # ✅ 1. EMA Crossover 점수 계산(가중치 40%)
        ema_adx_score = calc_ema_adx_score(self.ema1, self.ema2, self.adx)
        score += ema_adx_score

        # ✅ 2. MACD 히스토그램 점수(가중치 20%)
        macd_score = calc_macd_hist_score(self.macd, self.signal)
        score += macd_score


        # ✅ 3. RSI 점수 계산(가중치 20%)
        # RSI 20 이하 -> -2점, RSI 80 이상 -> -2점
        rsi_score = calc_rsi_score(self.rsi[-1])
        score += rsi_score


        # ✅ 4. 거래량 점수 계산(가중치 10%)
        volume = self.data.Volume[-1]
        avg_volume = pd.Series(self.data.Volume).rolling(window=20).mean().iloc[-1]
        volume_score = calc_volume_score(volume, avg_volume)
        score += volume_score


        # 최종 스코어링 결과 출력
        # write_log(
        #     f"📅 [{self.data.index[-1].strftime('%Y.%m.%d')}] | "
        #     f"EMA: {ema_adx_score:>5.2f} | "
        #     f"MACD Historgram: {macd_score:>5.2f} | "
        #     f"RSI: {rsi_score:>5.2f} | "
        #     f"VOL: {volume_score:>5.2f} | "
        #     f"TOTAL: {score:>5.2f}"
        # , file_score_log)
        score_log_record.append({
            "date": self.data.index[-1].strftime('%Y.%m.%d'),
            "EMA": round(ema_adx_score, 2),
            "MACD": round(macd_score, 2),
            "RSI": round(rsi_score, 2),
            "VOL": round(volume_score, 2),
            "TOTAL": round(score, 2)
        })

        return score
    

    def next(self):
        score = self.calculate_score()
        current_price = self.data.Close[-1]

        # 현재 포지션 존재 여부 확인
        has_position = self.position.size > 0

        # ✅ 매수 조건: 스코어가 매수 임계값 이상이고 포지션 없음
        if score >= self.buy_threshold and not has_position:
            size = int(self._broker._cash / current_price * 0.5)  # 50% 자금 투입 예시
            if size >= 1:
                self.buy(size=size)
                trading_log_record.append({
                    "date": self.data.index[-1].strftime('%Y.%m.%d'),
                    "action": "buy",
                    "score": round(score, 2),
                    "price": round(current_price, 2),
                    "size": size
                })

        # ✅ 매도 조건: 스코어가 매도 임계값 이하이고 포지션 있음
        elif score <= self.sell_threshold and has_position:
            size = max(int(self.position.size * 0.5), 1)  # 보유 수량 50% 매도 예시
            self.sell(size=size)
            trading_log_record.append({
                "date": self.data.index[-1].strftime('%Y.%m.%d'),
                "action": "sell",
                "score": round(score, 2),
                "price": round(current_price, 2),
                "size": size
            })

        # ✅ 손절 (-7%) / 익절 (+15%)
        if has_position:
            avg_entry = (self.position.pl + self.position.size * current_price) / self.position.size
            pnl_ratio = current_price / avg_entry
            if pnl_ratio <= 0.93 or pnl_ratio >= 1.15:
                self.sell(size=self.position.size)
                tag = "Stop Loss" if pnl_ratio <= 0.93 else "Take Profit"
                trading_log_record.append({
                    "date": self.data.index[-1].strftime('%Y.%m.%d'),
                    "action": tag,
                    "score": round(score, 2),
                    "price": round(current_price, 2),
                    "size": self.position.size
                })
