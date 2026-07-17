"""
Batch evaluation runner.

Runs the agent against a fixed set of test tasks and prints an aggregate
summary - average judge score, total cost, retry rate, average steps/latency.
This is the "prove it works reliably, not just once" script.

Usage:
    python eval_suite.py
"""

from agent import run_agent

TEST_TASKS = [
    "What is 47 times 6?",
    "Who is the current CEO of Anthropic?",
    "What is 15% of 240?",
    "Who is the current CEO of Anthropic, and what is 12 times 8?",
    "What is the capital of France, and what is 9 times 9?",
]


def run_eval_suite():
    results = []

    for i, task in enumerate(TEST_TASKS, 1):
        print("\n" + "=" * 60)
        print(f"TEST CASE {i}/{len(TEST_TASKS)}: {task}")
        print("=" * 60)

        result = run_agent(task)
        result["task"] = task
        results.append(result)

    _print_summary(results)


def _print_summary(results: list[dict]):
    print("\n\n" + "=" * 60)
    print("EVAL SUITE SUMMARY")
    print("=" * 60)

    completed = [r for r in results if r.get("answer") is not None]
    scores = [r["judge_score"] for r in completed if r.get("judge_score") is not None]
    total_cost = sum(r.get("cost_usd", 0) or 0 for r in completed)
    total_retries = sum(r.get("retries", 0) or 0 for r in completed)
    avg_steps = sum(r.get("steps", 0) or 0 for r in completed) / len(completed) if completed else 0
    avg_latency = sum(r.get("latency_seconds", 0) or 0 for r in completed) / len(completed) if completed else 0

    print(f"Tasks run: {len(results)}")
    print(f"Completed successfully: {len(completed)}/{len(results)}")
    print(f"Average judge score: {sum(scores)/len(scores):.2f}/5" if scores else "Average judge score: N/A")
    print(f"Total retries across all runs: {total_retries}")
    print(f"Average steps per run: {avg_steps:.1f}")
    print(f"Average latency per run: {avg_latency:.2f}s")
    print(f"Total cost across suite: ${total_cost:.6f}")

    print("\nPer-task breakdown:")
    for r in results:
        status = "OK" if r.get("answer") else "FAILED"
        print(f"  [{status}] score={r.get('judge_score')}/5 | "
              f"steps={r.get('steps')} | retries={r.get('retries')} | "
              f"task=\"{r['task'][:50]}\"")


if __name__ == "__main__":
    run_eval_suite()