"""离线单元测试：词汇数据加载、选词逻辑、渲染（不联网、不调用 LLM）。

运行：python -m tests.vocab_test
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src.vocab import data as vdata  # noqa: E402
from src.vocab import render as vrender  # noqa: E402


def _fake_words(n: int) -> list[dict]:
    return [
        {"rank": i + 1, "freq": 1000 - i, "word": f"word{i}",
         "zh": f"释义{i}", "spellings": None, "category": "测试",
         "subcategory": None}
        for i in range(n)
    ]


def test_load_word_list():
    words = vdata.load_word_list()
    assert len(words) == 5530
    assert words[0]["word"] == "the"
    assert {"rank", "freq", "word", "zh", "category"}.issubset(words[0].keys())


def test_pick_words_advances_cursor():
    words = _fake_words(100)
    picked, new_cursor, cycle = vdata.pick_words(words, 0, 15, set())
    assert len(picked) == 15
    assert picked[0]["rank"] == 1
    assert new_cursor == 15
    assert cycle is False


def test_pick_words_skips():
    words = _fake_words(30)
    picked, new_cursor, _ = vdata.pick_words(words, 0, 5, {"word0", "word2"})
    assert [w["word"] for w in picked] == ["word1", "word3", "word4", "word5", "word6"]
    assert new_cursor == 7


def test_pick_words_wraps():
    words = _fake_words(20)
    picked, new_cursor, cycle = vdata.pick_words(words, 15, 10, set())
    assert len(picked) == 10
    assert picked[0]["rank"] == 16
    assert picked[-1]["rank"] == 5
    assert cycle is True
    assert new_cursor == 5


def test_pick_words_all_skipped():
    words = _fake_words(5)
    picked, _, _ = vdata.pick_words(words, 0, 3, {"word0", "word1", "word2", "word3", "word4"})
    assert picked == []


def test_render_day_contains_key_sections():
    word = {"rank": 1, "freq": 100, "word": "abandon", "zh": "抛弃；放弃",
            "spellings": None, "category": "动作行为", "ipa": "/əˈbændən/",
            "defs": [{"pos": "verb", "def": "to give up", "example": "He abandoned it."}],
            "tip": "搭配 abandon oneself to"}
    md = vrender.render_day([word], "2026-08-26", {"progress_note": "进度 1/5530", "summary": "今日建议", "dict_source": "test"})
    assert "每日考研词汇 · 2026-08-26" in md
    assert "abandon" in md
    assert "抛弃" in md
    assert "考点提示" in md
    assert "今日学习建议" in md


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as e:  # noqa: BLE001
                failures += 1
                print(f"FAIL {name}: {e}")
    sys.exit(1 if failures else 0)
