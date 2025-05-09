# indicators/__init__.py

# Base indicators
from .base.ema import EMA
from .base.sma import SMA
from .base.atr import ATR

# Advanced indicators
from .advanced.macd import MACD_and_signal
from .advanced.bollinger import BollingerBands
from .advanced.adx import ADX
from .advanced.rsi import RSI


"""
📦 indicators

이 패키지는 백테스트 및 자동매매 전략에서 사용하는 모든 기술적 지표를 관리합니다.

디렉토리 구조:
- base/      → 단순 지표 (SMA, EMA 등)
- advanced/  → 고급 지표 (MACD, RSI, ADX, BollingerBands 등)

각 지표는 전략에서 독립적으로 호출 가능하며,
보조 해석/판단 로직은 별도의 signals/ 모듈에서 관리됩니다.
"""


__all__ = [
    "EMA", "SMA", "ATR",
    "MACD_and_signal", "BollingerBands", "ADX", "RSI"
]
