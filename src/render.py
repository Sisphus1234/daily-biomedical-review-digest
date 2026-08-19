"""把精读结果渲染为 Markdown 文件并维护索引。"""

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

    doi_line = f"[{doi}](https://doi.org/{urllib.parse.quote(doi)})" if doi else "—"
    pmc_link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    abstract_label = "全文精读" if "全文" in source_label else "摘要精读"

    return f"""# {title_en}

> **每日精读 · {date}** ｜ **类型：{abstract_label}** ｜ 原文来源：{source_label}

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

## 三、中英对照精读表

| 英文原文 | 中文对照 |
| --- | --- |
{btable}

## 四、专业术语表

| 术语 | 中文译名 | 简要解释 |
| --- | --- | --- |
{glossary}

## 五、前沿性与时效性点评

{reading['frontier_assessment']}

## 六、关键词

{', '.join(reading['keywords'])}

---

*本精读由 DeepSeek 自动生成，仅供参考，请以原文为准。*
"""


def _table_cell(value) -> str:
    return str(value or "").replace("\n", " ").replace("|", "\\|").strip()


def write_note(paper: dict, reading: dict, source_label: str) -> pathlib.Path:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    fname = f"{paper['date']}-{paper['pmid']}-{_safe_slug(paper['title'])}.md"
    path = NOTES_DIR / fname
    path.write_text(render_markdown(paper, reading, source_label), encoding="utf-8")
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