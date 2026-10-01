"""Streamlit chat UI. Copied from the café agent (Task 7b); only the title changed.
Run: streamlit run src/app.py
"""
import json
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # so "src" imports work under streamlit
from src.agent import Agent  # noqa: E402

st.set_page_config(page_title="목돈 마련 에이전트", page_icon="💰")
st.title("💰 목돈 마련 에이전트")

if "agent" not in st.session_state:
    st.session_state.agent = Agent(verbose=False)
    st.session_state.messages = []  # [{"role", "content", "steps"}]


def show_steps(steps):
    if steps:
        with st.expander(f"🔧 Tool calls ({len(steps)})"):
            for name, args, result in steps:
                st.code(f"{name}({args})\n→ {json.dumps(result, ensure_ascii=False)}", language="text")


for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        show_steps(m.get("steps"))

if prompt := st.chat_input("예: 이번 달 30만 원 맡길게, 어떻게 나눠?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            out = st.session_state.agent.run(prompt)
        st.markdown(out["answer"])
        show_steps(out["steps"])
    st.session_state.messages.append({"role": "assistant", "content": out["answer"], "steps": out["steps"]})
