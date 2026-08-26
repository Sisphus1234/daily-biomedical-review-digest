"""把精读结果渲染为 Markdown 文件并维护索引。"""

import datetime
import html
import pathlib
import re
import urllib.parse

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
NOTES_DIR = REPO_ROOT / "notes"
DATA_DIR = REPO_ROOT / "data"
INDEX_PATH = NOTES_DIR / "README.md"


def _safe_slug(text: str, limit: int = 48) -> str:
    slug = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-").lower()
    if len(slug) <= limit:
        return slug or "review"
    cut = slug[:limit]
    if "-" in cut:
        cut = cut.rsplit("-", 1)[0]
    return cut.rstrip("-") or slug[:limit].rstrip("-") or "review"


def _authors_str(raw) -> str:
    if isinstance(raw, list):
        names = [a.get("name", "") for a in raw if isinstance(a, dict)]
        if len(names) > 6:
            return f"{', '.join(names[:3])}, et al. ({len(names)} authors)"
        return ", ".join(names)
    return raw or ""


def _doi_from_articleids(rec: dict) -> str:
    for aid in rec.get("articleids", []):
        if aid.get("idtype") == "doi":
            return aid.get("value", "")
    return ""


def _table_cell(value) -> str:
    return str(value or "").replace("\n", " ").replace("|", "\\|").strip()


def render_markdown(paper: dict, reading: dict, source_label: str) -> str:
    date = paper["date"]
    title_en = paper["title"]
    authors = _authors_str(paper.get("authors", []))
    journal = paper.get("journal", "")
    doi = paper.get("doi", "")
    pmid = paper["pmid"]
    pubdate = paper.get("pubdate", "")

    btable = "\n".join(
        f"| {_table_cell(row.get('en',''))} | {_table_cell(row.get('zh',''))} |"
        for row in reading["bilingual_table"]
    )
    glossary = "\n".join(
        f"| {_table_cell(g.get('term',''))} | {_table_cell(g.get('zh',''))} | {_table_cell(g.get('note',''))} |"
        for g in reading["glossary"]
    )
    key_points = "\n".join(f"{i}. {p}" for i, p in enumerate(reading["key_points"], 1))

    sections = []
    for i, sec in enumerate(reading.get("deep_sections", []), 1):
        block = [f"### {sec.get('title', f'第 {i} 节')}"]
        for row in sec.get("sections_en_zh", []):
            block.append(f"**英文原文：**\n\n> {_table_cell(row.get('en',''))}\n")
            block.append(f"**中文翻译：**\n\n> {_table_cell(row.get('zh',''))}\n")
        block.append(f"> **深度解读：** {_table_cell(sec.get('deep_dive',''))}\n")
        sections.append("\n\n".join(block))
    sections_text = "\n\n".join(sections) if sections else "（无分节深度解读）"

    excerpts = []
    for i, ex in enumerate(reading.get("original_excerpts", []), 1):
        block = [
            f"### 原文摘录 {i}",
            f"**英文原文：**\n\n> {_table_cell(ex.get('en',''))}\n",
            f"**中文翻译：**\n\n> {_table_cell(ex.get('zh',''))}\n",
        ]
        excerpts.append("\n\n".join(block))
    excerpts_text = "\n\n".join(excerpts) if excerpts else "（无原文摘录，当前为摘要精读）"

    doi_line = f"[{doi}](https://doi.org/{urllib.parse.quote(doi)})" if doi else "—"
    pmc_link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    abstract_label = "全文精读" if "全文" in source_label else "摘要精读"

    return f"""# {title_en}

> **每日精读 · {date}** ｜ **类型：{abstract_label}** ｜ 原文来源：{source_label} ｜ 阅读时长：约 10-15 分钟

## 文章信息

| 项目 | 内容 |
| --- | --- |
| 中文标题 | {reading['title_cn']} |
| 期刊 | {_table_cell(journal)} |
| 发表日期 | {_table_cell(pubdate)} |
| 作者 | {_table_cell(authors)} |
| DOI | {doi_line} |
| PMID | [{pmid}]({pmc_link}) |

---

## 一、文章概览

{reading['summary']}

## 二、核心要点

{key_points}

## 三、分节深度解读（10-15 分钟精读）

{sections_text}

## 四、原文精读摘录（学英语/看综述写作）

{excerpts_text}

## 五、中英对照精读表

| 英文原文 | 中文对照 |
| --- | --- |
{btable}

## 六、专业术语表

| 术语 | 中文译名 | 简要解释 |
| --- | --- | --- |
{glossary}

## 七、前沿性与时效性点评

{reading['frontier_assessment']}

## 八、关键词

{', '.join(reading['keywords'])}

---

*本精读由 DeepSeek 自动生成，仅供参考，请以原文为准。*
"""


def write_note(paper: dict, reading: dict, source_label: str) -> pathlib.Path:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    fname = f"{paper['date']}-{paper['pmid']}-{_safe_slug(paper['title'])}.md"
    path = NOTES_DIR / fname
    path.write_text(render_markdown(paper, reading, source_label), encoding="utf-8")
    return path


def cleanup_old_notes(today: datetime.date, keep_days: int = 1) -> int:
    """删除早于保留期限的精读文件，返回删除数量。保留 notes/README.md 索引。"""
    removed = 0
    if keep_days < 0:
        keep_days = 0
    cutoff = today - datetime.timedelta(days=keep_days)
    for p in NOTES_DIR.glob("*.md"):
        if p.name == "README.md":
            continue
        try:
            file_date = datetime.date.fromisoformat(p.name[:10])
        except ValueError:
            continue
        if file_date < cutoff:
            p.unlink(missing_ok=True)
            removed += 1
    return removed


def _md_to_html(md_text: str) -> str:
    """把精读 Markdown 转成简单 HTML（处理标题/引用/粗体/表格/列表/段落）。"""
    out = []
    lines = md_text.splitlines()
    in_table = False
    table_rows = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            out.append(f"<h1>{html.escape(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            out.append(f"<h2>{html.escape(stripped[3:])}</h2>")
        elif stripped.startswith("### "):
            out.append(f"<h3>{html.escape(stripped[4:])}</h3>")
        elif stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if in_table:
                if all(set(c) <= set("-: ") for c in cells):
                    continue
                table_rows.append(cells)
            else:
                in_table = True
                table_rows.append(cells)
        else:
            if in_table:
                out.append("<table><thead><tr>" + "".join(f"<th>{html.escape(c)}</th>" for c in table_rows[0]) + "</tr></thead><tbody>")
                for row in table_rows[1:]:
                    out.append("<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in row) + "</tr>")
                out.append("</tbody></table>")
                in_table = False
                table_rows = []
            if stripped.startswith(">"):
                content = html.escape(stripped.lstrip("> ")).replace("**", "")
                out.append(f"<blockquote>{content}</blockquote>")
            elif stripped:
                out.append(f"<p>{html.escape(stripped)}</p>")
    if in_table:
        out.append("<table><thead><tr>" + "".join(f"<th>{html.escape(c)}</th>" for c in table_rows[0]) + "</tr></thead><tbody>")
        for row in table_rows[1:]:
            out.append("<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in row) + "</tr>")
        out.append("</tbody></table>")
    return "\n".join(out)


def write_index_html(paper: dict, reading: dict, source_label: str) -> pathlib.Path:
    """生成根目录 index.html 作为 Pages 首页，嵌入当天精读全文。"""
    title = html.escape(reading["title_cn"])
    html_body = _md_to_html(render_markdown(paper, reading, source_label))
    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>每日生物医学综述精读 · {paper['date']}</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; max-width: 900px; margin: 0 auto; padding: 24px; line-height: 1.8; color: #1a1a1a; background: #fafafa; }}
  h1 {{ font-size: 1.6em; border-bottom: 2px solid #2c7be5; padding-bottom: 8px; }}
  h2 {{ font-size: 1.3em; color: #2c7be5; margin-top: 32px; border-left: 4px solid #2c7be5; padding-left: 10px; }}
  h3 {{ font-size: 1.1em; margin-top: 24px; }}
  blockquote {{ border-left: 4px solid #d0d7de; margin: 8px 0; padding: 8px 16px; background: #f0f3f6; color: #333; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
  th, td {{ border: 1px solid #d0d7de; padding: 8px; text-align: left; vertical-align: top; font-size: 0.92em; }}
  th {{ background: #f0f3f6; }}
  a {{ color: #2c7be5; }}
  .meta {{ color: #666; font-size: 0.9em; }}
  .footer {{ margin-top: 48px; padding-top: 16px; border-top: 1px solid #e5e7eb; color: #999; font-size: 0.85em; }}
</style>
</head>
<body>
{html_body}
<div class="footer">每日精读自动生成 · 每日 09:15 更新 · 仅供学习参考，请以原文为准</div>
</body>
</html>
"""
    path = REPO_ROOT / "index.html"
    path.write_text(page, encoding="utf-8")
    return path


def update_index() -> None:
    """重建 notes/README.md 索引（最新的在前）。"""
    entries = []
    for p in sorted(NOTES_DIR.glob("*.md")):
        if p.name == "README.md":
            continue
        head = p.read_text(encoding="utf-8").splitlines()
        title = ""
        for line in head[:20]:
            if line.startswith("# "):
                title = line[2:].strip()
                break
        date = p.name[:10]
        entries.append((date, p.name, title))
    entries.sort(reverse=True)
    lines = [
        "# 每日精读索引",
        "",
        "每日自动从 PubMed 精选一篇最新生物医学前沿综述进行精读。",
        "",
        "| 日期 | 文章 | 标题 |",
        "| --- | --- | --- |",
    ]
    for date, name, title in entries:
        lines.append(f"| {date} | [{name}]({name}) | {title} |")
    INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")