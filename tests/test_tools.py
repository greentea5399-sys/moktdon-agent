"""Tool tests. No LLM needed. One ok test and one error test per tool.
Run one group:  python -m pytest tests -k allocate
"""
from src.tools.calculator import calculate
from src.tools.data_store import load
from src.tools.ledger_tools import get_budget_summary, record_transaction
from src.tools.savings_tools import allocate_savings, get_goal_status


# ---- Already done ----
def test_calculate_ok():
    assert calculate("3 * 4500 * 0.9")["result"] == 12150.0


def test_calculate_error_has_hint():
    assert "error" in calculate("import os")


# ---- Task 7: get_budget_summary ----
def test_get_budget_summary_ok():
    out = get_budget_summary("2026-09")
    assert out["income"] == 720000 and out["expense"] == 367500 and out["saved"] == 300000
    assert out["free_cash"] == 52500
    assert out["top_expenses"][0] == {"category": "식비", "amount": 128000}


def test_get_budget_summary_error_has_hint():
    assert "YYYY-MM" in get_budget_summary("9월")["error"]
    assert "get_budget_summary" in get_budget_summary("2026-03")["error"]


# ---- Task 8: record_transaction ----
def test_record_transaction_ok():
    before = len(load("ledger")["records"])
    out = record_transaction("expense", 9000, "식비", "점심")
    assert out["recorded"]["amount"] == 9000
    assert len(load("ledger")["records"]) == before + 1


def test_record_transaction_saving_updates_bucket():
    out = record_transaction("save_short", 140000)
    assert out["bucket"] == "short_term" and out["balance"] == 640000 + 140000


def test_record_transaction_error_has_hint():
    assert "식비" in record_transaction("expense", 13500, "구독")["error"]
    assert "income" in record_transaction("spend", 1000)["error"]


# ---- Task 9: get_goal_status ----
def test_get_goal_status_ok():
    out = get_goal_status()
    assert out["saved"] == 1000000 and out["remaining"] == 2000000
    assert out["emergency_gap"] == 100000 and out["progress_pct"] == 33.3


def test_get_goal_status_error_has_hint(temp_data):
    (temp_data / "goal.json").write_text('{"item": "맥북"}', encoding="utf-8")
    assert "data/goal.json" in get_goal_status()["error"]


# ---- Task 10: allocate_savings ----
def test_allocate_savings_ok():
    out = allocate_savings(300000, 14, 100000)
    assert (out["emergency"], out["short_term"], out["long_term"]) == (100000, 140000, 60000)


def test_allocate_savings_long_goal():
    out = allocate_savings(300000, 40, 0)
    assert (out["emergency"], out["short_term"], out["long_term"]) == (0, 90000, 210000)


def test_allocate_savings_error_has_hint():
    assert "get_goal_status" in allocate_savings(300000, 0, 0)["error"]
