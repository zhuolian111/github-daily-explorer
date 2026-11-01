from __future__ import annotations

from github_daily_explorer.literature_sample import render_sample
from github_daily_explorer.mailer import send_digest


plain, html_body = render_sample()
send_digest("Ta 文献训练 · 样例邮件", plain, html_body)
print("Literature sample email sent successfully.")

