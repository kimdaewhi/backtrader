import backtrader as bt

class SmaCrossover(bt.Strategy):
    # 단순 이동평균선 (SMA) 전략
    params = (
        ("short_period", 10), 
        ("long_period", 50)
    )

    def __init__(self):
        self.sma_short = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_period)
        self.sma_long = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_period)

        # plotinfo 설정
        self.sma_short.plotinfo.plotname = "단순 SMA(10일)"
        self.sma_long.plotinfo.plotname = "단순 SMA(50일)"

        # Trades 관련 설정
        self.plotinfo.trades = True         # 매매 시점 표시
        self.plotinfo.legend = True         # 범례 표시
        self.plotinfo.plot_text = True      # 매매 시 수익/손실 표시
        self.plotinfo.plot_profit = True    # 순손익 표시

        self.plotinfo.tradewins = "수익"    # 수익 거래
        self.plotinfo.tradelosses = "손실"  # 손실 거래

    
    def next(self):
        if self.sma_short[0] > self.sma_long[0] and self.sma_short[-1] <= self.sma_long[-1]:
            self.buy()
        elif self.sma_short[0] < self.sma_long[0] and self.sma_short[-1] >= self.sma_long[-1]:
            self.sell()
