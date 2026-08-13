import json
from datetime import date

from github_daily_explorer import app
from github_daily_explorer.models import Recommendation, Repository


def test_dry_run_writes_output_but_does_not_send_or_change_history(tmp_path, monkeypatch):
    (tmp_path / "config").mkdir()
    (tmp_path / "data").mkdir()
    (tmp_path / "config" / "topics.yaml").write_text("categories: {}\n", encoding="utf-8")
    original = '{"recommendations": []}\n'
    (tmp_path / "data" / "history.json").write_text(original, encoding="utf-8")
    repo = Repository("org/tool", "https://github.com/org/tool", stars=10, language="Python", pushed_at="2026-08-14", category="engineering")
    rec = Recommendation("org/tool", "engineering", "intro", "why", "learn", "src/", "⭐ 值得 Star", 8, "best")

    class FakeCollector:
        def __init__(self, *args): pass
        def collect(self, day): return [repo]

    class FakeSelector:
        def select(self, candidates): return [rec]

    monkeypatch.setattr(app, "Collector", FakeCollector)
    monkeypatch.setattr(app, "ModelSelector", FakeSelector)
    monkeypatch.setattr(app, "send_digest", lambda *args: (_ for _ in ()).throw(AssertionError("must not send")))
    output = app.run(dry_run=True, root=tmp_path, today=date(2026, 8, 14))
    assert output.exists()
    assert (tmp_path / "data" / "history.json").read_text(encoding="utf-8") == original


def test_history_changes_only_after_successful_send(tmp_path, monkeypatch):
    (tmp_path / "config").mkdir()
    (tmp_path / "data").mkdir()
    (tmp_path / "config" / "topics.yaml").write_text("categories: {}\n", encoding="utf-8")
    (tmp_path / "data" / "history.json").write_text('{"recommendations": []}\n', encoding="utf-8")
    repo = Repository("org/tool", "https://github.com/org/tool", category="engineering")
    rec = Recommendation("org/tool", "engineering", "i", "w", "l", "src/", "🔍 值得深入", 8, "best")
    class FakeCollector:
        def __init__(self, *args): pass
        def collect(self, day): return [repo]
    class FakeSelector:
        def select(self, candidates): return [rec]
    monkeypatch.setattr(app, "Collector", FakeCollector)
    monkeypatch.setattr(app, "ModelSelector", FakeSelector)
    monkeypatch.setattr(app, "send_digest", lambda *args: (_ for _ in ()).throw(RuntimeError("SMTP failed")))
    try:
        app.run(dry_run=False, root=tmp_path, today=date(2026, 8, 14))
    except RuntimeError:
        pass
    assert json.loads((tmp_path / "data" / "history.json").read_text())["recommendations"] == []

