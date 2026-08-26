"""把每日单词渲染为手机友好的自包含 HTML 页面（vocab.html，覆盖式更新）。"""

import html
import pathlib

from .data import REPO_ROOT


def _card(index: int, word: dict) -> str:
    defs = word.get("defs") or []
    rows = []
    for d in defs[:3]:
        pos = html.escape(d.get("pos") or "")
        definition = html.escape(d.get("def") or "")
        example = html.escape(d.get("example") or "")
        pos_txt = f"<span class='pos'>{pos}</span>" if pos else ""
        ex_txt = f"<span class='ex'>例：{example}</span>" if example else ""
        rows.append(f"<li>{pos_txt}{definition}{ex_txt}</li>")
    defs_txt = (
        f"<h3>英文释义</h3><ul class='defs'>{''.join(rows)}</ul>"
        if rows else ""
    )
    tip = word.get("tip") or ""
    tip_txt = f"<div class='tip'><b>考点提示</b>{html.escape(tip)}</div>" if tip else ""
    freq = word.get("freq") or ""
    rank = word.get("rank") or ""
    freq_txt = (
        f"<div class='freq'>词频排名 #{html.escape(str(rank))} · 真题出现 {html.escape(str(freq))} 次</div>"
        if freq else ""
    )
    ipa = word.get("ipa") or ""
    ipa_txt = f"<span class='ipa'>/{html.escape(ipa)}/</span>" if ipa else ""
    return f"""
    <section class='card'>
      <div class='card-head'>
        <span class='num'>{index}</span>
        <h2 class='word'>{html.escape(str(word.get('word') or ''))} {ipa_txt}</h2>
      </div>
      {freq_txt}
      <p class='zh'>{html.escape(str(word.get('zh') or ''))}</p>
      {defs_txt}
      {tip_txt}
    </section>"""


def _page_body(words: list[dict], date: str, meta: dict) -> str:
    cards = "".join(_card(i, w) for i, w in enumerate(words, 1))
    progress_note = html.escape(meta.get("progress_note") or "")
    progress_txt = f"<p class='note'>{progress_note}</p>" if progress_note else ""
    summary = html.escape(meta.get("summary") or "")
    summary_txt = (
        f"<h2 class='advice-title'>今日学习建议</h2><div class='advice'>{summary}</div>"
        if summary else ""
    )
    dict_source = html.escape(meta.get("dict_source") or "")
    source_txt = (
        f"<p class='source'>释义来源：{dict_source} + DeepSeek 精读，仅供学习参考。</p>"
    )
    return f"""<h1 class='title'>每日考研词汇 · {html.escape(date)}</h1>
{progress_txt}
{cards}
{summary_txt}
{source_txt}"""


def write_day_html(words: list[dict], date: str, meta: dict) -> pathlib.Path:
    """把今日单词渲染为手机优先的自包含 HTML，写入 REPO_ROOT/vocab.html（覆盖式）。"""
    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>每日考研词汇 · {html.escape(date)}</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; max-width: 640px; margin: 0 auto; padding: 16px; line-height: 1.7; font-size: 17px; color: #1f2328; background: #fafafa; }}
  h1.title {{ font-size: 1.35em; text-align: center; margin: 8px 0 12px; }}
  p.note {{ color: #57606a; font-size: 0.9em; background: #eef2f7; border-radius: 8px; padding: 10px 14px; }}
  .card {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 14px 16px; margin: 14px 0; box-shadow: 0 1px 3px rgba(0,0,0,.05); }}
  .card-head {{ display: flex; align-items: baseline; gap: 10px; }}
  .num {{ flex: none; width: 30px; height: 30px; line-height: 30px; text-align: center; border-radius: 50%; background: #2c7be5; color: #fff; font-size: 0.85em; font-weight: 600; }}
  .word {{ margin: 0; font-size: 1.35em; color: #111; }}
  .ipa {{ color: #6e7781; font-weight: 400; font-size: 0.85em; }}
  .freq {{ color: #6e7781; font-size: 0.85em; margin: 4px 0 6px; }}
  .zh {{ font-size: 1.05em; font-weight: 500; margin: 4px 0; }}
  h3 {{ font-size: 0.95em; color: #2c7be5; margin: 10px 0 4px; }}
  ul.defs {{ list-style: none; padding: 0; margin: 0; }}
  ul.defs li {{ padding: 6px 10px; border-left: 3px solid #d0d7de; background: #f6f8fa; border-radius: 0 6px 6px 0; margin: 6px 0; }}
  .pos {{ display: inline-block; color: #2c7be5; font-weight: 600; margin-right: 6px; }}
  .ex {{ display: block; color: #57606a; font-size: 0.9em; margin-top: 2px; }}
  .tip {{ margin-top: 10px; padding: 8px 12px; background: #fff8e6; border-left: 3px solid #e3a008; border-radius: 0 6px 6px 0; font-size: 0.95em; }}
  .tip b {{ color: #9a6700; margin-right: 6px; }}
  h2.advice-title {{ font-size: 1.1em; margin: 24px 0 8px; color: #2c7be5; border-left: 4px solid #2c7be5; padding-left: 10px; }}
  .advice {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 14px 16px; white-space: pre-wrap; }}
  .source {{ color: #8b949e; font-size: 0.85em; text-align: center; margin-top: 28px; }}
</style>
</head>
<body>
{_page_body(words, date, meta)}
</body>
</html>
"""
    path = REPO_ROOT / "vocab.html"
    path.write_text(page, encoding="utf-8")
    return path