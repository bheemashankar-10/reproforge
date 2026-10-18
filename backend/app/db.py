import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

_client = None


def get_collection():
    global _client
    if _client is None:
        _client = MongoClient(os.environ["MONGODB_URI"], serverSelectionTimeoutMS=3000)
    return _client["reproforge"]["history"]


def save_run(kind: str, request: dict, response: dict) -> None:
    """Save one run. Never crash the API if the database is down."""
    try:
        get_collection().insert_one(
            {
                "kind": kind,
                "request": request,
                "response": response,
                "created_at": datetime.now(timezone.utc),
            }
        )
    except Exception as e:
        print(f"History save failed: {e}")


def list_runs(limit: int = 20) -> list[dict]:
    docs = get_collection().find().sort("created_at", -1).limit(limit)
    return [
        {
            "id": str(d["_id"]),
            "kind": d["kind"],
            "request": d["request"],
            "response": d["response"],
            "created_at": d["created_at"].isoformat(),
        }
        for d in docs
    ]