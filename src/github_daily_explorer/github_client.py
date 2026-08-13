from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class GitHubAPIError(RuntimeError):
    pass


class GitHubClient:
    def __init__(self, token: str | None = None, timeout: int = 20) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.timeout = timeout
        self.base_url = "https://api.github.com"

    def _get(self, path: str) -> Any:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "github-daily-explorer/0.1",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(f"{self.base_url}{path}", headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            detail = "rate limit exceeded" if exc.code in {403, 429} else f"HTTP {exc.code}"
            raise GitHubAPIError(f"GitHub API 请求失败: {detail}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise GitHubAPIError("GitHub API 网络连接失败") from exc

    def search_repositories(self, query: str, per_page: int = 10) -> list[dict[str, Any]]:
        params = urllib.parse.urlencode({"q": query, "sort": "updated", "order": "desc", "per_page": per_page})
        payload = self._get(f"/search/repositories?{params}")
        return payload.get("items", [])

    def get_readme(self, full_name: str) -> str:
        owner, repo = full_name.split("/", 1)
        path = f"/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repo)}/readme"
        headers = {
            "Accept": "application/vnd.github.raw+json",
            "User-Agent": "github-daily-explorer/0.1",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(f"{self.base_url}{path}", headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return ""
            raise GitHubAPIError(f"读取 {full_name} README 失败: HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise GitHubAPIError(f"读取 {full_name} README 时网络连接失败") from exc

