import json
import time
from groq import Groq
from storage import save_run
import os
from dotenv import load_dotenv
from schemas import AgentAction
from tools import calculator, web_search
from evaluator import judge_answer

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
    retries_count = 0
    total_tokens = 0
    start_time = time.time()

    for step in range(1, max_steps + 1):
        print(f"\n--- Step {step} ---")

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.2,
        )
        raw_text = response.choices[0].message.content
        total_tokens += response.usage.total_tokens if response.usage else 0

        try:
            action = AgentAction.model_validate_json(raw_text)
        except Exception as e:
            print(f"PARSE FAILED: {e}")
            retries_count += 1
            messages.append({"role": "assistant", "content": raw_text})
            messages.append({
                "role": "user",
                "content": f"Your last response could not be parsed as valid JSON ({e}). Respond again with ONLY a valid JSON object in the exact format specified."
            })
            continue

        print(f"Thought: {action.thought}")
        print(f"Tool: {action.tool.value} | Input: {action.tool_input}")

        if action.tool.value == "finish":
            print(f"\nFINAL ANSWER: {action.tool_input}")
            print(f"Retries needed: {retries_count}")

            judgement = judge_answer(task, action.tool_input)
            print(f"Judge score: {judgement.get('score')}/5 - {judgement.get('reasoning')}")

            latency = round(time.time() - start_time, 2)
            cost_usd = round((total_tokens / 1_000_000) * 0.59, 6)

            print(f"Total tokens: {total_tokens} | Latency: {latency}s | Est. cost: ${cost_usd}")

            result = {
                "answer": action.tool_input,
                "retries": retries_count,
                "steps": step,
                "judge_score": judgement.get("score"),
                "judge_reasoning": judgement.get("reasoning"),
                "total_tokens": total_tokens,
                "latency_seconds": latency,
                "cost_usd": cost_usd,
            }
            save_run(task, result)
            return result

        if action.tool.value == "calculator":
            result = calculator(action.tool_input)
        elif action.tool.value == "web_search":
            result = web_search(action.tool_input)
        else:
            result = "ERROR: unknown tool"

        print(f"Observation: {result}")

        messages.append({"role": "assistant", "content": raw_text})
        messages.append({"role": "user", "content": f"Observation: {result}"})

    print(f"\nStopped: reached max steps without finishing. Retries: {retries_count}")
    return {"answer": None, "retries": retries_count, "steps": max_steps}


if __name__ == "__main__":
    run_agent("Who is the current CEO of Anthropic, and what is 12 times 8?")