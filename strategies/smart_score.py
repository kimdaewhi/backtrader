import pandas as pd
import numpy as np
from backtesting import Strategy

from utils.logger_sqlite import sqlite_logger, LOG_TABLES
from indicators.base import EMA, SMA, ATR
from indicators.advanced import ADX, RSI, MACD_and_signal
from scoring.score_factors import (
    calc_ema_adx_score,
    calc_macd_hist_score,
    calc_rsi_score,
    calc_volume_score,
)
from regime import MarketRegime
from regime.market_regime_evaluator import MarketRegimeEvaluator


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


    def init(self):
        """ 초기화 """
        self.ema1 = self.I(EMA, self.data.Close, self.n1, overlay=True)                         # 단기 EMA(12일선)
        self.ema2 = self.I(EMA, self.data.Close, self.n2, overlay=True)                         # 중기 EMA(26일선)
        self.adx = self.I(ADX, self.data.High, self.data.Low, self.data.Close, period=14, overlay=False)   # ADX 계산
        self.rsi = self.I(RSI, self.data.Close, overlay=False)                                  # RSI 계산
        self.macd, self.signal = self.I(MACD_and_signal, self.data.Close, name='MACD', overlay=False)  # MACD 계산
        self.atr = self.I(ATR, self.data.High, self.data.Low, self.data.Close, window=14, overlay=False)  # ATR 계산
        self.atr_series = pd.Series(self.atr, index=self.data.index)
        # MarketRegimeEvaluator에서 사용할 인디케이터 설정
        self.regime_evaluator = MarketRegimeEvaluator(
            indicators={
                "atr": self.atr_series,
            }
        )

        self.score_logs = []  # 스코어 로그 초기화
        self.trading_logs = []  # 매매 로그 초기화
        self.regime_logs = []  # 매매 로그 초기화

        # ✅ 테이블 구조 정의용 예시 row
        example_score_log = {
            "date": "2025.01.01",               # TEXT
            "EMA": 0.0,                          # REAL
            "MACD": 0.0,
            "RSI": 0.0,
            "VOL": 0.0,
            "TOTAL": 0.0,
            "current price": 0.0,
            "market_regime": "none"             # TEXT
        }
        example_trading_log = {
            "date": "2025.01.01",               # TEXT
            "action": "Buy",                    # TEXT
            "score": 0.0,                       # REAL
            "price": 0.0,
            "size": 0,                          # INTEGER
            "avg_price": 0.0,
            "roi": 0.0,
            "market_value": 0.0,
            "market_regime": MarketRegime.NONE.value
        }
        example_regime_log = {
            "date": "2025.01.01",               # TEXT
            "market_regime": MarketRegime.NONE.value,  # TEXT
            "direction_score": 0.0,         # REAL(방향성 스코어)
            "trend_score": 0.0,            # REAL(추세 스코어)
            "noise_score": 0.0,              # REAL
            "atr": 0.0,                       # REAL
            "std": 0.0,                       # REAL
            "z-score": 0.0,                   # REA
        }
        # 테이블 생성
        sqlite_logger._ensure_table(LOG_TABLES["score"], example_score_log)  
        sqlite_logger._ensure_table(LOG_TABLES["trade"], example_trading_log)
        sqlite_logger._ensure_table(LOG_TABLES["regime"], example_regime_log)

        sqlite_logger.begin()  # SQLite 트랜잭션 시작
    

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

        score_log = {
            "date": self.data.index[-1].strftime('%Y.%m.%d'),
            "EMA": round(ema_adx_score, 2),
            "MACD": round(macd_score, 2),
            "RSI": round(rsi_score, 2),
            "VOL": round(volume_score, 2),
            "TOTAL": round(score, 2),
            "current price": round(current_price, 2),
            "market_regime": self.market_regime.value,
        }
        self.score_logs.append(score_log)  # 스코어 로그 추가

        return score

    
    def check_trailing_stop(self, current_price, score):
        """ 트레일링 스탑 손절 기준 체크 및 발동 시 매도 """
        """ current_price: 현재 가격 """
        """ score: 스코어 """
        stop_price = self.trailing_high * (1 - self.trailing_stop_drawdown)  # 손절 기준 가격

        if(current_price <= stop_price):
            self.sell(size=self.position.size)  # 포지션 청산(비율 : 100%)
            roi = (current_price - self.avg_entry_price) / self.avg_entry_price * 100  # 수익률 계산
            
            # 트레일링 스탑 손절 기록
            trading_log = {
                "date": self.data.index[-1].strftime('%Y.%m.%d'),
                "action": "Trailing Stop",
                "score": round(score, 2),
                "price": round(current_price, 2),
                "size": self.position.size,
                "avg_price": round(self.avg_entry_price, 2),
                "roi": round(roi, 2),
                "market_value": 0.0,
                "market_regime": self.market_regime.value
            }
            self.trading_logs.append(trading_log)  # 매매 로그 추가

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

            trading_log = {
                "date": date_str,
                "action": tag,
                "score": round(score, 2),
                "price": round(current_price, 2),
                "size": self.position.size,
                "avg_price": round(avg_entry, 2),
                "roi": round(roi, 2),
                "market_value": 0.0,
                "market_regime": self.market_regime.value
            }
            self.trading_logs.append(trading_log)  # 매매 로그 추가

            self.avg_entry_price = 0
            self.last_size = 0


    def next(self):
        """ 일별 매매 로직
        - 매수/매도 조건을 만족할 경우 매매 실행.
        - 매수 : 스코어가 score 임계값 이상이고 포지션이 없는 경우
        - 매도 : 스코어가 score 임계값 이하이고 포지션이 있는 경우
        - 손절/익절 : 스코어가 손절/익절 기준을 만족할 경우 매도(익절 : 15% / 손절 : 7%)
        - 매도 후 매수 평균가 계산
        - 매매 기록은 trading_log 테이블에 저장.
        """
        # ✅ 1단계: 시장 판단
        date = self.data.index[-1]
        directon_score = 0.0
        trend_score = 0.0
        noise_score, latest_atr, std, z_score = self.regime_evaluator.score_noise(date, window=14)
        if noise_score == 1:
            self.market_regime = MarketRegime.VOLATILE
        else:
            self.market_regime = MarketRegime.NONE
        
        regime_log = {
            "date": self.data.index[-1].strftime('%Y.%m.%d'),
            "market_regime": self.market_regime.value,
            "direction_score": round(directon_score, 2),
            "trend_score": round(trend_score, 2),
            "noise_score": noise_score,
            "atr": round(latest_atr, 2),
            "std": round(std, 2),
            "z-score": round(z_score, 2)
        }
        self.regime_logs.append(regime_log)  # 레짐 로그 추가


        # 1. 스코어 계산
        score = self.calculate_score()   # 스코어 계산

        current_price = self.data.Close[-1] # 현재가
        has_position = self.position.size > 0   # 포지션 보유 여부
        date_str = self.data.index[-1].strftime('%Y.%m.%d') # 날짜 포맷 변환

        # ✅ 손절 / 익절 조건
        if has_position:
            self.check_exit_conditions(score, current_price, date_str)


    def __del__(self):
        """ 종료 시 SQLite 트랜잭션 종료 """
        if self.score_logs:
            sqlite_logger.insert_many(LOG_TABLES["score"], self.score_logs)
        
        if self.trading_logs:
            sqlite_logger.insert_many(LOG_TABLES["trade"], self.trading_logs)

        if self.regime_logs:
            sqlite_logger.insert_many(LOG_TABLES["regime"], self.regime_logs)

        if sqlite_logger._in_transaction:
            sqlite_logger.commit()




