import json
from groq import Groq
import os
from dotenv import load_dotenv
from schemas import AgentAction
from tools import calculator, web_search

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a task-solving assistant. Given a task, decide ONE action at a time.

Available tools:
- web_search: search the web for information. input = a search query.
- calculator: evaluate a math expression. input = the expression, e.g. "42*3.5"
- finish: call this when you have the final answer. input = your final answer.

Respond with ONLY a JSON object, no other text, in exactly this shape:
{"thought": "<your reasoning>", "tool": "<one of web_search|calculator|finish>", "tool_input": "<the input>"}
"""

def run_agent(task: str, max_steps: int = 5):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Task: {task}"},
    ]

    for step in range(1, max_steps + 1):
        print(f"\n--- Step {step} ---")

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.2,
        )
        raw_text = response.choices[0].message.content
        action = AgentAction.model_validate_json(raw_text)

        print(f"Thought: {action.thought}")
        print(f"Tool: {action.tool.value} | Input: {action.tool_input}")

        if action.tool.value == "finish":
            print(f"\nFINAL ANSWER: {action.tool_input}")
            return action.tool_input

        # ACT: run the tool
        if action.tool.value == "calculator":
            result = calculator(action.tool_input)
        elif action.tool.value == "web_search":
            result = web_search(action.tool_input)
        else:
            result = "ERROR: unknown tool"

        print(f"Observation: {result}")

        # append this round to the conversation so the model sees it next time
        messages.append({"role": "assistant", "content": raw_text})
        messages.append({"role": "user", "content": f"Observation: {result}"})

    print("\nStopped: reached max steps without finishing.")
    return None


if __name__ == "__main__":
    run_agent("Who is the current CEO of Anthropic, and what is 12 times 8?")