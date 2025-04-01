import os
from datetime import datetime
from pydantic_settings import BaseSettings

class PathConfig:
    # ---------------------------
    # 📅 날짜 및 결과 디렉토리 설정
    # ---------------------------
    TODAY = datetime.now().strftime("%Y%m%d")
    RESULT_DIR = os.path.join("results", f"result_{TODAY}")

    # ---------------------------
    # 📄 로그 파일명 정의
    # ---------------------------
    FILE_SCORE_LOG = "score_log.txt"
    FILE_TRADING_LOG = "trading_log.txt"
    FILE_BACKTEST_LOG = "backtest_results.txt"

    # ---------------------------
    # 📁 전체 경로 (선택)
    # ---------------------------
    PATH_SCORE_LOG = os.path.join(RESULT_DIR, FILE_SCORE_LOG)
    PATH_TRADING_LOG = os.path.join(RESULT_DIR, FILE_TRADING_LOG)
    PATH_BACKTEST_LOG = os.path.join(RESULT_DIR, FILE_BACKTEST_LOG)



class BacktestConfig(BaseSettings):
    # ---------------------------
    # ⚙️ 백테스트 설정
    # ---------------------------
    # (모듈 전역에서 import 해서 사용 가능)
    SYMBOL: str = "ORCL"  # 종목 코드
    CASH: int = 10000    # 초기 자본금
    COMMISSION: float = 0.002  # 거래 수수료

    # 기간
    BACKTEST_START: str = "2022-01-01"
    BACKTEST_END: str = "2024-12-31"

    # yfinance 데이터 fetch용 (이건 SMA 등 계산 고려한 기간 포함)
    FETCH_START: str = "2019-06-01"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


backtesting_config = BacktestConfig()