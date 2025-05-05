import pandas as pd

def ADX(high, low, close, period=14):
    """
    ADX (Average Directional Index) 계산 함수
    - 시장의 추세 강도를 측정하는 데 사용
    - DI+: 양의 방향성 지표
    - DI-: 음의 방향성 지표
    - DX : DI+와 DI-의 차이를 통해 추세 강도를 수치화
    - ADX: DX의 평균으로, 추세 강도만 남긴 지표 (방향성은 제거됨)
    
    - 0 ~ 15 : 추세 없음(No Trend) > 횡보 구간. 방향성 없음
    - 15 ~ 20 : 약한 추세(Weak Trend) > 애매한 구간. 추세 전환 여부 확인 필요
    - 20 ~ 25 : 시작 추세(Emerging Trend) > 추세 형성 가능성. 보조 지표와 함께 사용
    - 25 ~ 30 : 강한 추세(Strong Trend) > 추세 추종 전략 유효. 매매 신호로 활용 가능
    - 30 ~ 50 : 매우 강한 추세(Very Strong) > 모멘텀 강함. 지속 기대 가능
    - 50 ~ 100 : 극단적 추세(Extreme Trend) > 과매수/과매도 구간

    Parameters:
        high (list or Series): 고가 시계열
        low (list or Series): 저가 시계열
        close (list or Series): 종가 시계열
        period (int): 계산에 사용할 기간 (보통 14일)

    Returns:
        Series: ADX 값 (pandas.Series)
    """

    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)

    # 1. DM+ / DM- 계산 (Directional Movement)
    up_move = high.diff()
    down_move = low.diff()

    plus_dm = ((up_move > down_move) & (up_move > 0)) * up_move
    minus_dm = ((down_move > up_move) & (down_move > 0)) * down_move

    # 2. TR (True Range) 계산
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # 3. ATR (Average True Range): 변동성 추정 (EMA로 개선)
    atr = tr.ewm(span=period, adjust=False).mean()

    # 4. DI+ / DI- 계산
    plus_di = 100 * plus_dm.ewm(span=period, adjust=False).mean() / atr
    minus_di = 100 * minus_dm.ewm(span=period, adjust=False).mean() / atr

    # 5. DX 계산: DI+ 와 DI- 간의 차이를 백분율로 수치화
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100

    # 6. ADX 계산: DX의 EMA (방향성 제거한 순수 추세 강도)
    adx = dx.ewm(span=period, adjust=False).mean()

    return adx
