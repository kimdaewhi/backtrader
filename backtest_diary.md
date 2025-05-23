# 🧾 Backtest Simulation Log – Oracle (2022 ~ 2024)

## 📌 백테스트 조건

- **백테스트 기간** : 2022.01.01 ~ 2024.12.31 (약 3년 가량)  
- **종목** : Oracle  
- **초기 자본금** : $10,000  
- **커미션(거래수수료)** : 0.002  



## ⚙️ 전략 구성

**전략은 스코어 기반의 전략이며, 4가지 보조지표를 활용 중이다.**

- 총합 스코어 : ± 10  
- EMA Crossover + ADX : ± 4  
- MACD 히스토그램 : ± 2  
- RSI Score : ± 2  
- Volume Score : ± 2  



## 🔄 매매 로직

- **score 매매 임계값**
  - 매수 : 1.5 이상  
  - 매도 : 1.5 이하  

- **매수 조건** : 스코어가 매수 임계값 이상이고 포지션 없음 → 50% 자금 투입  
- **매도 조건** : 스코어가 매도 임계값 이하이고 포지션 있음 → 보유량 50% 매도  
<br><br><br>

## 📊 백테스트 시뮬레이션 & 전략 튜닝의 흐름

1. 전략의 성능 정량 분석  
2. 스코어와 수익률의 상관 분석  
3. 조건 튜닝 & 임계값 시뮬레이션  
<br><br>

## ⚠️ score 기반 매매의 문제점

**근본적으로 내가 하고자 했던 매도의 목적은 큰 손실을 피하려고 한 거임. 그러나 상승장에서 조정이 왔을 때 문제가 생김.**


### [문제 1]

- 매수 후에 실제로 하락폭이나 상승폭이 크지는 않지만, 종합 스코어 때문에 전략이 민감하게 반응해서 시장의 조정을 견디지 못하고 팔아버림.  
- 매수 후 견디지 못하고 찔끔찔끔 팔아버리는 sell이 근본적인 문제인 것 같음.

**[해결 1]**

- 매도조건 리디자인  
- 트레일링 스탑 / 수익률 기반 보호 매도(이게 이익 보존?; Profit Preservation) / 전략 트레이싱?  

---

### [문제 2]

- 7% 이상 손실, 15% 이상 수익인 구간이 발생하면 청산(or 실현)  
- 포지션 청산 시에 100% 청산해버림.  
- 이게 Sharp Ratio가 안 좋게 나오는 이유 중 하나가 되는 거 같음. 맞나...?

**[해결 2]**

- 어떻게?

---

### [문제 3]

- 매수도 문제가 있네. 지금 조건식을 보면 포지션이 없을 때만 매수를 가능하게 했는데, 이 경우에는 불타기가 안 되잖아.  
- 즉 추세추종 매수가 안 된다는 거지.  
- 이 부분도 내 생각에는 수정해야 할 것 같은데...
  두 가지 경우 모두 백테스트 후 결과를 보자


## 🧷 트레일링 스탑 도입

1. 기준가격 : 매수 이후 기록된 최고가  
2. 트레일링 스탑 가격 : 기준가격에서 일정 비율(ex. -7%) 하락한 주가  
3. 청산조건 : 현재가가 트레일링 스탑 가격보다 낮아졌을 때 자동매도  
<br><br><br>


## ❗ 트레일링 스탑 도입 후 문제점

**우리가 맨 처음에 문제가 됐었던 게 뭐였지?**  
매수 타이밍은 괜찮았지만 매도가 너무 빈번하게 발생해서, 즉 매도를 찔끔찔끔 하는 게 문제였잖아.

그래서 생각해놓은 방법이 뭐지?  
**'트레일링 스탑' 도입.**  
왜냐? 보수적으로 매도해야겠다는 의미였지만, 시장 조정에 찔끔찔끔 팔아버리는 역효과를 낳음.

그래서 '트레일링 스탑'을 도입했는데, 현재 문제는?  
반대로 트레일링 스탑 drawdown이나 손/익절 조건에 걸리지 않으면  
**'매도 자체를 수행하지 않음.'** 매수만 진행해.

그리고, 시장이 조정 중일 때도 10% 마이너스는 종종 일어나는 현상인 것 같은데...

도대체 이런 경우에는 어떻게 해야 할까?  
지금은 기존에 쓰던 매도 조건이 전부 주석처리되어서 그렇다고 쳐.

그런데 내가 머리가 아픈 건.  
**어떻게 매도를 '잘' 해야 하는 거지? 너무너무 어렵다 하...**

이미지는 내가 백테스트 시뮬레이션을 돌린 기간 오라클의 전반적인 주가 추이야.
<br><br><br>

## 💥 트레일링 스탑 도입 후 두 번째 고찰

**매도 전략의 진짜 딜레마에 빠짐**

- 처음 문제 : 매수는 괜찮아보임 but 매도 로직이 이상해서 수익률 & 승률 & sharp ratio 등 지표가 안 나옴. (매도가 줄줄 샘...)  
- 두 번째 문제 : 조건에 안 걸리면 매도 자체가 안 됨 (매도 트리거 없음)


### 1. 너무 보수적인 매도 트리거

- 트레일링 스탑 (7%) / 손절(-7%) / 익절(+15%) 외에 나머지는 전부 무시되고 있음

### 2. "시장 조정" or "점수 하락" 같은 Soft Signal 무시

- 종합 스코어가 분명히 하락하고 있는데, 가격이 하락 안 했다고 그냥 들고 있음  
- → 결국 손실 커진 후에 뒤늦게 손절

### 3. 전략이 말 그대로 ‘조건 반응형’이지, 상황을 파악하고 ‘판단형’이 아님

- 그냥 if this then that 식 자동반응

---

**해결 방법은?**  
👉 핵심은 "복합적 판단" 기반의 매도 조건 설계.  
👉 "조건만 있는 전략"을 만들지 말자.  
👉 전략 설계에 '판단'을 섞어보자.  
👉 여러 지표를 보고, 사람처럼 매수/매도 판단을 할 수 있도록, 여러 지표를 다양하게 활용해보자.
<br><br><br>


## 🧠 '판단형' 전략으로 진화하기 위한 첫 번째 과제


### 1️⃣ 스코어의 구간별 의미를 정리

- 스코어 범위는 `-10 ~ +10`

- 각 구간별로 **시장 상태를 분류**할 수 있지 않을까?

- 예를 들어, **3개월간 평균 스코어**가 아래와 같고  
  이를 기반으로 정규 분포를 적용해 시장의 흐름을 판단한다면?

> - **-10 ~ -4** : 급격한 하락장  
> - **-4 ~ 0** : 점진적(?) 하락장  
> - **-2 ~ 2** : 횡보장  
> - **0 ~ 4** : 점진적? 상승장  
> - **5 ~ 10** : 가파른 상승장

👉 이런 식으로 **시장 흐름의 컨텍스트**를 먼저 잡아보라는 이야기일까?
<br>


### 2️⃣ 흐름별로 유의해서 봐야 할 보조지표는?

- 만약 위에서 말한 대로 **시장 흐름이 나뉜다면**,  
  흐름별로 **주의 깊게 확인해야 할 보조지표**도 다를 수 있음.

예를 들어:

- **가파른 상승장**이라면  
  - RSI가 `70 이상`,  
  - 거래량이 매우 높고,  
  - 주가가 **볼린저밴드 상단**을 터치할 가능성이 큼.

- 반대로 하락장이라면  
  - RSI가 급락 중이거나,  
  - MACD 히스토그램이 약해지고 있을 수도 있고...?

👉 이런 지표들을 **시장 흐름별로 조합해서** 보는 게 핵심일까?
<br>


### 3️⃣ 스코어의 변화량(모멘텀)을 도입하자

- 중요한 건 **"지금 좋은가?"** 보다  
  → **"좋아지고 있는가? 나빠지고 있는가?"**  

- 즉, **절대값이 아니라 방향성(추세)** 를 따져야 함.

> 그런데 아직은 **세부적으로 어떻게 판단해야 할지**는 머릿속에 떠오르는 것이 없음.  
> 이게 내가 말하는 **델타 스코어**라는 개념.
<br><br><br>




## 🗓️ [2025.05.02] Market Regime을 판단하기 위한 지표 활용과 기존 regime 판단 로직 검토

### ✨ 목적

- **Market Regime(시장 흐름)** 에 따라서 **매매 전략을 다르게 적용하기 위한 기반 설계 중**  
- 이를 위해 먼저 **Market Regime 자체를 어떻게 판단할 것인지** 고민 시작

---

### ⚠️ 현재 문제 상황

- Market Regime이 **제대로 판단되지 않고 있음**

> - 하락장인데 `volatile` 이라고 나온다...?  
> - 상승장인데 `bull`로 분류되지 않는다...?  
> - 하루 단위로 시황이 바뀌는 등 **노이즈가 너무 많다**  

→ 시장 흐름 판단의 **일관성·신뢰성 부족**

---

### 🔍 왜 그럴까? 원인 분석

- **기존 로직**은 `z-score`와 `표준편차` 기반의 판단
- 그래서 아래와 같은 한계가 있었음:

---

#### 🧠 표준편차 개념 재정리

- 표준편차는 단지  
  **"시계열 데이터가 평균에서 얼마나 퍼져 있는가?"**  
  를 측정하는 도구일 뿐

> 즉, 표준편차는  
> - 시장의 **방향성(trend)** 을 알려주지 않는다  
> - 단지 **노이즈 수준 / 분산 정도** 만 제공한다  

---

#### ⚠️ z-score도 마찬가지

- z-score는 특정 시점에서 현재가가 평균 대비  
  **몇 σ(표준편차)** 만큼 떨어져 있는지를 보여주는 값

- 이것도 방향성보다는  
  **평균 대비 이탈 정도를 수치화**한 것일 뿐

---

### 📌 정리하면...

- 지금 사용하는 Market Regime 판단 로직은  
  - **방향성(TREND)을 제대로 측정하지 못하고**,  
  - **노이즈가 많은 구간에서는 자주 오판**을 유발함

---

### 🔧 다음 액션 아이디어

- 📈 **방향성 지표** : MACD, EMA 기울기, Price Momentum 등  
- 📊 **추세 강도 지표** : ADX, RSI, MACD Histogram 등  
- 🔇 **노이즈 필터링 지표** : ATR, Bollinger Band Width, z-score 변화량

큰 틀에서 세 가지 지표를 **조합해서** 더 정교한 Market Regime 분류 체계를 설계해야 할 듯


