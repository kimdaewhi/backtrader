"""
📦 signals

이 디렉토리는 기술적 지표 간의 **명확한 이벤트 기반 트리거**만을 정의합니다.

📌 특징:
- SMA / EMA 크로스오버 (ex: 골든크로스, 데드크로스)
- MACD vs Signal 교차
- 특정 방향성 전환 등 **지표 간 상호 비교로 정의 가능한 신호만 포함**

⚠️ 단순 임계값 조건(예: ADX > 25)은 전략마다 해석이 달라지므로 여기에 포함하지 않습니다.
이런 해석은 전략 로직에서 직접 수행하세요.
"""