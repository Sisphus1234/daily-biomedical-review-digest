"""DeepSeek 精读：把一篇综述生成中文概要、核心要点、中英对照精读表与术语表。"""

import json
import pathlib
import re

import requests

PROMPT_PATH = pathlib.Path(__file__).resolve().parent.parent / "prompts" / "deep_reader.txt"

REQUIRED_FIELDS = (
    "title_cn", "summary", "key_points", "deep_sections",
    "bilingual_table", "glossary", "frontier_assessment", "keywords",
)


def _read_prompt() -> str:
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8")
    return _DEFAULT_PROMPT


_DEFAULT_PROMPT = """你是资深生物医学编辑与中英医学翻译专家。请对给定的一篇前沿综述做高质量中文精读，并生成中英对照阅读材料。

要求：
1. 严格基于给定原文，不编造不存在的结论。
2. 译文专业、准确、通顺，术语保留英文并给出中文译名。
3. 中英对照表按原文行文顺序，选取每部分最有代表性的 8-15 条片段。
4. 术语表覆盖文中出现的重要专业术语，10-20 条。

只输出一个 JSON 对象，不要输出任何其他文字。JSON 结构如下：
{
  "title_cn": "中文译名",
  "summary": "中文概要，500-800字，覆盖研究背景、核心内容、主要结论",
  "key_points": ["要点1", "要点2", ...],
  "bilingual_table": [{"en": "英文原文片段", "zh": "中文翻译"}],
  "glossary": [{"term": "术语英文名", "zh": "中文译名", "note": "一句话专业解释"}],
  "frontier_assessment": "前沿性与时效性点评，150-300字：为何重要、处于什么发展阶段、局限与展望",
  "keywords": ["英文关键词"]
}
"""


def call_deepseek(cfg: dict, system_prompt: str, user_prompt: str) -> str:
    resp = requests.post(
        f"{cfg['deepseek_base_url']}/chat/completions",
        headers={
            "Authorization": f"Bearer {cfg['deepseek_api_key']}",
            "Content-Type": "application/json",
        },
        json={
            "model": cfg["deepseek_model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": cfg["temperature"],
            "response_format": {"type": "json_object"},
            "max_tokens": 6000,
        },
        timeout=180,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        text = text[start:end + 1]
    return json.loads(text)


def deep_read(cfg: dict, paper: dict, source_text: str, source_label: str) -> dict:
    system_prompt = _read_prompt()
    meta = {
        "title": paper["title"],
        "journal": paper["journal"],
        "pubdate": paper["pubdate"],
        "authors": paper.get("authors", ""),
        "doi": paper.get("doi", ""),
        "pmid": paper["pmid"],
        "source_label": source_label,
    }
    user_prompt = (
        "论文信息：\n"
        + json.dumps(meta, ensure_ascii=False, indent=2)
        + "\n\n原文：\n" + source_text
    )
    content = call_deepseek(cfg, system_prompt, user_prompt)
    data = _extract_json(content)
    for field in REQUIRED_FIELDS:
        if field not in data:
            raise ValueError(f"DeepSeek 输出缺少字段: {field}")
    return data