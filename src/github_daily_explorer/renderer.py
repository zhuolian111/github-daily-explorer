from __future__ import annotations

import html
from datetime import date

from .models import Recommendation, Repository


LABELS = {"research": "🧪 科研探索", "engineering": "🛠️ 工程成长", "fun": "🎮 今日整活"}


def _repo_map(repositories: list[Repository]) -> dict[str, Repository]:
    return {repo.full_name.lower(): repo for repo in repositories}


def render_plain(day: date, recommendations: list[Recommendation], repositories: list[Repository]) -> str:
    lookup = _repo_map(repositories)
    lines = [f"GitHub Daily Explorer · {day.isoformat()}", f"今天发现 {len(recommendations)} 个值得打开的项目。", ""]
    for rec in recommendations:
        repo = lookup[rec.full_name.lower()]
        lines.extend([
            LABELS[rec.category], repo.full_name, repo.html_url,
            f"⭐ {repo.stars:,} · {repo.language} · 最近活跃 {repo.pushed_at[:10] or '未知'}",
            f"它是干什么的：{rec.intro}", f"为什么有意思：{rec.why_interesting}",
            f"我能学到什么：{rec.learning}", f"如果只有 5 分钟：{rec.five_minutes}",
            f"{rec.verdict} · 匹配度 {rec.match_score}/10", "",
        ])
    champion = next((rec for rec in recommendations if rec.champion_reason.strip()), None)
    if champion:
        lines.extend(["🏆 今日最推荐", f"{champion.full_name}：{champion.champion_reason}", ""])
    lines.append("Generated automatically by GitHub Daily Explorer")
    return "\n".join(lines)


def render_html(day: date, recommendations: list[Recommendation], repositories: list[Repository]) -> str:
    lookup = _repo_map(repositories)
    cards = []
    for rec in recommendations:
        repo = lookup[rec.full_name.lower()]
        e = html.escape
        cards.append(f"""
        <section class="card">
          <div class="category">{e(LABELS[rec.category])}</div>
          <h2><a href="{e(repo.html_url, quote=True)}">{e(repo.full_name)}</a></h2>
          <div class="meta">⭐ {repo.stars:,} &nbsp;·&nbsp; {e(repo.language)} &nbsp;·&nbsp; 最近活跃 {e(repo.pushed_at[:10] or '未知')}</div>
          <h3>一句话介绍</h3><p>{e(rec.intro)}</p>
          <h3>为什么有意思</h3><p>{e(rec.why_interesting)}</p>
          <h3>我能学到什么</h3><p>{e(rec.learning)}</p>
          <h3>如果只有 5 分钟</h3><p>{e(rec.five_minutes)}</p>
          <div class="score"><span>{e(rec.verdict)}</span><span>匹配度 {rec.match_score}/10</span></div>
        </section>""")
    champion = next((rec for rec in recommendations if rec.champion_reason.strip()), None)
    champion_html = ""
    if champion:
        champion_html = f"""<section class="champion"><h2>🏆 今日最推荐</h2>
        <p><strong>{html.escape(champion.full_name)}</strong>：{html.escape(champion.champion_reason)}</p></section>"""
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GitHub Daily Explorer · {day.isoformat()}</title>
<style>
body{{margin:0;background:#f4f6f8;color:#24292f;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.65}}
.wrap{{max-width:680px;margin:auto;padding:24px 14px}}header{{padding:18px 4px 10px}}h1{{font-size:26px;margin:0}}header p{{color:#57606a;margin:4px 0}}
.card,.champion{{background:#fff;border:1px solid #d8dee4;border-radius:12px;padding:20px;margin:16px 0;box-shadow:0 2px 7px rgba(31,35,40,.05)}}
.category{{font-size:14px;font-weight:700;color:#57606a}}h2{{font-size:21px;margin:4px 0 6px;overflow-wrap:anywhere}}h2 a{{color:#0969da;text-decoration:none}}
.meta{{font-size:13px;color:#57606a;border-bottom:1px solid #eaeef2;padding-bottom:12px}}h3{{font-size:14px;margin:15px 0 2px}}p{{margin:0}}
.score{{display:flex;justify-content:space-between;gap:12px;margin-top:16px;padding-top:12px;border-top:1px solid #eaeef2;font-weight:650}}
.champion{{border-color:#d4a72c;background:#fffbea}}footer{{text-align:center;color:#6e7781;font-size:12px;padding:16px}}
@media(max-width:480px){{.wrap{{padding:12px 9px}}.card,.champion{{padding:16px;border-radius:9px}}.score{{align-items:flex-start;flex-direction:column;gap:3px}}}}
</style></head><body><main class="wrap"><header><h1>GitHub Daily Explorer</h1>
<p>今天发现 {len(recommendations)} 个值得打开的项目。</p></header>{''.join(cards)}{champion_html}
<footer>Generated automatically by GitHub Daily Explorer</footer></main></body></html>"""

