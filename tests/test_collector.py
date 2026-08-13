from datetime import date

from github_daily_explorer.collector import Collector
from github_daily_explorer.history import HistoryStore


class EmptyClient:
    def search_repositories(self, query, per_page=10):
        return []

    def get_readme(self, full_name):
        raise AssertionError("empty result must not fetch README")


def test_empty_github_results_do_not_crash(tmp_path):
    config = {"categories": {"research": {"queries": ["science"]}}, "readme_shortlist_size": 10}
    result = Collector(EmptyClient(), HistoryStore(tmp_path / "history.json"), config).collect(date(2026, 8, 14))
    assert result == []

