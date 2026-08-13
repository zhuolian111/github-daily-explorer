import pytest

from github_daily_explorer.mailer import SMTPConfigError, _smtp_config


def test_missing_smtp_config_has_safe_error(monkeypatch):
    for key in ("SMTP_USER", "SMTP_AUTH_CODE", "DIGEST_TO"):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(SMTPConfigError) as error:
        _smtp_config()
    assert "SMTP_AUTH_CODE" in str(error.value)
    assert "password" not in str(error.value).lower()

