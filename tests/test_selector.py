import json

import pytest

from github_daily_explorer.models import Repository
from github_daily_explorer.selector import ModelResponseError, parse_recommendations


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

