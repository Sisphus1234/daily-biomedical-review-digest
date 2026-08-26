"""词典释义获取：Free Dictionary API（dictionaryapi.dev，Wiktionary 词源）。

提供 IPA 音标、词性、英文定义与例句。带本地缓存与容错，失败时返回 None 由调用方降级处理。
"""

import time
import urllib.parse

import requests

_BASE = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
_SOURCE = "Free Dictionary API (dictionaryapi.dev / Wiktionary)"


def fetch_word(word: str, cache: dict, min_interval: float = 0.3) -> dict | None:
    """获取单个单词的词典信息；命中缓存直接返回，失败返回 None。"""
    key = word.lower()
    if key in cache:
        return cache[key]
    try:
        url = _BASE.format(word=urllib.parse.quote(word))
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        entry = data[0] if isinstance(data, list) and data else None
        if not entry:
            return None
        result = _normalize(entry)
        cache[key] = result
        time.sleep(min_interval)
        return result
    except Exception:  # noqa: BLE001 - 网络/解析失败一律降级
        cache[key] = None
        return None


def _normalize(entry: dict) -> dict:
    ipa = ""
    for ph in entry.get("phonetics", []):
        text = (ph or {}).get("text", "") or ""
        if text:
            ipa = text
            break
    defs: list[dict] = []
    for meaning in entry.get("meanings", []):
        pos = meaning.get("partOfSpeech", "")
        for d in meaning.get("definitions", []):
            defs.append({
                "pos": pos,
                "def": d.get("definition", ""),
                "example": d.get("example", "") or "",
            })
        if len(defs) >= 3:
            break
    return {"ipa": ipa, "defs": defs, "source": _SOURCE}
