# 💰 목돈 마련 에이전트

사고 싶은 물건이 있는 사용자가 매달 맡긴 돈을 정해진 규칙대로 비상금·단기(저금)·장기(투자)로 나누고, 가계부를 기록하도록 돕는 에이전트입니다.
고급 비즈니스 프로그래밍 팀 실습(`agent-template`) 형식으로 만들었습니다. 과제 설명은 `ASSIGNMENT.ko.md`, 원래 템플릿 안내는 `README.ko.md`를 보세요.

## 도구
| 도구 | 유형 | 파일 | 하는 일 |
|---|---|---|---|
| `get_budget_summary` | read | `src/tools/ledger_tools.py` | 한 달 수입·지출·저축·여유자금 요약 |
| `record_transaction` | write | `src/tools/ledger_tools.py` | 가계부 기록, 저축이면 통장 잔액 반영 (확인 후) |
| `get_goal_status` | read | `src/tools/savings_tools.py` | 목표 물건까지 남은 금액·개월·비상금 부족액 |
| `allocate_savings` | compute | `src/tools/savings_tools.py` | **카페에 없는 도구.** 규칙대로 비상금·단기·장기 배분 |
| `calculate` | compute | `src/tools/calculator.py` | 제공된 계산기 |

## 실행
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Groq 또는 xAI API 키 입력

python -m pytest tests           # 형식 검사 + 도구 테스트 (LLM 불필요)
python -m src.main               # 터미널에서 대화
streamlit run src/app.py         # 브라우저에서 대화
```

목표 물건을 바꾸려면 `data/goal.json`의 `item`, `price`, `target_month`만 고치면 됩니다.
시나리오는 `tests/scenarios.md`에 있습니다. write 시나리오 전에 `cp -r data data_backup`으로 백업해 두세요.
