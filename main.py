import backtrader as bt
import yfinance as yf
import pandas as pd
import datetime
from strategies.sma_crossover import SmaCrossover

# ✅ 데이터 다운로드 함수
def get_stock_data(symbol="AAPL", start="2023-01-01", end="2024-01-01"):
    data = yf.download(symbol, start=start, end=end)

    # 🔥 컬럼명을 Backtrader에 맞게 변환 (튜플 → 문자열)
    data.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in data.columns]

    # 🔥 날짜 인덱스 변환 (Backtrader는 datetime 인덱스 필요)
    data.index = pd.to_datetime(data.index)
    
    return data



# ✅ Backtrader 데이터 피드 클래스를 커스텀하여 `adj_close` 포함
class CustomPandasData(bt.feeds.PandasData):
    # Backtrader 기본 제공 필드에 `adj_close` 추가
    lines = ("adj_close",)
    params = (("adj_close", -1),)  # -1이면 데이터 사용 안 함
    

# ✅ 백테스트 실행 함수
def run_backtest():
    # 1. Backtrader Cerebro 엔진 생성
    cerebro = bt.Cerebro()

    # 2. 데이터 가져오기
    df = get_stock_data()
    data = CustomPandasData(dataname=df)

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
    cerebro.plot()

if __name__ == "__main__":
    run_backtest()
