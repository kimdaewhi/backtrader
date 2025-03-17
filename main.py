import backtrader as bt
import yfinance as yf
import pandas as pd
import datetime
import matplotlib
import matplotlib.pyplot as plt
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
    # fig = cerebro.plot(figsize=(16, 8), grid=False)[0][0]   # 차트 크기 조정 & 그리드 제거
    matplotlib.rcParams["figure.figsize"] = (16, 8)  # 기본 차트 크기 설정
    matplotlib.rcParams["figure.dpi"] = 100  # DPI 설정 (화질 개선)

    # ✅ Cerebro 플로팅 후 윈도우 크기 조정
    # ✅ 차트 스타일 수정
    figs = cerebro.plot(style="candlestick", 
                        barup="#33A474", bardown="#E57373",  # 부드러운 초록/빨강
                        grid=False, gridcolor="#DDDDDD",  # 연한 회색 그리드
                        volume=True)  # 거래량 표시

    fig = figs[0][0]  # 첫 번째 Figure 가져오기
    fig.patch.set_facecolor("#F5F5F5")  # 배경을 밝은 회색으로 변경

    # 9. 윈도우 크기 조정 (Windows 전용)
    fig_manager = plt.get_current_fig_manager()
    fig_manager.window.geometry("1200x800")  # 윈도우 크기 조정





if __name__ == "__main__":
    run_backtest()
