### backtesting.py & Yahoo Finance 이용한 백테스트 시뮬레이션

1. yfinance를 이용한 데이터 수집 이후 데이터 컨버팅은 어떻게 모듈화할지?
<br><br><br>

# 공식문서<br>
https://kernc.github.io/backtesting.py/doc/backtesting/#gsc.tab=0<br>


# backtesting.py 수익률지표 설명
https://backtesting.tistory.com/entry/Backtesting-Trading-Strategies-with-the-Python-Backtestingpy-Library



>### 🟨 기간 및 노출
>🔸**Start**:<br>
>시작 날짜 (2020-01-02 00:00:00)<br>
>→ 전략이 시작된 시점을 나타냅니다.<br>
>
>🔸**End**:<br>
>종료 날짜 (2021-12-31 00:00:00)<br>
>→ 전략이 종료된 시점을 나타냅니다.
>
>🔸**Duration**:<br>
>기간 (729 days)<br>
>→ 전략이 실행된 총 기간입니다.
>
>🔸**Exposure Time [%]**:<br>
>노출 시간 비율 (76.0396%)<br>
>→ 자산이 시장에 투자된 총 시간의 비율입니다.
>
>### 🟨 수익 및 비용
>🔸**Equity Final [$]**:<br>
>최종 자산 가치 ($12,684.01)<br>
>→ 전략 종료 시점의 계좌 잔고입니다.
>
>🔸**Equity Peak [$]**:<br>
>최고 자산 가치 ($12,684.01)<br>
>→ 전략 기간 중 가장 높은 계좌 잔고입니다.
>
>🔸**Commissions [$]**:<br>
>수수료 ($281.36)<br>
>→ 거래를 수행하면서 발생한 총 수수료 비용입니다.
>
>🔸**Return [%]**:<br>
>총 수익률 (26.84%)<br>
>→ 전략 기간 동안의 총 수익률입니다.
>
>🔸**Buy & Hold Return [%]**:<br>
>매수 후 보유 전략 수익률 (87.17%)<br>
>→ 동일 기간 동안 단순히 자산을 매수하여 보유했을 경우의 수익률입니다.
><br>
><br>
>
>### 🟨 연간 성과 및 위험
>🔸**Return (Ann.) [%]**:<br>
>연간화 수익률 (12.60%)<br>
>→ 연간 기준으로 환산한 수익률입니다.
>
>🔸**Volatility (Ann.) [%]**:<br>
>연간화 변동성 (10.35%)<br>
>→ 연간 기준으로 환산한 자산 가격 변동성입니다.
>
>🔸**CAGR [%]**:<br>
>연평균 복리 성장률 (8.57%)<br>
>→ 투자 기간 동안 자산이 매년 평균적으로 증가한 비율입니다.
><br>
><br>
>
>### 🟨 위험 조정 성과 지표
>🔸**Sharpe Ratio**:<br>
>샤프 비율 (1.21714)<br>
>→ 위험 대비 초과 수익을 측정하는 지표로, 값이 높을수록 위험 대비 성과가 
> 좋습니다.
>
>🔸**Sortino Ratio**:<br>
>소르티노 비율 (3.45952)<br>
>→ 샤프 비율과 유사하지만, 변동성 대신 하락 위험만 고려하여 초과 수익을 
>측정합니다.
>
>🔸**Calmar Ratio**:<br>
>칼마 비율 (3.48959)<br>
>→ 최대 손실(MDD)에 대한 연평균 복리 성장률을 나타냅니다.
><br>
><br>
>
>### 🟨 알파와 베타
>🔸**Alpha [%]**:<br>
>알파 (15.40%)<br>
>→ 시장 대비 초과 성과를 나타냅니다. 양수일 경우 시장보다 더 나은 성과를 
>낸 것입니다. &nbsp;&nbsp;(벤치마크 필요)
>
>🔸**Beta**:<br>
>베타 (0.13126)<br>
>→ 전략이 시장 움직임에 얼마나 민감하게 반응하는지를 나타냅니다. 값이 
>낮을수록 시장에 덜 민감합니다. &nbsp;&nbsp;(벤치마크 필요)
><br>
><br>
>
>### 🟨 손실 지표
>🔸**Max. Drawdown [%]**:<br>
>최대 손실 (-3.61%)<br>
>→ 전략 기간 중 계좌 잔고에서 가장 큰 하락 폭을 나타냅니다.
>
>🔸**Avg. Drawdown [%]**:<br>
>평균 손실 (-0.74%)<br>
>→ 모든 손실 구간에서 평균적인 하락 폭을 나타냅니다.
>
>🔸**Max. Drawdown Duration**:<br>
>최대 손실 지속 기간 (84 days)<br>
>→ 최대 손실 구간이 지속된 시간입니다.
>
>🔸**Avg. Drawdown Duration**:<br>
>평균 손실 지속 기간 (17 days)<br>
>→ 모든 손실 구간에서 평균적으로 지속된 시간입니다.
>
>### 거래 통계
>🔸**Trades**:<br>
>총 거래 횟수 (405회)<br>
>→ 전략 기간 동안 수행된 거래의 총 개수입니다.
>
>🔸**Win Rate [%]**:<br>
>승률 (70.37%)<br>
>→ 전체 거래 중 이익을 낸 거래의 비율입니다.
>
>🔸**Best Trade [%]**:<br>
>최고 거래 수익률 (15.96%)<br>
>→ 가장 높은 수익률을 기록한 거래입니다.
>
>🔸**Worst Trade [%]**:<br>
>최악 거래 손실률 (-8.71%)<br>
>→ 가장 큰 손실률을 기록한 거래입니다.
>
>🔸**Avg. Trade [%]**:<br>
>평균 거래 수익률 (2.87%)<br>
>→ 모든 거래에서 평균적으로 얻은 수익률입니다.
>
>### 거래 지속 시간
>🔸**Max. Trade Duration**:<br>
>최장 거래 지속 시간 (56 days)<br>
>→ 하나의 거래가 가장 오래 지속된 기간입니다.
>
>🔸**Avg. Trade Duration**:<br>
>평균 거래 지속 시간 (19 days)<br>
>→ 모든 거래에서 평균적으로 지속된 시간입니다.
><br>
><br>
>
>### 🟨 기대성과 및 기타 지표
>🔸**Profit Factor**:<br>
>이익 요인 (6.30247)<br>
>→ 총 이익 대비 총 손실의 비율로, 값이 높을수록 좋은 성과를 의미합니다.
>
>🔸**Expectancy [%]**:<br>
>기대치 (2.97%)<br>
>→ 한 번의 거래당 기대되는 평균 수익률입니다.
>
>🔸**SQN**:<br>
>시스템 품질 번호 (10.11998)<br>
>→ 시스템의 성능을 평가하는 지표로, 값이 높을수록 우수한 시스템을 >의미합니다.
>
>🔸**Kelly Criterion**:<br>
>켈리 기준값 (0.6211)
>→ 자산 배분 비율을 계산하기 위한 지표로, 값이 클수록 공격적인 투자 >전략에 적합합니다.
><br>
><br>
>
>### 🟨 전략 이름
>🔸**_strategy**:<br>
>사용한 전략 이름 ("SmaBollingerStrategy")
>→ 이 결과를 도출하기 위해 사용한 트레이딩 전략 이름입니다.


---

## 백테스트 결과 분석 시 할 수 있는 것들
### 1. 



## 매도 조건 리디자인 필요

1. **스코어가 낮다고 바로 매도하지 말고, 현재 수익률이 양수일 경우에만 매도하는 조건 추가하는 것도 고려**<br>
예시:

```python
if score <= -1.5 and has_position and roi >= 0:
    self.sell(...)
```
또는, 스코어 < -2.0과 동시에 MACD Dead Cross와 같이 복합 조건 도입

2. **전략 분화**

단기 전략 vs 중기 전략 분리하여 각각 스코어 기준 다르게 적용

조정장에서 견디는 전략: trailing stop 또는 수익률 기반 보호 매도 전략 도입

3. **전략 트레이싱 추가**

로그에 “포지션 보유 기간”이나 “보유 중 최대 수익률” 등의 지표 추가해 인내했으면 어땠을까 시뮬레이션 가능