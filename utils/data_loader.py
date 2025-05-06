import pandas as pd
import yfinance as yf

def get_stock_data(symbol: str, start: str, end: str) -> pd.DataFrame:
    """
    yfinance 데이터를 다운로드하고 Backtesting.py에 맞게 변환합니다.
    """
    data = yf.download(symbol, start=start, end=end, interval="1d", threads=False, progress=False)

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data.rename(columns={
        "Open": "Open",
        "High": "High",
        "Low": "Low",
        "Close": "Close",
        "Volume": "Volume"
    }, inplace=True)

    required_columns = ["Open", "High", "Low", "Close", "Volume"]
    data = data[required_columns]

    data.index = pd.to_datetime(data.index)
    
    data.dropna(inplace=True)
    
    return data
