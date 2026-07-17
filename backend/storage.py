import os
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_client = None
_db = None


def _get_db():
    global _client, _db
    if _db is None:
        uri = os.environ.get("MONGODB_URI")
        db_name = os.environ.get("MONGODB_DB", "verix")
        _client = MongoClient(uri)
        _db = _client[db_name]
    return _db


def save_run(task: str, result: dict):
    """Save a completed agent run to the 'runs' collection."""
    db = _get_db()
    document = {
        "task": task,
        "answer": result.get("answer"),
        "retries": result.get("retries"),
        "steps": result.get("steps"),
        "judge_score": result.get("judge_score"),
        "judge_reasoning": result.get("judge_reasoning"),
        "total_tokens": result.get("total_tokens"),
        "latency_seconds": result.get("latency_seconds"),
        "cost_usd": result.get("cost_usd"),
        "created_at": datetime.now(timezone.utc),
    }
    db.runs.insert_one(document)
    print("Run saved to MongoDB.")


def get_all_runs():
    """Fetch all past runs, most recent first - used by the eval suite summary."""
    db = _get_db()
    return list(db.runs.find().sort("created_at", -1))