from enum import Enum


"""
    📊 시장 레짐 판단에 사용되는 지표 분류

    [📈 방향성 지표]
    - EMA Crossover         : 방향성 핵심 지표
    - MACD Value            : MACD 값 양/음으로 장기 방향 판단
    - CCI                   : ±100 기준, 평균 이탈 기반 방향성 감지
    - ROC                   : 가격 변화율(속도) 기반 선행 방향성 감지

    [📉 추세 강도 지표]
    - ADX                   : 추세 존재 여부 및 강도 판단
    - MACD Histogram        : 모멘텀(추세의 힘) 시각화
    - MACD Signal Crossover : 추세 전환 타이밍 감지
    - CCI                   : ±100 기준, 평균 이탈 수준에 따라 추세 강도 보조 판단

    [⚠️ 노이즈 필터링 지표]
    - 시그마(표준편차)        : 절대적 변동성 수준 측정
    - z-score               : 평균 대비 상대적 이탈 탐지 (정규화 기반)
"""


class MarketRegime(Enum):
    """
        시장 레짐 상태 분류를 위한 열거형 클래스

        레짐 종류:
        - BULL      : 강세장
        - BEAR      : 약세장
        - SIDEWAYS  : 횡보장
        - VOLATILE  : 변동성 장세
        - NONE      : 명확한 레짐 없음
    """
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    NONE = "none"