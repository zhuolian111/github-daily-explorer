from __future__ import annotations

import html
from datetime import date


TITLE = "Different structural transitions of rapidly supercooled tantalum melt under pressure"
LOCAL_SOURCE = "Ta_reference/淬火文献/不同压强Ta熔化淬火有不同的结构转变.pdf"


def render_sample() -> tuple[str, str]:
    day = date.today().isoformat()
    sections = [
        ("今天要解决的问题", "压力改变 Ta 熔体的淬火路径时，改变的是成核、局部结构竞争，还是晶化动力学？这封样例邮件展示后续正式导读会怎样组织问题。"),
        ("先读哪里", "先读 Abstract 和 Introduction。正式版本会在这里标出作者提出的问题、引用的前人结论，以及文章试图填补的缺口。"),
        ("问题层面", "现象：不同压力下的快速过冷 Ta 熔体可能出现不同的结构演化。核心矛盾：压力究竟稳定了哪类局部结构，以及这种结构变化是否足以解释最终晶化差异？正式导读会逐条对应原文和被引用文献。"),
        ("证据层面", "理论/模拟：需要比较不同压力、冷却路径和结构判据下的结果。重点不是罗列图，而是说明每个物理量为什么被测量、它支持了哪个结论，以及模拟势函数、体系尺寸和冷却速率可能带来的影响。"),
        ("当前缺口", "需要把压力效应拆成可检验的问题：局部配位与中程有序如何变化？成核事件是否在不同压力下改变？结构转变发生在冷却过程的哪个温度区间？"),
        ("今日阅读任务", "读完 Abstract 和 Introduction 后，请回答：1）作者真正要解释的现象是什么？2）作者引用了哪些彼此不一致的结果？3）如果你要复现这项工作，最先检查哪个结构指标？"),
    ]
    plain_lines = [f"Ta 文献训练 · 样例 · {day}", "主题：Ta 的淬火过程受压力影响", "", f"论文：{TITLE}", f"本地来源：{LOCAL_SOURCE}", "", "说明：这是一封格式样例，正文中的表述用于展示邮件结构，正式版本会基于核对后的论文原文和引用文献。", ""]
    for heading, body in sections:
        plain_lines.extend([heading, body, ""])
    plain_lines.extend(["阅读顺序：Abstract → Introduction → 指定图/结果 → 3 个阅读问题", "Generated automatically by Ta Literature Reader"])
    plain = "\n".join(plain_lines)
    cards = "".join(f'<section class="card"><h2>{html.escape(heading)}</h2><p>{html.escape(body)}</p></section>' for heading, body in sections)
    html_body = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Ta 文献训练 · 样例</title><style>
body{{margin:0;background:#f5f6f8;color:#202124;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.7}}.wrap{{max-width:680px;margin:auto;padding:18px 14px}}header{{padding:12px 4px 8px}}h1{{font-size:25px;margin:0 0 4px}}.subtitle{{color:#5f6368;margin:0}}.notice{{background:#fff8e1;border:1px solid #f0c36d;border-radius:10px;padding:12px 14px;margin:14px 0;font-size:13px}}.paper{{background:#eef4ff;border-left:4px solid #2f6feb;padding:14px;margin:14px 0}}.paper strong{{display:block;margin-bottom:5px}}.card{{background:#fff;border:1px solid #dadce0;border-radius:11px;padding:17px;margin:13px 0;box-shadow:0 2px 8px rgba(60,64,67,.06)}}h2{{font-size:17px;margin:0 0 7px;color:#303134}}p{{margin:0}}footer{{text-align:center;color:#777;font-size:12px;padding:16px}}@media(max-width:480px){{.wrap{{padding:10px 9px}}.card{{padding:14px}}}}</style></head><body><main class="wrap"><header><h1>Ta 文献训练</h1><p class="subtitle">样例：每天一篇，先读摘要和 Introduction</p></header><div class="notice">这是一封格式样例。正文中的科学表述用于展示组织方式，正式邮件会基于核对后的论文原文和引用文献。</div><div class="paper"><strong>{html.escape(TITLE)}</strong><span>本地来源：{html.escape(LOCAL_SOURCE)}</span></div>{cards}<footer>Generated automatically by Ta Literature Reader</footer></main></body></html>"""
    return plain, html_body

