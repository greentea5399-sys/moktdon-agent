# 도구 명세

도구를 구현하기 **전에** 명세를 씁니다. "Purpose" 줄이 곧 LLM이 읽는 도구 설명이 됩니다.

> 항목 이름(`## Tool:`, `- Purpose:` 등)과 도구 이름은 영어 그대로 둡니다. 형식 검사기와 AI 어시스턴트가 이 이름으로 내용을 찾습니다. 내용은 한국어로 써도 됩니다.

## 템플릿
```
## Tool: <도구 이름>
- Owner: <이 도구를 설명할 수 있는 팀원>
- File: src/tools/<파일>.py
- Purpose: <명확한 한 문장 — LLM이 보는 설명>
- Type: read | write | compute
- Parameters: <이름> (<타입>, required|optional) — <설명>
- Returns: <예시 JSON>
- Errors: <언제> → <힌트가 들어 있는 예시 오류 JSON>
- Example request: "<이 도구를 호출하게 만드는 사용자 문장>"
```

## 명세의 각 줄이 코드에서 가는 곳
| 명세 줄 | 코드에서 |
|---|---|
| 도구 이름 | 함수 이름, 스키마의 `"name"`, `TOOL_FUNCTIONS`의 키 — 셋이 모두 같아야 함 |
| Purpose | 스키마의 `"description"`, 글자 그대로 |
| Parameters | 함수의 매개변수, 그리고 스키마의 `"properties"` |
| required / optional | 스키마의 `"required"`. optional 매개변수는 함수에서 기본값을 가짐 |
| Returns | 성공했을 때 함수가 돌려주는 dict |
| Errors | 함수가 돌려주는 `{"error": "..."}` dict, 그리고 테스트 하나 |
| Example request | `tests/scenarios.md`의 한 행 |

## 도구 지도
이 표를 가장 먼저 채웁니다. 도구들이 서로 이어질 수 있는지 한눈에 보입니다.

| 도구 | 유형 | 담당자 | 주로 이 도구의 앞 / 뒤에 쓰이는 도구 |
|---|---|---|---|
| calculate | compute | (제공됨) | `allocate_savings`, `get_goal_status` 뒤에 (예상 이자·수익, 남은 개월 계산) |
| get_budget_summary | read | 팀원 A | 맨 앞 (이번 달 여유자금 확인) → `allocate_savings` 또는 `record_transaction` |
| record_transaction | write | 팀원 A | `allocate_savings` 뒤에 (배분 결과 입금 기록), 또는 단독 (수입·지출 기록) |
| get_goal_status | read | 팀원 B | `allocate_savings` 앞에 (남은 개월, 비상금 부족액 제공) |
| allocate_savings | compute | 팀원 B | `get_goal_status` 뒤 → `calculate` 또는 `record_transaction` |

---

## Tool: calculate
- Owner: (제공됨 — 이미 구현되어 있습니다. 예시로 참고하세요)
- File: src/tools/calculator.py
- Purpose: Evaluate a math expression. Use this for every calculation, including interest, returns, percentages, and totals.
- Type: compute
- Parameters: expression (string, required) — e.g. "3 * 4500 * 0.9"
- Returns: `{"expression": "3 * 4500 * 0.9", "result": 12150.0}`
- Errors: invalid expression → `{"error": "Invalid expression. Use numbers and + - * / ( ) only."}`
- Example request: "How much are 3 lattes with 10% off?"

---

## 우리 팀의 도구 (과제 3–4)
도구마다 템플릿을 한 번씩 복사해서 여기에 채웁니다. 도구는 4개 이상이고, `read` 하나, `write` 하나, 카페에는 없는 도구 하나가 들어 있어야 합니다.

> 참고: 모든 기록이 아니라 **요약**을 돌려주세요. 도구 결과가 크면 컨텍스트를 낭비합니다.

## Tool: get_budget_summary
- Owner: 팀원 A
- File: src/tools/ledger_tools.py
- Purpose: 한 달 가계부의 수입, 지출, 저축 배분액, 여유자금과 지출 상위 3개 항목을 요약해 돌려준다. 맡길 금액을 정하거나 이번 달 돈 상황을 물을 때 쓴다.
- Type: read
- Parameters: month (string, optional) — "YYYY-MM" 형식. 비우면 기록이 있는 가장 최근 달
- Returns: `{"month": "2026-09", "income": 720000, "expense": 367500, "saved": 300000, "free_cash": 52500, "top_expenses": [{"category": "식비", "amount": 128000}, {"category": "쇼핑", "amount": 89000}, {"category": "통신", "amount": 55000}]}`
- Errors: 형식이 틀린 달 → `{"error": "Month '9월' is not in YYYY-MM format. Use a month like '2026-09'."}` / 기록이 없는 달 → `{"error": "No records for 2026-03. Months with records: 2026-09, 2026-10. Call get_budget_summary with one of them."}`
- Example request: "9월에 돈 얼마 썼어?"

## Tool: record_transaction
- Owner: 팀원 A
- File: src/tools/ledger_tools.py
- Purpose: 가계부에 수입·지출을 기록하거나 비상금·단기·장기 저축 입금을 기록한다. 데이터를 바꾸므로 반드시 사용자 확인을 받은 뒤에 호출한다.
- Type: write
- Parameters: kind (string, required) — income, expense, save_emergency, save_short, save_long 중 하나 / amount (integer, required) — 원 단위 양수 / category (string, optional) — income이면 용돈·아르바이트·기타수입, expense면 식비·교통·카페·쇼핑·통신·문화·기타지출. 저축이면 비워 둠 / memo (string, optional) — 짧은 메모
- Returns: `{"recorded": {"date": "2026-10-01", "kind": "expense", "category": "식비", "amount": 9000, "memo": "점심"}}` / 저축이면 `{"recorded": {...}, "bucket": "short_term", "balance": 780000}`
- Errors: 없는 kind → `{"error": "Unknown kind 'spend'. Use one of: income, expense, save_emergency, save_short, save_long."}` / 없는 카테고리 → `{"error": "Unknown expense category '구독'. Use one of: 식비, 교통, 카페, 쇼핑, 통신, 문화, 기타지출."}` / 0 이하 금액 → `{"error": "Amount must be a positive number of won, e.g. 9000."}`
- Example request: "점심값 9,000원 적어줘"

## Tool: get_goal_status
- Owner: 팀원 B
- File: src/tools/savings_tools.py
- Purpose: 사고 싶은 목표 물건의 가격, 목표 시점까지 남은 개월 수, 지금까지 모은 목돈, 부족한 금액, 비상금 부족액을 돌려준다. 돈을 배분하기 전에 먼저 호출한다.
- Type: read
- Parameters: (없음)
- Returns: `{"item": "맥북 프로 14", "price": 3000000, "target_month": "2027-12", "months_left": 14, "saved": 1000000, "remaining": 2000000, "progress_pct": 33.3, "emergency_gap": 100000, "monthly_deposit": 300000, "assumed_annual_rates": {"short_term": 0.03, "long_term": 0.06}}`
- Errors: 목표 파일이 깨졌을 때 → `{"error": "Goal data is missing 'price'. Fix data/goal.json and try again."}`
- Example request: "맥북까지 얼마 남았어?"

## Tool: allocate_savings
- Owner: 팀원 B
- File: src/tools/savings_tools.py
- Purpose: 맡긴 금액을 비상금, 단기(저금), 장기(투자)로 정해진 규칙에 따라 나눈다. months_left와 emergency_gap은 get_goal_status 결과를 그대로 넣는다.
- Type: compute
- Parameters: amount (integer, required) — 맡긴 금액(원) / months_left (integer, required) — 목표까지 남은 개월 수 / emergency_gap (integer, required) — 비상금 부족액(원), 다 찼으면 0
- Returns: `{"amount": 300000, "emergency": 100000, "short_term": 140000, "long_term": 60000, "rule": "비상금 부족분 100000원을 먼저 채움. 목표까지 14개월(36개월 미만)이라 나머지를 단기 70% / 장기 30%로 배분"}`
- Errors: 0 이하 금액 → `{"error": "Amount must be a positive number of won, e.g. 300000."}` / 0 이하 개월 → `{"error": "months_left must be 1 or more. Call get_goal_status to get the correct value."}` / 음수 부족액 → `{"error": "emergency_gap cannot be negative. Call get_goal_status to get the correct value."}`
- Example request: "이번 달 30만 원 맡길게. 어떻게 나눠?"

### 배분 규칙 (allocate_savings)
1. 비상금이 목표(생활비 3개월분)에 못 미치면 부족분만큼 먼저 비상금에 넣는다.
2. 남은 금액은 목표까지 남은 기간으로 나눈다.
   - 36개월 미만: 단기 70%, 장기 30% (곧 써야 할 돈은 원금 손실 위험을 줄인다)
   - 36개월 이상: 단기 30%, 장기 70% (오래 둘 돈은 수익을 더 노린다)
3. 단기 금액은 원 단위로 반올림하고, 장기 = 남은 금액 − 단기.
