from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

import yaml

from .collector import Collector
from .github_client import GitHubClient
from .history import HistoryStore
from .mailer import send_digest
from .renderer import render_html, render_plain
from .selector import ModelSelector


LOGGER = logging.getLogger("github_daily_explorer")


def run(*, dry_run: bool, root: Path, today: date | None = None) -> Path:
    day = today or date.today()
    config_path = root / "config" / "topics.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    history = HistoryStore(root / "data" / "history.json")
    LOGGER.info("正在收集近期活跃项目…")
    candidates = Collector(GitHubClient(), history, config).collect(day)
    LOGGER.info("候选短名单：%d 个", len(candidates))
    if not candidates:
        LOGGER.warning("GitHub API 没有返回可用的新项目；今天不发送空日报。")
        return root / "output" / f"digest-{day.isoformat()}.html"
    recommendations = ModelSelector().select(candidates)
    if not recommendations:
        LOGGER.warning("模型认为今天没有质量足够高的项目；今天不发送邮件。")
        return root / "output" / f"digest-{day.isoformat()}.html"
    plain = render_plain(day, recommendations, candidates)
    html_body = render_html(day, recommendations, candidates)
    output = root / "output" / f"digest-{day.isoformat()}.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html_body, encoding="utf-8")
    (output.parent / f"digest-{day.isoformat()}.txt").write_text(plain, encoding="utf-8")
    if dry_run:
        LOGGER.info("dry-run：日报已保存到 %s；未发送邮件，未修改历史。", output)
        return output
    send_digest(f"GitHub Daily Explorer · {day.isoformat()}", plain, html_body)
    # Transaction boundary: only record recommendations after SMTP succeeds.
    repo_lookup = {repo.full_name.lower(): repo for repo in candidates}
    history.append(recommendations, repo_lookup, day)
    LOGGER.info("邮件发送成功，history.json 已更新。")
    return output

