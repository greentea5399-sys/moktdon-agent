# Architecture

Same as the café agent. Only the tools and the data are new. (The agent class is called `Agent`.)

## Components
```
main.py (CLI) ──┐
                ├──►  agent.py  ──►  llm_client.py  ──►  LLM API (Groq / xAI)
app.py  (UI)  ──┘        │
                         └──►  tools/__init__.py (registry)  ──►  tools/*.py  ──►  data/*.json
```

| File | Responsibility | Who writes it |
|---|---|---|
| `src/main.py` | CLI loop: read user input, call `agent.run()`, print answer. | copied from café agent |
| `src/app.py` | Streamlit chat UI. Only calls `agent.run()` and shows results. | copied from café agent |
| `src/config.py` | Load settings from `.env` into constants. | copied from café agent |
| `src/llm_client.py` | `chat(messages, tools)` → returns the assistant message. Nothing else. | copied from café agent |
| `src/agent.py` | Holds message history and runs the agent loop. | copied from café agent |
| `src/tools/data_store.py` | `load(name)` / `save(name, data)` helpers for `data/*.json`. | copied from café agent |
| `src/tools/__init__.py` | `TOOL_SCHEMAS` (list sent to LLM) and `TOOL_FUNCTIONS` (name → function). | your team |
| `src/tools/*.py` | Tool implementations. Pure Python, no LLM calls. | your team |

## The agent loop (in `agent.py`)
```
add user message to history
repeat up to MAX_TOOL_ROUNDS:
    response = chat(system_prompt + history, TOOL_SCHEMAS)
    add response to history
    if response has no tool_calls:
        return response.content          # final answer
    for each tool_call:
        result = TOOL_FUNCTIONS[name](**arguments)   # catch errors → {"error": ...}
        add {"role": "tool", "tool_call_id": id, "content": json(result)} to history
return "Sorry, I could not finish this request."
```

Nothing in this loop mentions a café. That is why you can reuse it.

## Context sent to the LLM on every call
1. **System prompt** — from `prompts/system_prompt.md` (always first, never trimmed)
2. **Tool schemas** — names, descriptions, parameters
3. **History** — user messages, assistant messages, tool results (trimmed to last `MAX_HISTORY_MESSAGES`)

Everything in this list costs tokens and affects the agent's decisions. Keep it clean.

## Data files
List every file in `data/` with one example of its shape. Tools use `load("<name>")` and `save("<name>", data)`.

- `data/ledger.json` — 가계부. `{"records": [{"date": "2026-09-05", "kind": "expense", "category": "식비", "amount": 128000, "memo": "장보기·외식"}, ...]}`. kind는 income, expense, save_emergency, save_short, save_long
- `data/goal.json` — 목표 물건과 규칙 설정. `{"item": "맥북 프로 14", "price": 3000000, "target_month": "2027-12", "monthly_deposit": 300000, "emergency_target": 900000, "assumed_annual_rates": {"short_term": 0.03, "long_term": 0.06}}`
- `data/buckets.json` — 통장별 잔액. `{"emergency": 800000, "short_term": 640000, "long_term": 360000}`
