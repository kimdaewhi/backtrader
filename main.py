from backtesting import Backtest
from utils.data_loader import get_stock_data
from strategies.sma_crossover import SmaBollingerStrategy

def run_backtest():
    symbol = 'ORCL'
    start_date = '2020-01-01'
    end_date = '2020-06-30'

    fetch_start_date = '2019-10-01' # SMA60 계산산을 위한 프리롤 데이터 수집 시작일

    # 데이터 로드
    data = get_stock_data(symbol=symbol, start=fetch_start_date, end=end_date)
    # SMA 등 프리롤이 계산된 이후부터 필터
    filter_data = data[data.index >= start_date]

    # 백테스트 실행
    bt = Backtest(filter_data, SmaBollingerStrategy, cash=10000, commission=.002)
    stats = bt.run()
    
    print(stats)
    
    bt.plot()

# main 함수 실행행
if __name__ == "__main__":
    run_backtest()
