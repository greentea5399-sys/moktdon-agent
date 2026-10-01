"""Savings tools: get_goal_status (read), allocate_savings (compute). Owner: 팀원 B.
allocate_savings is the tool a café owner never needs.
"""
from datetime import date

from src.tools.data_store import load

LONG_HORIZON_MONTHS = 36           # 36개월 이상이면 장기 위주
SHORT_RATIO = {False: 0.7, True: 0.3}  # key: 장기 목표인가? -> 단기 비율


def _months_until(target_month: str) -> int:
    """Months from this month to 'YYYY-MM' (this month -> 0)."""
    year, month = map(int, target_month.split("-"))
    today = date.today()
    return (year - today.year) * 12 + (month - today.month)


def get_goal_status() -> dict:
    """Return the goal item, months left, money saved so far, what is still missing, and the emergency-fund gap."""
    goal, buckets = load("goal"), load("buckets")
    for key in ("item", "price", "target_month", "emergency_target"):
        if key not in goal:
            return {"error": f"Goal data is missing '{key}'. Fix data/goal.json and try again."}
    saved = buckets["short_term"] + buckets["long_term"]
    return {
        "item": goal["item"], "price": goal["price"], "target_month": goal["target_month"],
        "months_left": max(_months_until(goal["target_month"]), 0),
        "saved": saved, "remaining": max(goal["price"] - saved, 0),
        "progress_pct": round(saved / goal["price"] * 100, 1),
        "emergency_gap": max(goal["emergency_target"] - buckets["emergency"], 0),
        "monthly_deposit": goal.get("monthly_deposit"),
        "assumed_annual_rates": goal.get("assumed_annual_rates"),
    }


def _whole_number(value):
    """Return value as int if it is a whole number (not bool), else None."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value != int(value):
        return None
    return int(value)


def allocate_savings(amount: int, months_left: int, emergency_gap: int) -> dict:
    """Split the entrusted money: fill the emergency gap first, then short/long by the time left to the goal."""
    amount, months_left, emergency_gap = map(_whole_number, (amount, months_left, emergency_gap))
    if amount is None or amount <= 0:
        return {"error": "Amount must be a positive number of won, e.g. 300000."}
    if months_left is None or months_left <= 0:
        return {"error": "months_left must be 1 or more. Call get_goal_status to get the correct value."}
    if emergency_gap is None or emergency_gap < 0:
        return {"error": "emergency_gap cannot be negative. Call get_goal_status to get the correct value."}
    emergency = min(amount, emergency_gap)
    rest = amount - emergency
    is_long = months_left >= LONG_HORIZON_MONTHS
    short = round(rest * SHORT_RATIO[is_long])
    ratio = "단기 30% / 장기 70%" if is_long else "단기 70% / 장기 30%"
    horizon = f"{LONG_HORIZON_MONTHS}개월 이상" if is_long else f"{LONG_HORIZON_MONTHS}개월 미만"
    rule = (f"비상금 부족분 {emergency}원을 먼저 채움. " if emergency else "비상금은 이미 충분함. ") + \
           f"목표까지 {months_left}개월({horizon})이라 나머지를 {ratio}로 배분"
    return {"amount": amount, "emergency": emergency, "short_term": short, "long_term": rest - short, "rule": rule}


GET_GOAL_STATUS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_goal_status",
        "description": "사고 싶은 목표 물건의 가격, 목표 시점까지 남은 개월 수, 지금까지 모은 목돈, 부족한 금액, 비상금 부족액을 돌려준다. 돈을 배분하기 전에 먼저 호출한다.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}

ALLOCATE_SAVINGS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "allocate_savings",
        "description": "맡긴 금액을 비상금, 단기(저금), 장기(투자)로 정해진 규칙에 따라 나눈다. months_left와 emergency_gap은 get_goal_status 결과를 그대로 넣는다.",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {"type": "integer", "description": "맡긴 금액(원), 예: 300000"},
                "months_left": {"type": "integer", "description": "목표까지 남은 개월 수 (get_goal_status의 months_left)"},
                "emergency_gap": {"type": "integer", "description": "비상금 부족액(원) (get_goal_status의 emergency_gap). 다 찼으면 0"},
            },
            "required": ["amount", "months_left", "emergency_gap"],
        },
    },
}
