from backtesting import Backtest
from utils.data_loader import get_stock_data
from strategies.smart_score import SmartScore, score_log_record, trading_log_record
from utils.logger import write_log, write_log_xlsx
from config.config import PathConfig, backtesting_config
import os
import pandas as pd
import pprint


def convert_stats_to_vertical_dict(stats_obj):
    """ stats 객체를 {항목명: 값} 형태의 딕셔너리로 변환 """
    series = pd.Series(stats_obj)
    return {k: str(v) if not isinstance(v, (str, int, float)) else v for k, v in series.items()}


def run_backtest():
    symbol = backtesting_config.SYMBOL
    start_date = backtesting_config.BACKTEST_START
    end_date = backtesting_config.BACKTEST_END

    fetch_start_date = backtesting_config.FETCH_START


    # 🔥 로그 초기화: 기존 로그 파일 삭제
    os.makedirs(PathConfig.RESULT_DIR, exist_ok=True)

    for log_file in [f"{symbol}_{PathConfig.TODAY}_{PathConfig.XLSX_SCORE_LOG}", f"{symbol}_{PathConfig.TODAY}_{PathConfig.XLSX_TRADING_LOG}", f"{symbol}_{PathConfig.TODAY}_{PathConfig.TXT_BACKTEST_LOG}"]:
        path = os.path.join(PathConfig.RESULT_DIR, log_file)
        if os.path.exists(path):
            os.remove(path)
            print(f"🧹 기존 로그 파일 삭제됨: {path}")


    # 데이터 로드
    data = get_stock_data(symbol=symbol, start=fetch_start_date, end=end_date)
    # SMA 등 프리롤이 계산된 이후부터 필터
    filter_data = data[data.index >= start_date]

    # 백테스트 실행
    bt = Backtest(filter_data, SmartScore, cash=10000, commission=.002)
    stats = bt.run()

    # 스코어 로그 기록
    score_df = pd.DataFrame(score_log_record, columns=["date", "EMA", "MACD", "RSI", "VOL", "TOTAL", "current price", "market_regime"])
    write_log_xlsx(score_df, f"{symbol}_{PathConfig.TODAY}_{PathConfig.XLSX_SCORE_LOG}", template="score")

    # 트레이딩 로그 기록
    trading_df = pd.DataFrame(trading_log_record, columns=["date", "action", "score", "price", "size", "avg_price", "roi", "market_value", "market_regime"])
    write_log_xlsx(trading_df, f"{symbol}_{PathConfig.TODAY}_{PathConfig.XLSX_TRADING_LOG}", template="trading")

    # 백테스트 결과 기록(text 파일)
    write_log(pprint.pformat(stats), f"{backtesting_config.SYMBOL}_{PathConfig.TODAY}_{PathConfig.TXT_BACKTEST_LOG}")

    
    os.makedirs(PathConfig.RESULT_DIR, exist_ok=True)
    html_path = os.path.join(PathConfig.RESULT_DIR, f"{symbol}_backtest_{PathConfig.TODAY}.html")

    bt.plot(filename=html_path)

# main 함수 실행행
if __name__ == "__main__":
    run_backtest()
