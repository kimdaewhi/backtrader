from backtesting import Backtest
from utils.data_loader import get_stock_data
from strategies.sma_crossover import SmaCross

def run_backtest():
    symbol = 'ORCL'
    start_date = '2018-01-01'
    end_date = '2019-01-01'

    # 데이터 로드
    data = get_stock_data(symbol=symbol, start=start_date, end=end_date)

    # 백테스트 실행
    bt = Backtest(data, SmaCross, cash=10000, commission=.002)
    
    stats = bt.run()
    
    print(stats)
    
    bt.plot()

if __name__ == "__main__":
    run_backtest()
