"""Ledger (가계부) tools: get_budget_summary (read), record_transaction (write). Owner: 팀원 A."""
import re
from datetime import date

from src.tools.data_store import load, save

KINDS = ["income", "expense", "save_emergency", "save_short", "save_long"]
CATEGORIES = {
    "income": ["용돈", "아르바이트", "기타수입"],
    "expense": ["식비", "교통", "카페", "쇼핑", "통신", "문화", "기타지출"],
}
BUCKET_OF = {"save_emergency": "emergency", "save_short": "short_term", "save_long": "long_term"}


def _positive_won(value):
    """Return value as a positive int, or None if it is not a positive number."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        return None
    return int(round(value))


def get_budget_summary(month: str = "") -> dict:
    """Summarize one month of the ledger: totals, free cash, and the top 3 expense categories."""
    records = load("ledger")["records"]
    months = sorted({r["date"][:7] for r in records})
    if not isinstance(month, str) or (month and not re.fullmatch(r"\d{4}-\d{2}", month)):
        return {"error": f"Month '{month}' is not in YYYY-MM format. Use a month like '2026-09'."}
    month = month or months[-1]
    rows = [r for r in records if r["date"].startswith(month)]
    if not rows:
        return {"error": f"No records for {month}. Months with records: {', '.join(months)}. "
                         "Call get_budget_summary with one of them."}
    total = lambda kinds: sum(r["amount"] for r in rows if r["kind"] in kinds)  # noqa: E731
    income, expense, saved = total(["income"]), total(["expense"]), total(BUCKET_OF)
    by_cat = {}
    for r in rows:
        if r["kind"] == "expense":
            by_cat[r["category"]] = by_cat.get(r["category"], 0) + r["amount"]
    top = sorted(by_cat.items(), key=lambda kv: kv[1], reverse=True)[:3]
    return {"month": month, "income": income, "expense": expense, "saved": saved,
            "free_cash": income - expense - saved,
            "top_expenses": [{"category": c, "amount": a} for c, a in top]}


def record_transaction(kind: str, amount: int, category: str = "", memo: str = "") -> dict:
    """Add one income/expense/saving row to the ledger. Saving rows also update the bucket balance."""
    if kind not in KINDS:
        return {"error": f"Unknown kind '{kind}'. Use one of: {', '.join(KINDS)}."}
    won = _positive_won(amount)
    if won is None:
        return {"error": "Amount must be a positive number of won, e.g. 9000."}
    if kind in CATEGORIES and category not in CATEGORIES[kind]:
        return {"error": f"Unknown {kind} category '{category}'. Use one of: {', '.join(CATEGORIES[kind])}."}
    row = {"date": date.today().isoformat(), "kind": kind,
           "category": category if kind in CATEGORIES else "저축", "amount": won, "memo": str(memo)[:40]}
    ledger = load("ledger")
    ledger["records"].append(row)
    save("ledger", ledger)
    if kind not in BUCKET_OF:
        return {"recorded": row}
    buckets = load("buckets")
    bucket = BUCKET_OF[kind]
    buckets[bucket] += won
    save("buckets", buckets)
    return {"recorded": row, "bucket": bucket, "balance": buckets[bucket]}


GET_BUDGET_SUMMARY_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_budget_summary",
        "description": "한 달 가계부의 수입, 지출, 저축 배분액, 여유자금과 지출 상위 3개 항목을 요약해 돌려준다. 맡길 금액을 정하거나 이번 달 돈 상황을 물을 때 쓴다.",
        "parameters": {
            "type": "object",
            "properties": {
                "month": {"type": "string", "description": "'YYYY-MM' 형식의 달, 예: '2026-09'. 비우면 가장 최근 달"},
            },
            "required": [],
        },
    },
}

RECORD_TRANSACTION_SCHEMA = {
    "type": "function",
    "function": {
        "name": "record_transaction",
        "description": "가계부에 수입·지출을 기록하거나 비상금·단기·장기 저축 입금을 기록한다. 데이터를 바꾸므로 반드시 사용자 확인을 받은 뒤에 호출한다.",
        "parameters": {
            "type": "object",
            "properties": {
                "kind": {"type": "string", "enum": KINDS,
                         "description": "income(수입), expense(지출), save_emergency(비상금), save_short(단기 저금), save_long(장기 투자)"},
                "amount": {"type": "integer", "description": "원 단위 양수 금액, 예: 9000"},
                "category": {"type": "string",
                             "description": "income: 용돈/아르바이트/기타수입, expense: 식비/교통/카페/쇼핑/통신/문화/기타지출. 저축이면 비워 둠"},
                "memo": {"type": "string", "description": "짧은 메모, 예: '점심'"},
            },
            "required": ["kind", "amount"],
        },
    },
}
