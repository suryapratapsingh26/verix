About ![Verix demo](demo.gif)

Verix is a self-correcting, tool-calling AI agent with a built-in evaluation layer. It plans multi-step tasks, executes them with real tools, catches and recovers from its own failures, and automatically grades every run for correctness, cost, and latency.

Installation

Clone the repo and install dependencies:

```
git clone https://github.com/suryapratapsingh26/verix.git
cd verix/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

What is Verix?

Verix is an agent built around a hand-written plan → act → observe loop, with self-correction and evaluation treated as first-class parts of the system rather than an afterthought. It is not built on LangChain or LangGraph — the loop, schema validation, and retry logic are all written directly.

This repository contains:

* A ReAct-style agent loop (Groq / Llama 3.3 70B)
* Two real tools: `web_search` (Tavily) and `calculator` (numexpr)
* Pydantic schema validation on every model decision, with automatic retry on malformed output
* An independent LLM-as-judge evaluation pass, scoring each run 1-5 with written reasoning
* Token, cost, and latency tracking per run
* MongoDB persistence for run history
* A batch eval suite (`eval_suite.py`) that runs a fixed task set and reports pass rate, retry rate, and cost

Quick Start

Prerequisites:

* Python 3.10+
* A Groq API key
* A Tavily API key
* MongoDB (Atlas free tier or local)

Create a `.env` file in `backend/`:

```
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
MONGODB_URI=your_mongodb_connection_string
MONGODB_DB=verix
```

Run a single task:

```
python agent.py
```

Run the full eval suite:

```
python eval_suite.py
```

Eval Results

`eval_suite.py` runs the agent against 5 tasks spanning pure math, pure lookup, and combined multi-step reasoning: 5/5 completed, average judge score 5.00/5, 0 retries, average latency 2.11s, total cost $0.0036 across all 5 runs.

Repository Layout

* `backend/agent.py` - the plan-act-observe loop and self-correction logic
* `backend/evaluator.py` - LLM-as-judge scoring
* `backend/storage.py` - MongoDB persistence
* `backend/schemas.py` - Pydantic models for agent actions and tool results
* `backend/tools.py` - web_search and calculator tool implementations
* `backend/eval_suite.py` - batch evaluation runner across a fixed task set

License

This project is not currently licensed for reuse. All rights reserved.