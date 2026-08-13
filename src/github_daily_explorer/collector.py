from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Any

from .github_client import GitHubClient
from .history import HistoryStore
from .models import Repository


def _quality_hint(repo: Repository) -> float:
    stars = math.log10(repo.stars + 1)
    documentation_hint = 0.3 if repo.description else 0
    license_hint = 0.2 if repo.license != "Unknown" else 0
    discovery_bonus = max(0, 1.8 - math.log10(repo.stars + 10) / 2)
    return stars + documentation_hint + license_hint + discovery_bonus


class Collector:
    def __init__(self, client: GitHubClient, history: HistoryStore, config: dict[str, Any]) -> None:
        self.client = client
        self.history = history
        self.config = config

    def collect(self, today: date) -> list[Repository]:
        lookback = int(self.config.get("lookback_days", 45))
        since = (today - timedelta(days=lookback)).isoformat()
        pool_target = int(self.config.get("candidate_pool_size", 45))
        categories = self.config["categories"]
        per_query = max(5, math.ceil(pool_target / max(1, sum(len(v["queries"]) for v in categories.values()))))
        by_name: dict[str, Repository] = {}
        for category, category_config in categories.items():
            for query in category_config["queries"]:
                full_query = f"({query}) pushed:>={since} archived:false fork:false"
                for item in self.client.search_repositories(full_query, per_page=per_query):
                    key = item["full_name"].lower()
                    candidate = Repository.from_api(item, category)
                    if key not in by_name:
                        by_name[key] = candidate
        fresh = self.history.filter_new(list(by_name.values()))
        fresh.sort(key=_quality_hint, reverse=True)
        shortlist_size = min(int(self.config.get("readme_shortlist_size", 15)), len(fresh))
        shortlist = _balanced_shortlist(fresh, shortlist_size)
        for repo in shortlist:
            repo.readme = self.client.get_readme(repo.full_name)[:8000]
        return shortlist


def _balanced_shortlist(repositories: list[Repository], limit: int) -> list[Repository]:
    if not repositories or limit <= 0:
        return []
    groups = {category: [] for category in ("research", "engineering", "fun")}
    for repo in repositories:
        groups.setdefault(repo.category, []).append(repo)
    result: list[Repository] = []
    while len(result) < limit and any(groups.values()):
        for category in ("research", "engineering", "fun"):
            if groups.get(category) and len(result) < limit:
                result.append(groups[category].pop(0))
    return result

