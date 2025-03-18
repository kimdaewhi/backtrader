import backtrader as bt
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from utils.data_loader import get_stock_data
from strategies.sma_crossover import SmaCrossover



# ✅ 백테스트 실행 함수
def run_backtest():
    # 1. Backtrader Cerebro 엔진 생성
    cerebro = bt.Cerebro()

    ticker = 'ORCL'
    start_date = '2018-01-01'
    end_date = '2019-01-01'

    # 2. 데이터 가져오기
    data = get_stock_data(symbol=ticker, start=start_date, end=end_date)

    # 3. Cerebro에 데이터 추가
    cerebro.adddata(data)

    # 4. 전략 추가
    cerebro.addstrategy(SmaCrossover)

    # 5. 초기 자본 및 수수료 설정
    cerebro.broker.set_cash(10000)
    cerebro.broker.setcommission(commission=0.001)

    # 6. 매매 단위 설정
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # 7. 백테스트 실행
    print(f"초기 자본: {cerebro.broker.getvalue():,.2f} USD")
    cerebro.run()
    print(f"최종 자본: {cerebro.broker.getvalue():,.2f} USD")


    # 8. 결과 차트 출력
    plt.rcParams["figure.figsize"] = (16, 7)  # 차트 크기 조정

    cerebro.plot(style="candlestick", 
        barup="#d32f2f", bardown="#1976d2",
        grid=False,
        volume=True,
        dpi=100
    )


if __name__ == "__main__":
    run_backtest()
