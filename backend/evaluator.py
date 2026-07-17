import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

JUDGE_SYSTEM_PROMPT = """You are an impartial evaluator. You will be given a TASK and an ANSWER
that another AI produced for that task. Judge ONLY whether the answer is correct and complete -
you were not involved in producing it and have no context on how it was derived.

Respond with ONLY a JSON object in exactly this shape:
{"score": <integer 1-5, where 5 = fully correct and complete, 1 = wrong or missing>, "reasoning": "<one sentence explaining the score>"}
"""


def judge_answer(task: str, answer: str) -> dict:
    """Grade a completed agent run. Returns {"score": int, "reasoning": str}."""
    if not answer:
        return {"score": 1, "reasoning": "Agent did not produce an answer."}

    response = _client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": f"TASK: {task}\n\nANSWER: {answer}"},
        ],
        temperature=0,
    )
    raw = response.choices[0].message.content

    try:
        return json.loads(raw)
    except Exception as e:
        return {"score": None, "reasoning": f"Judge output could not be parsed: {e}"}