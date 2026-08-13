from datetime import date

from github_daily_explorer.models import Recommendation, Repository
from github_daily_explorer.renderer import render_html


def test_html_renderer_escapes_content_and_is_mobile_friendly():
    repo = Repository("org/<tool>", "https://github.com/org/tool?a=1&b=2", stars=123, language="Python", pushed_at="2026-08-13T00:00:00Z", category="fun")
    rec = Recommendation(repo.full_name, "fun", "<script>bad</script>", "why", "learn", "examples/", "🎮 看个乐子", 7, "因为好玩。")
    output = render_html(date(2026, 8, 14), [rec], [repo])
    assert '<meta name="viewport"' in output
    assert "&lt;script&gt;" in output
    assert "<script>bad</script>" not in output
    assert "🏆 今日最推荐" in output

