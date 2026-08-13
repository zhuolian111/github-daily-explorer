from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


CATEGORIES = {"research", "engineering", "fun"}


@dataclass(slots=True)
class Repository:
    full_name: str
    html_url: str
    description: str = ""
    topics: list[str] = field(default_factory=list)
    stars: int = 0
    forks: int = 0
    language: str = "Unknown"
    created_at: str = ""
    updated_at: str = ""
    pushed_at: str = ""
    license: str = "Unknown"
    category: str = ""
    readme: str = ""

    @classmethod
    def from_api(cls, item: dict[str, Any], category: str) -> "Repository":
        license_info = item.get("license") or {}
        return cls(
            full_name=item["full_name"],
            html_url=item["html_url"],
            description=item.get("description") or "",
            topics=item.get("topics") or [],
            stars=item.get("stargazers_count", 0),
            forks=item.get("forks_count", 0),
            language=item.get("language") or "Unknown",
            created_at=item.get("created_at") or "",
            updated_at=item.get("updated_at") or "",
            pushed_at=item.get("pushed_at") or "",
            license=license_info.get("spdx_id") or "Unknown",
            category=category,
        )

    def prompt_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["readme"] = self.readme[:5000]
        return data


@dataclass(slots=True)
class Recommendation:
    full_name: str
    category: str
    intro: str
    why_interesting: str
    learning: str
    five_minutes: str
    verdict: str
    match_score: int
    champion_reason: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Recommendation":
        required = {
            "full_name", "category", "intro", "why_interesting", "learning",
            "five_minutes", "verdict", "match_score",
        }
        missing = required - data.keys()
        if missing:
            raise ValueError(f"模型结果缺少字段: {', '.join(sorted(missing))}")
        category = str(data["category"])
        if category not in CATEGORIES:
            raise ValueError(f"无效类别: {category}")
        score = int(data["match_score"])
        if not 1 <= score <= 10:
            raise ValueError("match_score 必须在 1 到 10 之间")
        verdict = str(data["verdict"])
        allowed = {"⭐ 值得 Star", "🔍 值得深入", "🎮 看个乐子"}
        if verdict not in allowed:
            raise ValueError(f"无效推荐标签: {verdict}")
        return cls(
            full_name=str(data["full_name"]), category=category,
            intro=str(data["intro"]), why_interesting=str(data["why_interesting"]),
            learning=str(data["learning"]), five_minutes=str(data["five_minutes"]),
            verdict=verdict, match_score=score,
            champion_reason=str(data.get("champion_reason", "")),
        )

