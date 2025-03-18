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
    plt.style.use("seaborn-v0_8-bright")
    plt.rcParams["font.family"] = "NanumGothic"
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.figsize"] = (16, 7)  # 차트 크기 조정
    plt.rcParams["legend.fontsize"] = 12  # 범례 글씨 크기 조정
    plt.rcParams["axes.labelsize"] = 12  # 축 레이블 크기 조정
    plt.rcParams["xtick.labelsize"] = 10  # X축 눈금 크기
    plt.rcParams["ytick.labelsize"] = 10  # Y축 눈금 크기

    figs = cerebro.plot(style="candlestick", 
        barup="#d32f2f", bardown="#1976d2",
        grid=False,
        volume=True,
        dpi=100
    )

    fig = figs[0][0]  # 첫 번째 Figure 가져오기

    # ✅ 각 서브플롯(Axes) 개별 속성 변경
    for ax in fig.axes:
        ax.set_facecolor("#FFFFFF")  # 서브플롯 배경 흰색
        ax.spines["top"].set_visible(False)  # 상단 테두리 제거
        ax.spines["right"].set_visible(False)  # 우측 테두리 제거
        ax.spines["left"].set_linewidth(1.2)  # 좌측 테두리 굵기 증가
        ax.spines["bottom"].set_linewidth(1.2)  # 하단 테두리 굵기 증가

        # ✅ X축, Y축 라벨 한글화
        xlabel = ax.get_xlabel()
        ylabel = ax.get_ylabel()
        
        label_map = {
            "Open": "개장가",
            "High": "최고가",
            "Low": "최저가",
            "Close": "종가",
            "Volume": "거래량"
        }

        if xlabel in label_map:
            ax.set_xlabel(label_map[xlabel])
        if ylabel in label_map:
            ax.set_ylabel(label_map[ylabel])

        # ✅ 범례(레전드) 한글화
        legend = ax.get_legend()
        if legend:
            for text in legend.get_texts():
                legend_text = text.get_text()
                if legend_text == "BuySell":
                    text.set_text("매매")
                elif legend_text == "Volume":
                    text.set_text("거래량")
                elif legend_text.startswith("SimpleMovingAverage"):
                    text.set_text(legend_text.replace("SimpleMovingAverage", "단순 SMA"))

    # ✅ 차트 업데이트
    plt.draw()


if __name__ == "__main__":
    run_backtest()
