from __future__ import annotations

import os
import smtplib
import ssl
from email.message import EmailMessage


class SMTPConfigError(ValueError):
    pass


def _smtp_config() -> dict[str, str | int]:
    values = {
        "host": os.getenv("SMTP_HOST", "smtp.qq.com"),
        "port": os.getenv("SMTP_PORT", "465"),
        "user": os.getenv("SMTP_USER", ""),
        "auth_code": os.getenv("SMTP_AUTH_CODE", ""),
        "to": os.getenv("DIGEST_TO", ""),
    }
    missing = [env for env, key in (("SMTP_USER", "user"), ("SMTP_AUTH_CODE", "auth_code"), ("DIGEST_TO", "to")) if not values[key]]
    if missing:
        raise SMTPConfigError(f"缺少 SMTP 配置: {', '.join(missing)}")
    try:
        values["port"] = int(str(values["port"]))
    except ValueError as exc:
        raise SMTPConfigError("SMTP_PORT 必须是整数") from exc
    return values


def send_digest(subject: str, plain: str, html_body: str) -> None:
    config = _smtp_config()
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = str(config["user"])
    message["To"] = str(config["to"])
    message.set_content(plain)
    message.add_alternative(html_body, subtype="html")
    try:
        with smtplib.SMTP_SSL(str(config["host"]), int(config["port"]), context=ssl.create_default_context(), timeout=30) as smtp:
            smtp.login(str(config["user"]), str(config["auth_code"]))
            smtp.send_message(message)
    except smtplib.SMTPAuthenticationError as exc:
        raise RuntimeError("SMTP 认证失败：请检查邮箱账号和 SMTP 授权码（不是 QQ 登录密码）") from exc
    except (smtplib.SMTPException, OSError) as exc:
        raise RuntimeError("SMTP 发送失败：请检查服务器、端口和网络；凭据不会显示") from exc

