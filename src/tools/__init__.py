"""Tool registry: the single place where tools are connected to the agent.

TOOL_SCHEMAS   -> sent to the LLM (what the model can SEE)
TOOL_FUNCTIONS -> used by agent.py (what actually RUNS)

When you add a tool: import its function and schema, then add both below.
"""
from src.tools.calculator import CALCULATE_SCHEMA, calculate
from src.tools.ledger_tools import (GET_BUDGET_SUMMARY_SCHEMA, RECORD_TRANSACTION_SCHEMA,
                                    get_budget_summary, record_transaction)
from src.tools.savings_tools import (ALLOCATE_SAVINGS_SCHEMA, GET_GOAL_STATUS_SCHEMA,
                                     allocate_savings, get_goal_status)

TOOL_SCHEMAS = [
    CALCULATE_SCHEMA,
    GET_BUDGET_SUMMARY_SCHEMA,
    RECORD_TRANSACTION_SCHEMA,
    GET_GOAL_STATUS_SCHEMA,
    ALLOCATE_SAVINGS_SCHEMA,
]

TOOL_FUNCTIONS = {
    "calculate": calculate,
    "get_budget_summary": get_budget_summary,
    "record_transaction": record_transaction,
    "get_goal_status": get_goal_status,
    "allocate_savings": allocate_savings,
}
