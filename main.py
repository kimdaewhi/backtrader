from backtesting import Backtest
from utils.data_loader import get_stock_data
from strategies.sma_crossover import SmaBollingerStrategy
from utils.logger import write_log_csv
from config.config import PathConfig, backtesting_config
import os
import pandas as pd


def convert_stats_to_row_list(stats_obj):
    """ stats 객체를 [{항목: ..., 값: ...}, ...] 형식으로 변환 """
    series = pd.Series(stats_obj)
    row_list = [{"항목": k, "값": str(v) if not isinstance(v, (str, int, float)) else v} for k, v in series.items()]
    return row_list


def run_backtest():
    symbol = backtesting_config.SYMBOL
    start_date = backtesting_config.BACKTEST_START
    end_date = backtesting_config.BACKTEST_END

    fetch_start_date = backtesting_config.FETCH_START


    # 🔥 로그 초기화: 기존 로그 파일 삭제
    os.makedirs(PathConfig.RESULT_DIR, exist_ok=True)

    for log_file in [f"{symbol}_{PathConfig.CSV_SCORE_LOG}", f"{symbol}_{PathConfig.CSV_TRADING_LOG}", f"{symbol}_{PathConfig.CSV_BACKTEST_LOG}"]:
        path = os.path.join(PathConfig.RESULT_DIR, log_file)
        if os.path.exists(path):
            os.remove(path)
            print(f"🧹 기존 로그 파일 삭제됨: {path}")


    # 데이터 로드
    data = get_stock_data(symbol=symbol, start=fetch_start_date, end=end_date)
    # SMA 등 프리롤이 계산된 이후부터 필터
    filter_data = data[data.index >= start_date]

    # 백테스트 실행
    bt = Backtest(filter_data, SmaBollingerStrategy, cash=10000, commission=.002)
    stats = bt.run()

    # ✅ stats만 dict로 정제해서 csv로 기록
    stats_dict = convert_stats_to_row_list(stats)
    # ✅ 한 줄씩 기록 (공통 csv 함수 사용)
    for row in stats_dict:
        write_log_csv(row, f"{symbol}_{PathConfig.CSV_BACKTEST_LOG}")
    # write_log(pprint.pformat(stats), f"{symbol}_{PathConfig.FILE_BACKTEST_LOG}")
    
    os.makedirs(PathConfig.RESULT_DIR, exist_ok=True)
    html_path = os.path.join(PathConfig.RESULT_DIR, f"{symbol}_backtest_{PathConfig.TODAY}.html")

    bt.plot(filename=html_path)

# main 함수 실행행
if __name__ == "__main__":
    run_backtest()
