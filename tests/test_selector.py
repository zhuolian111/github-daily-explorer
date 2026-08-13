import json

import pytest

from github_daily_explorer.models import Repository
from github_daily_explorer.selector import ModelResponseError, ModelSelector, parse_recommendations


def valid_payload(**changes):
    item = {
        "full_name": "org/tool", "category": "engineering", "intro": "简介",
        "why_interesting": "理由", "learning": "学习", "five_minutes": "tests/",
        "verdict": "🔍 值得深入", "match_score": 8, "champion_reason": "今天先看它。",
    }
    item.update(changes)
    return json.dumps({"recommendations": [item]}, ensure_ascii=False)


def test_parse_model_json():
    repos = [Repository("org/tool", "https://github.com/org/tool", category="engineering")]
    parsed = parse_recommendations(f"```json\n{valid_payload()}\n```", repos)
    assert parsed[0].full_name == "org/tool"
    assert parsed[0].match_score == 8


@pytest.mark.parametrize("changes", [
    {"category": "research"},
    {"category": "wrong"},
    {"full_name": "someone/else"},
])
def test_rejects_wrong_category_or_unknown_repo(changes):
    repos = [Repository("org/tool", "https://github.com/org/tool", category="engineering")]
    with pytest.raises((ModelResponseError, ValueError)):
        parse_recommendations(valid_payload(**changes), repos)


def test_rejects_invalid_json():
    with pytest.raises(ModelResponseError):
        parse_recommendations("not json", [])


def test_github_provider_uses_github_token(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "github")
    monkeypatch.setenv("MODEL_NAME", "openai/gpt-4.1")
    monkeypatch.setenv("GITHUB_TOKEN", "github-actions-token")
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    selector = ModelSelector()
    assert selector.api_key == "github-actions-token"
    assert selector.base_url == "https://models.github.ai/inference"
