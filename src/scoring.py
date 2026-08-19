"""论文打分与选择：在候选综述中选出"最前沿 + 最新"的一篇。"""

import datetime
import json
import pathlib
import re

TIER1_JOURNALS = (
    "nature reviews", "nature medicine", "nature", "science", "cell", "nejm",
    "new england journal of medicine", "the lancet", "lancet ", "jama",
    "immunity", "science translational medicine", "nature biotechnology",
    "nature genetics", "nature immunology", "nature cancer", "nature oncology",
    "cancer discovery", "bmj", "cell research", "nature reviews drug discovery",
)
TIER2_JOURNALS = (
    "nature communications", "cell reports", "pnas", "elife",
    "trends in ", "annual review of ", "signal transduction and targeted therapy",
    "molecular cancer", "cancer cell", "journal of clinical investigation",
    "plos medicine", "nature metabolism", "nature microbiology", "nature cell biology",
)

FRONTIER_KEYWORDS = (
    "crispr", "car-t", "single-cell", "spatial", "ai", "artificial intelligence",
    "machine learning", "deep learning", "foundation model", "large language model",
    "gene therapy", "mrna", "immunotherapy", "cancer", "tumor", "tumour",
    "long covid", "aging", "senescen", "microbiome", "epigenom", "proteom",
    "organoid", "3d bioprinting", "nanomedicine", "vaccine", "autoimmune",
    "precision medicine", "omics", "multi-omic", "gene editing", "base editing",
    "prime editing", "biomarker", "drug discovery", "protein design", "alpha",
    "synthetic biology", "biosensor", "exosome", "antibody",
)

EXCLUDE_JOURNALS = (
    "cognitive sciences", "cognitive", "psycholog", "behavioral and brain",
    "philosophy", "mathematics", "pure and applied", "physical review",
    "theoretical computer science", "computer vision", "neural networks",
    "plant", "botan", "crop", "agricultur", "agronom", "forest",
    "animal", "veterinary", "zoolog", "entomolog", "insect",
    "phyto", "food science", "nutrition research", "marine", "aquacultur",
)

BIOMEDICAL_KEYWORDS = (
    "disease", "patient", "clinical", "cancer", "tumor", "tumour", "tumorigen",
    "therapy", "therapeutic", "drug", "immune", "vaccine", "antibody",
    "gene", "genome", "genetic", "genomic", "mutation", "protein", "enzyme",
    "cell", "cellular", "molecular", "biomarker", "metabolic", "metabolism",
    "microbiome", "bacteria", "virus", "pathogen", "infection", "inflammat",
    "organ", "tissue", "neuron", "neural", "brain", "cardiac", "heart",
    "lung", "liver", "kidney", "skeletal", "muscle", "hormone", "endocrine",
    "neurodegenerative", "cardiovascular", "oncology", "hematolog", "immunolog",
    "pharmacolog", "toxicolog", "epidemiolog", "biomedical", "physiolog",
    "biochem", "bioengineering", "biotech", "mrna", "crispr", "rna", "dna",
    "epigenom", "proteom", "metabolom", "nanomedicine", "organoid", "stem cell",
    "drug discovery", "precision medicine", "clinical trial",
)


PLANT_EXCLUDE_WORDS = (
    "plant", "plants", "botan", "crop", "crops", "agricultur", "agronom",
    "photosynth", "chloroplast", "arabidopsis", "rice plant", "wheat",
    "maize", "soybean", "tomato", "potato", "seed", "grain", "cereal",
    "horticultur", "greenhouse", "vegetable", "fruit tree", "tobacco",
    "cannabis", "phytoremediat", "allelopath", "phytopatholog", "plantae",
)


def is_biomedical(title: str, abstract: str, journal: str) -> bool:
    """标题+摘要需命中生物医学关键词，且期刊/内容不涉及植物/农业/动物。"""
    j = (journal or "").lower()
    if any(x in j for x in EXCLUDE_JOURNALS):
        return False
    text = f"{title} {abstract}".lower()
    if any(x in text for x in PLANT_EXCLUDE_WORDS):
        return False
    return any(kw in text for kw in BIOMEDICAL_KEYWORDS)


def load_seen(data_dir: pathlib.Path) -> set:
    path = data_dir / "seen.json"
    if not path.exists():
        return set()
    try:
        return set(json.loads(path.read_text(encoding="utf-8")).get("pmids", []))
    except (json.JSONDecodeError, OSError):
        return set()


def save_seen(data_dir: pathlib.Path, pmids: set) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "seen.json").write_text(
        json.dumps({"pmids": sorted(pmids)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _days_ago(pubdate: str, today: datetime.date) -> int | None:
    try:
        parts = pubdate.replace("  ", " ").split(" ")
        year = int(parts[0])
        months = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                  "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
        month = months.get(parts[1].lower()[:3], 1) if len(parts) > 1 else 1
        day = int(parts[2]) if len(parts) > 2 else 1
        d = datetime.date(year, month, day)
        return (today - d).days
    except (ValueError, IndexError):
        return None


def _journal_score(journal: str) -> int:
    j = (journal or "").lower()
    if any(t in j for t in TIER1_JOURNALS):
        return 60
    if any(t in j for t in TIER2_JOURNALS):
        return 35
    return 0


def _keyword_score(title: str, abstract_hint: str = "") -> int:
    text = f"{title} {abstract_hint}".lower()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    score = 0
    for kw in FRONTIER_KEYWORDS:
        if kw in text:
            score += 5
    return min(score, 40)


def score_records(records: list[dict], seen: set, today: datetime.date) -> list[dict]:
    scored = []
    for rec in records:
        pmid = str(rec.get("uid"))
        if pmid in seen:
            continue
        pubdate = rec.get("sortpubdate") or rec.get("pubdate") or ""
        days = _days_ago(pubdate, today)
        recency = 100 if days is None else max(0, 100 - days * 15)
        journal = rec.get("fulljournalname", "")
        title = rec.get("title", "")
        score = recency + _journal_score(journal) + _keyword_score(title)
        scored.append({
            "pmid": pmid,
            "title": title,
            "journal": journal,
            "pubdate": pubdate,
            "score": score,
            "recency_days": days,
        })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def select_best(
    records: list[dict],
    seen: set,
    today: datetime.date,
    abstracts: dict[str, str],
) -> dict | None:
    """按得分从高到低，挑出第一篇通过生物医学门控且可获取文本的论文。"""
    for cand in score_records(records, seen, today):
        rec = next(r for r in records if str(r.get("uid")) == cand["pmid"])
        title = cand["title"]
        journal = cand["journal"]
        abstract = abstracts.get(cand["pmid"], "")
        if is_biomedical(title, abstract, journal):
            return cand
    return None