"""Command-line chat with the agent. Copied from the café agent (Task 4)."""
from src.agent import Agent


def main():
    agent = Agent()
    print("목돈 마련 에이전트 — 종료하려면 exit")
    while True:
        text = input("You: ").strip()
        if text.lower() in ("exit", "quit"):
            break
        if text:
            print("Agent: " + agent.run(text)["answer"])


if __name__ == "__main__":
    main()
