from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .models import Recommendation, Repository


class HistoryStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> dict:
        if not self.path.exists():
            return {"recommendations": []}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise ValueError(f"无法读取历史文件 {self.path}") from exc
        if not isinstance(data.get("recommendations"), list):
            raise ValueError("history.json 格式错误: recommendations 必须是数组")
        return data

    def names(self) -> set[str]:
        return {item["full_name"].lower() for item in self.load()["recommendations"]}

    def filter_new(self, repositories: list[Repository]) -> list[Repository]:
        seen = self.names()
        return [repo for repo in repositories if repo.full_name.lower() not in seen]

    def append(self, recommendations: list[Recommendation], repositories: dict[str, Repository], day: date) -> None:
        data = self.load()
        existing = {item["full_name"].lower() for item in data["recommendations"]}
        for rec in recommendations:
            if rec.full_name.lower() in existing:
                continue
            repo = repositories[rec.full_name.lower()]
            data["recommendations"].append({
                "full_name": repo.full_name,
                "url": repo.html_url,
                "category": rec.category,
                "recommendation_date": day.isoformat(),
                "stars": repo.stars,
            })
            existing.add(rec.full_name.lower())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temp.replace(self.path)

