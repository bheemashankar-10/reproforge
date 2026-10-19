from datetime import datetime, timezone

from backend.app import db


def test_list_runs_formats_utc_timestamp_as_iso8601_z(monkeypatch):
    class Cursor:
        def sort(self, field, direction):
            return self

        def limit(self, count):
            return [
                {
                    "_id": "run-id",
                    "kind": "reproduce",
                    "request": {},
                    "response": {},
                    "created_at": datetime(2026, 10, 19, tzinfo=timezone.utc),
                }
            ]

    class Collection:
        def find(self):
            return Cursor()

    monkeypatch.setattr(db, "get_collection", lambda: Collection())

    assert db.list_runs() == [
        {
            "id": "run-id",
            "kind": "reproduce",
            "request": {},
            "response": {},
            "created_at": "2026-10-19T00:00:00Z",
        }
    ]
