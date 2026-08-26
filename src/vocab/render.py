"""把每日单词渲染为 Markdown 学习卡片并维护 vocab/ 索引。"""

import pathlib
import re

from .data import VOCAB_DIR


def _cell(value) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ").strip()


def render_day(words: list[dict], date: str, meta: dict) -> str:
    """渲染单日 Markdown：词频排名、音标、中英文释义、例句、考点提示。"""
    blocks = ["# 每日考研词汇 · " + date, ""]
    blocks.append(
        f"> 目标：考研英语一/二 + 六级 ｜ 词表：5530 个考研大纲词（按真题词频排序）"
        f" ｜ 今日 {len(words)} 词"
    )
    if meta.get("progress_note"):
        blocks.append("")
        blocks.append(f"> {meta['progress_note']}")
    blocks.extend(["", "---", ""])

    for i, w in enumerate(words, 1):
        ipa = f" /{_cell(w['ipa'])}/" if w.get("ipa") else ""
        freq = w.get("freq", "")
        rank = w.get("rank", "")
        freq_txt = f"词频排名 #{rank} · 真题出现 {freq} 次" if freq else f"词频排名 #{rank}"
        cat = w.get("category", "")
        blocks.append(f"## {i}. {w['word']} {ipa}")
        blocks.append("")
        blocks.append(f"**{freq_txt}** ｜ 分类：{_cell(cat)}")
        blocks.append("")
        if w.get("spellings"):
            blocks.append(f"**其他拼写：** {_cell(w['spellings'])}")
            blocks.append("")
        blocks.append(f"**中文释义：** {_cell(w['zh'])}")
        blocks.append("")

        defs = w.get("defs") or []
        if defs:
            rows = []
            for d in defs[:3]:
                pos = f"*{_cell(d['pos'])}*" if d.get("pos") else ""
                rows.append(f"- {pos} {_cell(d['def'])}")
                if d.get("example"):
                    rows.append(f"  - 例：_{_cell(d['example'])}_")
            blocks.append("**英文释义：**")
            blocks.append("")
            blocks.extend(rows)
            blocks.append("")
        if w.get("tip"):
            blocks.append(f"**考点提示：** {_cell(w['tip'])}")
            blocks.append("")
        blocks.append("---")
        blocks.append("")

    if meta.get("summary"):
        blocks.append("## 今日学习建议")
        blocks.append("")
        blocks.append(meta["summary"])
        blocks.append("")
        blocks.append("---")
        blocks.append("")
    blocks.append("*释义来源：" + meta.get("dict_source", "") + " + DeepSeek 精读，仅供学习参考。*")
    return "\n".join(blocks).rstrip() + "\n"


def write_day(words: list[dict], date: str, meta: dict) -> pathlib.Path:
    VOCAB_DIR.mkdir(parents=True, exist_ok=True)
    path = VOCAB_DIR / f"{date}.md"
    path.write_text(render_day(words, date, meta), encoding="utf-8")
    return path


def update_index() -> None:
    """重建 vocab/README.md 索引（最新在前）。"""
    entries = []
    for p in sorted(VOCAB_DIR.glob("*.md")):
        if p.name == "README.md":
            continue
        date = p.name[:10]
        head = p.read_text(encoding="utf-8").splitlines()
        first_word = ""
        for line in head:
            if line.startswith("## "):
                first_word = line[3:].split("/")[0].strip()
                first_word = re.sub(r"^\d+\.\s*", "", first_word)
                break
        entries.append((date, p.name, first_word))
    entries.sort(key=lambda e: e[0], reverse=True)
    lines = [
        "# 每日考研词汇索引",
        "",
        "每天自动按真题词频生成考研词汇学习卡片（5530 个大纲词，高频优先）。",
        "",
        "| 日期 | 文件 | 首词 |",
        "| --- | --- | --- |",
    ]
    for date, name, word in entries:
        lines.append(f"| {date} | [{name}]({name}) | {word} |")
    (VOCAB_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
