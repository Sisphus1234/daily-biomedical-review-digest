"""离线单元测试：每日词汇文件清理逻辑（不联网、不触碰真实目录）。

运行：python -m tests.test_vocab_cleanup
"""

import datetime
import os
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src.vocab import cleanup  # noqa: E402


def test_cleanup_old_days_keeps_today_removes_old():
    today = datetime.date(2026, 8, 27)
    with tempfile.TemporaryDirectory() as tmp:
        d = pathlib.Path(tmp)
        (d / "2026-08-26.md").write_text("old", encoding="utf-8")
        (d / "2026-08-25.md").write_text("older", encoding="utf-8")
        (d / "2026-08-27.md").write_text("today", encoding="utf-8")
        removed = cleanup.cleanup_old_days(today, d)
        assert removed == 2
        assert not (d / "2026-08-26.md").exists()
        assert not (d / "2026-08-25.md").exists()
        assert (d / "2026-08-27.md").exists()


def test_cleanup_old_days_keeps_readme_and_non_date_names():
    today = datetime.date(2026, 8, 27)
    with tempfile.TemporaryDirectory() as tmp:
        d = pathlib.Path(tmp)
        (d / "2026-08-26.md").write_text("old", encoding="utf-8")
        (d / "README.md").write_text("index", encoding="utf-8")
        (d / "daily.md").write_text("other", encoding="utf-8")
        (d / "2026-8-7.md").write_text("bad", encoding="utf-8")
        removed = cleanup.cleanup_old_days(today, d)
        assert removed == 1
        assert not (d / "2026-08-26.md").exists()
        for name in ("README.md", "daily.md", "2026-8-7.md"):
            assert (d / name).exists()


def test_cleanup_old_days_empty_dir():
    today = datetime.date(2026, 8, 27)
    with tempfile.TemporaryDirectory() as tmp:
        assert cleanup.cleanup_old_days(today, pathlib.Path(tmp)) == 0


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