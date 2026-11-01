from github_daily_explorer.literature_sample import render_sample


def test_literature_sample_contains_training_structure():
    plain, html = render_sample()
    assert "Abstract" in plain
    assert "问题层面" in plain
    assert "证据层面" in plain
    assert "当前缺口" in plain
    assert "viewport" in html
    assert "正式邮件会基于核对后的论文原文" in html

