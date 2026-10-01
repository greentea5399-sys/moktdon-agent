# 테스트 시나리오

`python -m src.main`을 실행하고 각 프롬프트를 입력합니다. 실제 도구 호출을 예상 도구 호출과 비교합니다.
순서는 조금 달라도 됩니다. 중요한 것은 에이전트가 추측하지 않고 도구를 쓰는지입니다.

| # | 종류 | 프롬프트 | 예상 도구 호출 | 확인할 것 |
|---|---|---|---|---|
| A | 도구 3개 연결 | 이번 달 30만 원 맡길게. 어떻게 나눠? 그리고 단기·장기에서 1년 뒤 이자는 얼마나 붙어? | `get_goal_status` → `allocate_savings` → `calculate` | 비상금 100,000 / 단기 140,000 / 장기 60,000. 1년 예상 이자 140000×0.03 + 60000×0.06 = 7,800원 |
| B | 오류 회복 | 3월에 돈 얼마 썼어? | `get_budget_summary("2026-03")` → 오류(기록 있는 달: 2026-09, 2026-10) → 사용자에게 알리거나 `get_budget_summary("2026-09")` | 3월 기록이 없다고 설명하고, 기록이 있는 달을 안내함 |
| C | write 전 확인 | 점심값 9,000원 가계부에 적어줘 | (확인 질문) → `record_transaction(kind="expense", amount=9000, category="식비", memo="점심")` | 먼저 확인하고, "네" 다음에만 `data/ledger.json`이 바뀜 |
| D | 배분 후 기록 | (A 다음에) 그대로 입금해줘 | (확인 질문) → `record_transaction` × 3 (save_emergency, save_short, save_long) | 확인 후 `data/buckets.json` 잔액이 늘어남 |
| E | 오류 회복 2 | 넷플릭스 13,500원 구독료 적어줘 | (확인) → `record_transaction(category="구독")` → 오류(가능한 카테고리) → `record_transaction(category="문화")` | 카테고리를 고쳐서 다시 기록함 |
| F | 진행률 | 맥북까지 얼마 남았어? 매달 30만 원씩이면 몇 달 걸려? | `get_goal_status` → `calculate` | 남은 200만 원 ÷ 30만 원 ≈ 6.7개월 (이자 제외) |

> write 도구를 테스트한 뒤에는 데이터를 원래대로 돌려놓습니다. 테스트 전에 `cp -r data data_backup` 해 두고, 끝나면 `cp data_backup/*.json data/` 로 복원하세요.
