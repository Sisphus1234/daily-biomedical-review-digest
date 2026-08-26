"""离线单元测试：跳过词集合加载逻辑（不联网、不读 .env）。

运行：python -m tests.test_vocab_skip
"""

import os
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src.vocab import skip as vskip  # noqa: E402

_ENV_KEYS = ("VOCAB_SKIP_CET4", "VOCAB_SKIP_WORDS")


def _clean_env():
    saved = {k: os.environ.get(k) for k in _ENV_KEYS}
    for k in _ENV_KEYS:
        os.environ.pop(k, None)
    return saved


def _restore_env(saved):
    for k, v in saved.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


def test_default_skip_always_present():
    saved = _clean_env()
    try:
        result = vskip.load_skip_set({})
        assert vskip.DEFAULT_SKIP.issubset(result)
    finally:
        _restore_env(saved)


def test_custom_words_appended():
    saved = _clean_env()
    try:
        os.environ["VOCAB_SKIP_WORDS"] = "Abandon, CAT "
        result = vskip.load_skip_set({})
        assert "abandon" in result
        assert "cat" in result
        assert vskip.DEFAULT_SKIP.issubset(result)
    finally:
        _restore_env(saved)


def test_cet4_disabled():
    saved = _clean_env()
    try:
        os.environ["VOCAB_SKIP_CET4"] = "false"
        result = vskip.load_skip_set({})
        sample = [w for w in vskip.CET4_PATH.read_text(encoding="utf-8").split()
                  if w not in vskip.DEFAULT_SKIP]
        assert sample
        assert all(w not in result for w in sample[:20])
    finally:
        _restore_env(saved)


def test_cet4_file_clean():
    assert vskip.CET4_PATH.exists()
    words = vskip.CET4_PATH.read_text(encoding="utf-8").splitlines()
    assert len(words) > 1000
    assert len(words) == len(set(words))
    assert all(re.fullmatch(r"[a-z]+", w) for w in words)


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