import yfinance as yf
import pandas as pd
import backtrader as bt


# ✅ Backtrader 데이터 피드 클래스를 커스텀하여 `adj_close` 포함
class CustomPandasData(bt.feeds.PandasData):
    # Backtrader 기본 제공 필드에 `adj_close` 추가
    lines = ("adj_close",)
    params = (("adj_close", -1),)  # -1이면 데이터 사용 안 함



# ✅ 데이터 다운로드 함수
def get_stock_data(symbol="AAPL", start="2023-01-01", end="2024-01-01"):
    data = yf.download(symbol, start=start, end=end)

    # 🔥 컬럼명을 Backtrader에 맞게 변환 (튜플 → 문자열)
    data.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in data.columns]

    # 🔥 날짜 인덱스 변환 (Backtrader는 datetime 인덱스 필요)
    data.index = pd.to_datetime(data.index)
    
    return CustomPandasData(dataname=data)