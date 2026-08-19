"""PubMed 数据拉取：NCBI E-utilities + Europe PMC 全文抓取。"""

import re
import time
import urllib.parse
import xml.etree.ElementTree as ET

import requests

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"

REVIEW_TYPES = ("review", "systematic review", "review article", "literature review")


def _get(cfg, url, params, tries=3):
    params = dict(params)
    if cfg["pubmed_email"]:
        params["email"] = cfg["pubmed_email"]
    if cfg["ncbi_api_key"]:
        params["api_key"] = cfg["ncbi_api_key"]
    for attempt in range(tries):
        try:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            if attempt == tries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))


def _parse_date(pubdate: str):
    """把 2026 Aug 19 / 2026 Aug / 2026 解析成 (year, month, day)，解析失败返回最大日期。"""
    try:
        parts = pubdate.replace("  ", " ").split(" ")
        year = int(parts[0])
        month = int({"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                     "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
                    .get(parts[1].lower()[:3], 1)) if len(parts) > 1 else 1
        day = int(parts[2]) if len(parts) > 2 else 1
        return year, month, day
    except (ValueError, IndexError):
        return 9999, 12, 31


def search_latest_reviews(cfg, days: int | None = None) -> list[dict]:
    """查询最近 days 天内发表的 Review 综述，按发表时间倒序，返回 esummary 原始记录列表。"""
    days = days or cfg["lookback_days"]
    term = (
        'review[pt] '
        f'AND ("last {days} days"[dp]) '
        'AND english[la] AND hasabstract[text]'
    )
    resp = _get(cfg, f"{EUTILS}/esearch.fcgi", {
        "db": "pubmed",
        "term": term,
        "retmax": cfg["retmax"],
        "sort": "pub+date",
        "retmode": "json",
    })
    data = resp.json()
    pmids = data.get("esearchresult", {}).get("idlist", [])
    if not pmids:
        return []

    ids = ",".join(pmids)
    resp = _get(cfg, f"{EUTILS}/esummary.fcgi", {
        "db": "pubmed", "id": ids, "retmode": "json",
    })
    result = resp.json().get("result", {})
    records = [result[i] for i in pmids if i in result]
    return [r for r in records if _is_review(r)]


def _is_review(rec: dict) -> bool:
    types = [t.lower() for t in rec.get("pubtype", [])]
    return any(any(rt in t for rt in REVIEW_TYPES) for t in types)


def fetch_abstract(cfg, pmid: str) -> str:
    resp = _get(cfg, f"{EUTILS}/efetch.fcgi", {
        "db": "pubmed", "id": pmid, "rettype": "abstract", "retmode": "text",
    })
    text = resp.text.strip()
    return _strip_abstract_header(text)


def fetch_abstracts(cfg, pmids: list[str]) -> dict[str, str]:
    """批量拉取摘要，返回 {pmid: abstract}。"""
    out: dict[str, str] = {}
    for i in range(0, len(pmids), 50):
        batch = pmids[i:i + 50]
        resp = _get(cfg, f"{EUTILS}/efetch.fcgi", {
            "db": "pubmed", "id": ",".join(batch), "rettype": "abstract", "retmode": "text",
        })
        text = resp.text.strip()
        if not text:
            continue
        chunks = re.split(r"\n\n(?=\d+\. )", text)
        for chunk in chunks:
            if not chunk.strip():
                continue
            m = re.match(r"^(\d+)\.\s+", chunk)
            if m:
                out[m.group(1)] = _strip_abstract_header(chunk)
    return out


def _strip_abstract_header(text: str) -> str:
    """去除 efetch 返回中的标题/作者等头部，只保留 ABSTRACT 之后的部分。"""
    marker = "ABSTRACT"
    idx = text.rfind(marker)
    if idx != -1:
        return text[idx + len(marker):].strip()
    return text


def fetch_pmc_fulltext(cfg, pmid: str) -> str | None:
    """尝试经 Europe PMC 获取开放获取全文正文文本；不可用返回 None。"""
    try:
        resp = requests.get(
            f"{EPMC}/search", params={"query": f"EXT_ID:{pmid}", "format": "json"}, timeout=30
        )
        resp.raise_for_status()
        hits = resp.json().get("resultList", {}).get("result", [])
        if not hits or not hits[0].get("pmcid"):
            return None
        pmcid = hits[0]["pmcid"]
        resp = requests.get(
            f"{EPMC}/{pmcid}/fullTextXML", timeout=60
        )
        if resp.status_code != 200:
            return None
        root = ET.fromstring(resp.content)
        body = root.find(".//body")
        if body is None:
            return None
        sections = []
        for sec in body.iter("sec"):
            heading = sec.findtext("title")
            if heading:
                sections.append(f"[{heading}]")
            for p in sec.findall(".//p"):
                txt = "".join(p.itertext()).strip()
                if txt:
                    sections.append(txt)
        text = "\n".join(sections)
        return text if len(text) > 800 else None
    except (requests.RequestException, ET.ParseError, KeyError):
        return None


def pick_abstract_or_fulltext(cfg, pmid: str) -> tuple[str | None, str | None]:
    """返回 (正文文本, 来源标签)。优先全文，其次摘要。"""
    full = fetch_pmc_fulltext(cfg, pmid)
    if full:
        return full[: cfg["max_text_chars"]], "PMC 开放获取全文"
    abstract = fetch_abstract(cfg, pmid)
    if abstract:
        return abstract[: cfg["max_text_chars"]], "PubMed 摘要"
    return None, None