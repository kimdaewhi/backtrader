from enum import Enum

class MarketRegime(Enum):
    """ 시장 레짐 판단을 위한 클래스 """
    """ 레짐 종류 : Bull(강세장), Bear(약세장), Sideways(횡보장), Volatile(변동성장), None(없음) """
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    NONE = "none"