import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a task-planning assistant. Given a task, decide ONE action to take.

Respond with ONLY a JSON object, no other text, in exactly this shape:
{"thought": "<your reasoning>", "tool": "<one of web_search|calculator|finish>", "tool_input": "<the input for that tool>"}
"""

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Task: What is 25 times 4?"},
    ],
    temperature=0.2,
)

raw_text = response.choices[0].message.content
print("RAW OUTPUT:")
print(raw_text)

from schemas import AgentAction

action = AgentAction.model_validate_json(raw_text)
print("\nVALIDATED SUCCESSFULLY:")
from tools import calculator

if action.tool.value == "calculator":
    result = calculator(action.tool_input)
    print(f"\nTOOL EXECUTED. Result: {result}")
print(f"Thought: {action.thought}")
print(f"Tool: {action.tool}")
print(f"Tool Input: {action.tool_input}")