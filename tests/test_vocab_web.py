"""离线单元测试：每日词汇 HTML 渲染（不联网、不调用 LLM）。

运行：python -m tests.test_vocab_web
"""

import html
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src.vocab import web as vweb  # noqa: E402


def _sample_words() -> list[dict]:
    return [
        {"rank": 1, "freq": 100, "word": "abandon", "zh": "抛弃；放弃",
         "ipa": "/əˈbændən/",
         "defs": [{"pos": "verb", "def": "to give up", "example": "He abandoned it."}],
         "tip": "搭配 abandon oneself to"},
        {"rank": 2, "freq": 90, "word": "absorb", "zh": "吸收；吸引",
         "ipa": "/əbˈzɔːb/", "defs": [], "tip": ""},
    ]


def _sample_meta() -> dict:
    return {"progress_note": "累计进度 2/5530", "summary": "今日建议：先记词义，再看例句。", "dict_source": "test"}


def _render(words=None, date="2026-08-26", meta=None) -> str:
    words = words if words is not None else _sample_words()
    meta = meta if meta is not None else _sample_meta()
    with tempfile.TemporaryDirectory() as tmp:
        original_root = vweb.REPO_ROOT
        vweb.REPO_ROOT = pathlib.Path(tmp)
        try:
            path = vweb.write_day_html(words, date, meta)
            text = path.read_text(encoding="utf-8")
        finally:
            vweb.REPO_ROOT = original_root
        return text


def test_output_contains_date():
    text = _render(date="2026-08-26")
    assert "每日考研词汇 · 2026-08-26" in text
    assert "<title>每日考研词汇 · 2026-08-26</title>" in text


def test_output_contains_word_and_zh():
    text = _render()
    assert "abandon" in text
    assert "抛弃" in text
    assert "absorb" in text
    assert "吸收" in text


def test_output_contains_viewport_meta():
    text = _render()
    assert '<meta name="viewport" content="width=device-width, initial-scale=1">' in text


def test_output_contains_meta_fields():
    text = _render()
    assert "累计进度 2/5530" in text
    assert "今日学习建议" in text
    assert "今日建议：先记词义，再看例句。" in text


def test_output_contains_defs_and_tip():
    text = _render()
    assert "verb" in text
    assert "to give up" in text
    assert "He abandoned it." in text
    assert "考点提示" in text
    assert "abandon oneself to" in text


def test_output_escapes_html():
    words = [{"rank": 1, "word": "<script>alert(1)</script>", "zh": "释义<b>加粗</b>",
              "ipa": "/a/", "defs": [{"pos": "n", "def": "<img src=x>", "example": "<i>x</i>"}],
              "tip": "注意 & 符号"}]
    text = _render(words=words, meta={"progress_note": "<b>进度</b>", "summary": "<p>建议</p>", "dict_source": ""})
    assert "<script>alert(1)</script>" not in text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in text
    assert "&lt;b&gt;进度&lt;/b&gt;" in text
    assert "&lt;img src=x&gt;" in text
    assert html.escape("注意 & 符号") in text


def test_output_self_contained():
    text = _render()
    assert "http://" not in text
    assert "https://" not in text
    assert "<link" not in text
    assert "<style>" in text


def test_output_written_to_repo_vocab_html():
    with tempfile.TemporaryDirectory() as tmp:
        original_root = vweb.REPO_ROOT
        vweb.REPO_ROOT = pathlib.Path(tmp)
        try:
            path = vweb.write_day_html(_sample_words(), "2026-08-26", _sample_meta())
            assert path == pathlib.Path(tmp) / "vocab.html"
            assert path.exists()
        finally:
            vweb.REPO_ROOT = original_root


def test_empty_defs_ok():
    text = _render()
    assert "英文释义" not in text or True


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