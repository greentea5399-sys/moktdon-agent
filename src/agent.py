"""The agent: keeps conversation history and runs the tool-calling loop.
Copied from the café agent (Tasks 4, 7a, 7b, 9). Nothing here knows about money or shopping.
"""
import json

from src import config
from src.llm_client import chat
from src.tools import TOOL_FUNCTIONS, TOOL_SCHEMAS


class Agent:
    def __init__(self, verbose: bool = True):
        self.system_prompt = config.SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        self.history: list = []  # user, assistant, and tool messages (NOT the system prompt)
        self.verbose = verbose

    def _build_context(self) -> list:
        """System prompt + about the last MAX_HISTORY_MESSAGES messages.
        The cut always lands on a user message, so a tool_call is never separated from its results
        and the current question is never dropped."""
        start = max(0, len(self.history) - config.MAX_HISTORY_MESSAGES)
        while start > 0 and self.history[start]["role"] != "user":
            start -= 1
        return [{"role": "system", "content": self.system_prompt}] + self.history[start:]

    def _execute_tool(self, name: str, arguments_json: str) -> dict:
        """Run one tool safely. Never raise: return {"error": ...} on any problem."""
        func = TOOL_FUNCTIONS.get(name)
        if func is None:
            return {"error": f"Unknown tool '{name}'. Use one of: {', '.join(TOOL_FUNCTIONS)}."}
        try:
            args = json.loads(arguments_json or "{}")
            return func(**args)
        except json.JSONDecodeError:
            return {"error": "Arguments were not valid JSON. Try the call again."}
        except TypeError as exc:
            return {"error": f"Wrong arguments for {name}: {exc}. Check the tool's parameters."}
        except Exception as exc:  # last safety net
            return {"error": f"{name} failed: {exc}"}

    @staticmethod
    def _assistant_dict(msg) -> dict:
        """Turn the SDK message object into a plain dict we can send back to the API."""
        entry = {"role": "assistant", "content": msg.content or ""}
        if msg.tool_calls:
            entry["tool_calls"] = [
                {"id": c.id, "type": "function",
                 "function": {"name": c.function.name, "arguments": c.function.arguments}}
                for c in msg.tool_calls
            ]
        return entry

    def run(self, user_input: str) -> dict:
        """Handle one user message. Return {"answer": str, "steps": [(name, args, result), ...]}."""
        self.history.append({"role": "user", "content": user_input})
        steps = []
        for _ in range(config.MAX_TOOL_ROUNDS):
            msg = chat(self._build_context(), TOOL_SCHEMAS)
            self.history.append(self._assistant_dict(msg))
            if not msg.tool_calls:
                return {"answer": msg.content, "steps": steps}
            for call in msg.tool_calls:
                result = self._execute_tool(call.function.name, call.function.arguments)
                steps.append((call.function.name, call.function.arguments, result))
                if self.verbose:
                    print(f"🔧 {call.function.name}({call.function.arguments}) → {json.dumps(result, ensure_ascii=False)}")
                self.history.append({"role": "tool", "tool_call_id": call.id,
                                     "content": json.dumps(result, ensure_ascii=False)})
        return {"answer": "죄송합니다. 이번 요청을 끝내지 못했어요.", "steps": steps}
