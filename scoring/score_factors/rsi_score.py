def calc_rsi_score(rsi_value):
    """ RSI 점수 계산 """
    """ rsi_value: RSI 값 """
    """ RSI 20 이하 -> -2점, RSI 80 이상 -> -2점 """
    if rsi_value < 20:
        rsi_score = 2.0
    elif rsi_value < 30:
        rsi_score = 1.0
    elif rsi_value > 80:
        rsi_score = -2.0
    elif rsi_value > 70:
        rsi_score = -1.0
    else:
        rsi_score = 0.0

    return rsi_score