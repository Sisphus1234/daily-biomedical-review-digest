"""数据层：加载考研词频表、管理每日进度与词典缓存。

词表来源：https://github.com/exam-data/NETEMVocabulary（CC BY-NC-SA 4.0）
5530 个考研大纲词按词频降序排列，前 2444 个为高频词（出现 40 次以上）。
"""

import datetime
import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "data"
VOCAB_DIR = REPO_ROOT / "vocab"
LIST_PATH = DATA_DIR / "netem_full_list.json"
PROGRESS_PATH = DATA_DIR / "vocab_progress.json"
CACHE_PATH = DATA_DIR / "vocab_dict_cache.json"

_FIELD_MAP = {
    "序号": "rank",
    "词频": "freq",
    "单词": "word",
    "释义": "zh",
    "其他拼写": "spellings",
    "分类": "category",
    "子分类": "subcategory",
}


def load_word_list() -> list[dict]:
    """加载词频表，返回按词频降序的内部结构列表。"""
    raw = json.loads(LIST_PATH.read_text(encoding="utf-8"))
    entries = list(raw.values())[0]
    words = []
    for e in entries:
        item = {en: e.get(cn) for cn, en in _FIELD_MAP.items()}
        item["zh"] = item["zh"] or ""
        words.append(item)
    return words


def _default_progress(start: int = 0) -> dict:
    return {
        "cursor": start,
        "start_date": datetime.date.today().isoformat(),
        "last_date": None,
        "total_generated": 0,
        "cycles": 0,
    }


def load_progress() -> dict:
    if PROGRESS_PATH.exists():
        try:
            return json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return _default_progress()


def save_progress(progress: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROGRESS_PATH.write_text(
        json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_cache(cache: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def pick_words(words: list[dict], cursor: int, per_day: int, skip: set[str]) -> tuple[list[dict], int, bool]:
    """从 cursor 起取 per_day 个词（跳过 skip 集合中的单词）。

    返回 (选中词列表, 新 cursor, 是否发生回绕)。到达表尾自动回绕继续选。
    """
    n = len(words)
    picked: list[dict] = []
    i = cursor
    cycle = False
    steps = 0
    while len(picked) < per_day and steps < n + per_day:
        w = words[i % n]
        if w["word"].lower() not in skip:
            picked.append(w)
        i += 1
        steps += 1
        if i % n == 0:
            cycle = True
            if not picked:
                break
    return picked, i % n, cycle
