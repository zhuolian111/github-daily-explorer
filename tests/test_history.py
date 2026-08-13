import json
from datetime import date

from github_daily_explorer.history import HistoryStore
from github_daily_explorer.models import Recommendation, Repository


def test_history_deduplicates_and_appends(tmp_path):
    path = tmp_path / "history.json"
    path.write_text(json.dumps({"recommendations": [{"full_name": "a/one"}]}), encoding="utf-8")
    store = HistoryStore(path)
    repos = [Repository("A/One", "https://x/a"), Repository("b/two", "https://x/b", stars=42)]
    assert [repo.full_name for repo in store.filter_new(repos)] == ["b/two"]
    rec = Recommendation("b/two", "fun", "i", "w", "l", "f", "🎮 看个乐子", 8, "best")
    store.append([rec], {"b/two": repos[1]}, date(2026, 8, 14))
    data = store.load()["recommendations"]
    assert len(data) == 2
    assert data[-1]["stars"] == 42
    assert "credentials" not in data[-1]

