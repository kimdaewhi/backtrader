import pandas as pd
import numpy as np
from backtesting import Strategy

from indicators.base import EMA, SMA
from indicators.advanced import ADX, RSI, MACD_and_signal
from scoring.score_factors import (
    calc_ema_adx_score,
    calc_macd_hist_score,
    calc_rsi_score,
    calc_volume_score,
)
from regime import MarketRegime



score_log_record = []   # 스코어 로그 기록용 DataFrame
trading_log_record = [] # 거래 로그 기록용 DataFrame


class SmartScore(Strategy):
    n1 = 12                             # EMA 단기 이동평균 기간
    n2 = 26                             # EMA 중기 이동평균 기간

    # buy, sell 비율
    buy_ratio = 0.5                     # 매수 비율 (50% 자금 투입)
    sell_ratio = 0.5                    # 매도 비율 (50% 자금 회수)

    # 종합 Score 임계값 설정
    buy_threshold = 1.5
    sell_threshold = -1.5

    # 매수 평균가
    avg_entry_price = 0.0               # 직전 매수 평균가
    last_size = 0                       # 직전 매수 수량

    # 트레일링 스탑
    trailing_stop_drawdown = 0.1        # 트레일링 스탑 손절 기준 (10% 손실)
    trailing_high = 0                   # 트레일링 스탑 최고가 기록용

    # 마켓 레짐 판단 지표
    market_regime = MarketRegime.NONE   # 시장 레짐 초기화
    regime_window = 20                  # 시장 regime 판단을 위한 스코어 히스토리 기간
    std = 0                             # 표준편차 초기화
    z_score = 0                         # z-score 초기화


    def init(self):
        """ 초기화 """
        self.ema1 = self.I(EMA, self.data.Close, self.n1, overlay=True)                         # 단기 EMA(12일선)
        self.ema2 = self.I(EMA, self.data.Close, self.n2, overlay=True)                         # 중기 EMA(26일선)
        self.adx = self.I(ADX, self.data.High, self.data.Low, self.data.Close, period=14, overlay=False)   # ADX 계산
        self.rsi = self.I(RSI, self.data.Close, overlay=False)                                  # RSI 계산
        self.macd, self.signal = self.I(MACD_and_signal, self.data.Close, name='MACD', overlay=False)  # MACD 계산
    

    def calculate_score(self):
        """ 매수/매도 판단을 위한 스코어링 엔진 - 각 지표의 Signal을 Score로 계산 """
        """ SMA Crossover, 볼린저 밴드, RSI, Volume을 종합하여 종목별 점수 산출 """
        """ Score Scale 기준 : -10 ~ 10점 """
        """ 가중치 : EMA & ADX(40%) + MACD(20%) + RSI(20%) + Volume(10%) """

        score = 0           # 총합 Score(+-10 ~ -10)
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
        current_price = self.data.Close[-1]

        score_log_record.append({
            "date": self.data.index[-1].strftime('%Y.%m.%d'),
            "EMA": round(ema_adx_score, 2),
            "MACD": round(macd_score, 2),
            "RSI": round(rsi_score, 2),
            "VOL": round(volume_score, 2),
            "TOTAL": round(score, 2),
            "current price": round(current_price, 2),
            "σ (std)": round(self.std, 2) if self.std is not None else "-",
            "z-score": round(self.z_score, 2) if self.z_score is not None else "-",
            "market_regime": self.market_regime.value,
        })

        return score
    

    def get_market_regime(self):
        """ SMA 기반의 z-score로 시장 레짐 판단 """
        self.std = 0        # 표준편차 초기화
        self.z_score = 0    # z-score 초기화
        
        close = self.data.Close
        if len(close) < self.regime_window:
            self.market_regime = MarketRegime.NONE
            return self.market_regime

        sma_series = SMA(close, self.regime_window)
        latest_price = close[-1]
        sma = sma_series.iloc[-1]

        # σ(표준편차) 계산
        # σ는 시장의 예측 가능성만을 나타내는 지표로, 가격의 변동성을 추정하기에는 부족함
        # 따라서, 가격의 변동성을 추정하기 위해서는 '방향성'을 고려해야 하는데, 이를 위해서는 다른 지표를 활용해야 함.(ex: ADX, ATR, CCI 등)
        # 기울기 / low pass filter
        self.std = float(np.std(close[-self.regime_window:]))
        self.z_score = float((latest_price - sma) / self.std) if self.std != 0 else 0

        std_threshold = 1.8  # 변동성 기준
        z_score_threshold = 0.9  # z-score 기준


        # 🔽 z-score를 이용한 시장 레짐 분류
        if self.std >= std_threshold:
            self.market_regime = MarketRegime.VOLATILE
        elif self.z_score >= z_score_threshold:
            self.market_regime = MarketRegime.BULL
        elif self.z_score <= -z_score_threshold:
            self.market_regime = MarketRegime.BEAR
        elif abs(self.z_score) < z_score_threshold:
            self.market_regime = MarketRegime.SIDEWAYS
        else:
            self.market_regime = MarketRegime.NONE

        return self.market_regime


    
    def check_trailing_stop(self, current_price, score):
        """ 트레일링 스탑 손절 기준 체크 및 발동 시 매도 """
        """ current_price: 현재 가격 """
        """ score: 스코어 """
        stop_price = self.trailing_high * (1 - self.trailing_stop_drawdown)  # 손절 기준 가격

        if(current_price <= stop_price):
            self.sell(size=self.position.size)  # 포지션 청산(비율 : 100%)
            roi = (current_price - self.avg_entry_price) / self.avg_entry_price * 100  # 수익률 계산
            
            # 트레일링 스탑 손절 기록
            trading_log_record.append({
                "date": self.data.index[-1].strftime('%Y.%m.%d'),
                "action": "Trailing Stop",
                "score": round(score, 2),
                "price": round(current_price, 2),
                "size": self.position.size,
                "avg_price": round(self.avg_entry_price, 2),
                "roi": round(roi, 2),
                "market_value": 0.0
            })

            self.avg_entry_price = 0  # 포지션 초기화
            self.last_size = 0
            self.trailing_high = 0  # 최고가 초기화

            return True  # 손절 발생
        return False  # 손절 미발동


    def check_exit_conditions(self, score, current_price, date_str):
        """ 손절/익절 조건 체크 및 매도 """
        """ score: 스코어 """
        """ current_price: 현재 가격 """
        """ date_str: 날짜 문자열 """
        # 1. 트레일링 스탑 갱신
        if current_price > self.trailing_high:
            self.trailing_high = current_price

        # 2. 트레일링 스탑 체크
        if self.check_trailing_stop(current_price, score):
            return

        # 3. 손절/익절 체크
        avg_entry = self.avg_entry_price
        pnl_ratio = current_price / avg_entry
        stop_loss_threshold = 0.93
        take_profit_threshold = 1.15

        if pnl_ratio <= stop_loss_threshold or pnl_ratio >= take_profit_threshold:
            tag = "Stop Loss" if pnl_ratio <= stop_loss_threshold else "Take Profit"
            self.sell(size=self.position.size)
            roi = (current_price - avg_entry) / avg_entry * 100

            trading_log_record.append({
                "date": date_str,
                "action": tag,
                "score": round(score, 2),
                "price": round(current_price, 2),
                "size": self.position.size,
                "avg_price": round(avg_entry, 2),
                "roi": round(roi, 2),
                "market_value": 0.0,
                "market_regime": self.market_regime.value
            })

            self.avg_entry_price = 0
            self.last_size = 0


    def handle_bull_market_logic(self, score: float, current_price: float):
        """상승장에서의 매매 전략
        - 스코어가 buy_threshold 이상이면 매수
        - 포지션 없어야만 매수 진행
        """
        has_position = self.position.size > 0
        date_str = self.data.index[-1].strftime('%Y.%m.%d')

        if score >= self.buy_threshold and not has_position:
            available_cash = self._broker if hasattr(self._broker, "get_cash") else self._broker._cash
            size = int(available_cash / current_price * self.buy_ratio)

            if size >= 1 and (current_price * size <= available_cash):
                self.buy(size=size)

                # 🔧 평균 매수가 계산
                if self.last_size == 0:
                    self.avg_entry_price = current_price
                else:
                    self.avg_entry_price = (
                        (self.avg_entry_price * self.last_size) + (current_price * size)
                    ) / (self.last_size + size)

                self.last_size += size
                market_value = self.last_size * current_price

                trading_log_record.append({
                    "date": date_str,
                    "action": "buy",
                    "score": round(score, 2),
                    "price": round(current_price, 2),
                    "size": size,
                    "avg_price": round(self.avg_entry_price, 2),
                    "roi": "-",
                    "market_value": round(market_value, 2),
                    "market_regime": self.market_regime.value
                })


    def next(self):
        """ 일별 매매 로직
        - 매수/매도 조건을 만족할 경우 매매 실행.
        - 매수 : 스코어가 score 임계값 이상이고 포지션이 없는 경우
        - 매도 : 스코어가 score 임계값 이하이고 포지션이 있는 경우
        - 손절/익절 : 스코어가 손절/익절 기준을 만족할 경우 매도(익절 : 15% / 손절 : 7%)
        - 매도 후 매수 평균가 계산
        - 매매 기록은 trading_log_record에 저장.
        """

        # 1. 스코어 계산
        score = self.calculate_score()   # 스코어 계산

        # 2. 시장 레짐 판단
        self.get_market_regime()

        current_price = self.data.Close[-1] # 현재가
        has_position = self.position.size > 0   # 포지션 보유 여부
        date_str = self.data.index[-1].strftime('%Y.%m.%d') # 날짜 포맷 변환

        # ✅ 1단계: 시장 판단 기반 매매 시도
        if self.market_regime == MarketRegime.BULL:
            self.handle_bull_market_logic(score, current_price)
        # elif self.market_regime == MarketRegime.SIDEWAYS:
        #     self.handle_sideways_market_logic(score, current_price)
        # elif self.market_regime == MarketRegime.BEAR:
        #     self.handle_bear_market_logic(score, current_price)
        # elif self.market_regime == MarketRegime.VOLATILE:
        #     self.handle_volatile_market_logic(score, current_price)
        else:
            pass  # 혹시 모를 init/none 등 기본 처리

        # ✅ 손절 / 익절 조건
        if has_position:
            self.check_exit_conditions(score, current_price, date_str)





