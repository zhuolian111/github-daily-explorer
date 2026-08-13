from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from collections import Counter

from .models import Recommendation, Repository


class ModelConfigError(ValueError):
    pass


class ModelResponseError(ValueError):
    pass


class ModelSelector:
    DEFAULT_BASES = {
        "openai": "https://api.openai.com/v1",
        "deepseek": "https://api.deepseek.com",
        "github": "https://models.github.ai/inference",
    }

    def __init__(self) -> None:
        self.provider = os.getenv("MODEL_PROVIDER", "openai").lower().strip()
        self.api_key = os.getenv("MODEL_API_KEY", "")
        if self.provider == "github":
            self.api_key = self.api_key or os.getenv("GITHUB_TOKEN", "")
        self.model = os.getenv("MODEL_NAME", "")
        self.base_url = os.getenv("MODEL_BASE_URL", "").rstrip("/") or self.DEFAULT_BASES.get(self.provider, "")
        if self.provider not in self.DEFAULT_BASES:
            raise ModelConfigError("MODEL_PROVIDER 仅支持 openai、deepseek 或 github")
        missing = [name for name, value in (("MODEL_API_KEY", self.api_key), ("MODEL_NAME", self.model)) if not value]
        if missing:
            raise ModelConfigError(f"缺少模型配置: {', '.join(missing)}")

    def select(self, repositories: list[Repository]) -> list[Recommendation]:
        if not repositories:
            return []
        prompt = _build_prompt(repositories)
        body = json.dumps({
            "model": self.model,
            "temperature": 0.55,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        }).encode("utf-8")
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        if self.provider == "github":
            headers.update({
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2026-03-10",
            })
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions", data=body, method="POST", headers=headers,
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                payload = json.load(response)
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"模型 API 请求失败: HTTP {exc.code}（凭据不会显示）") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError("模型 API 网络连接失败") from exc
        try:
            content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ModelResponseError("模型 API 返回格式异常") from exc
        return parse_recommendations(content, repositories)


SYSTEM_PROMPT = """你是一个挑剔的 GitHub 项目侦察员。你要为一位计算材料科研工作者挑项目，但不能只看 star。
重视 relevance、novelty、项目质量、近期活跃、文档、原创性、实用性、学习价值和 discovery value。
降低过度知名项目的权重，保留探索性，避免每天困在 MLIP/LAMMPS/DFT 循环。语言简洁、自然、有判断，不抄 README，不说营销套话。
只返回合法 JSON，不要 Markdown。"""


def _build_prompt(repositories: list[Repository]) -> str:
    schema = {
        "recommendations": [{
            "full_name": "必须原样来自候选",
            "category": "research|engineering|fun",
            "intro": "一句自然中文介绍",
            "why_interesting": "为什么今天挑中",
            "learning": "能学到的具体方法、工程思维或创造力",
            "five_minutes": "5 分钟优先打开的具体位置",
            "verdict": "⭐ 值得 Star|🔍 值得深入|🎮 看个乐子",
            "match_score": 8,
            "champion_reason": "仅今日最推荐填写 2-4 句话，其他为空",
        }]
    }
    candidates = [repo.prompt_dict() for repo in repositories]
    return (
        "从候选中每类最多选 1 个，理想情况恰好 research、engineering、fun 各 1 个。"
        "若某类明显不合格可以不选，绝不凑数。同一 full_name 不得重复，类别必须与候选 category 相同。"
        "全部推荐中恰好一个 champion_reason 非空。match_score 只用整数 1-10，不要伪精确。\n"
        f"输出结构：{json.dumps(schema, ensure_ascii=False)}\n"
        f"候选：{json.dumps(candidates, ensure_ascii=False)}"
    )


def _extract_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ModelResponseError("模型没有返回合法 JSON") from exc
    if not isinstance(value, dict):
        raise ModelResponseError("模型 JSON 顶层必须是对象")
    return value


def parse_recommendations(text: str, repositories: list[Repository]) -> list[Recommendation]:
    payload = _extract_json(text)
    raw = payload.get("recommendations")
    if not isinstance(raw, list):
        raise ModelResponseError("模型 JSON 缺少 recommendations 数组")
    if len(raw) > 3:
        raise ModelResponseError("模型选择超过 3 个项目")
    available = {repo.full_name.lower(): repo for repo in repositories}
    recommendations = [Recommendation.from_dict(item) for item in raw]
    names = [rec.full_name.lower() for rec in recommendations]
    if len(names) != len(set(names)):
        raise ModelResponseError("模型重复选择了同一项目")
    for rec in recommendations:
        repo = available.get(rec.full_name.lower())
        if repo is None:
            raise ModelResponseError(f"模型选择了候选之外的项目: {rec.full_name}")
        if repo.category != rec.category:
            raise ModelResponseError(f"模型修改了 {rec.full_name} 的类别")
    counts = Counter(rec.category for rec in recommendations)
    if any(count > 1 for count in counts.values()):
        raise ModelResponseError("每个类别最多只能选择一个项目")
    champions = sum(bool(rec.champion_reason.strip()) for rec in recommendations)
    if recommendations and champions != 1:
        raise ModelResponseError("必须且只能有一个今日最推荐")
    return recommendations
