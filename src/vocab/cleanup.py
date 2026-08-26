"""清理过期的每日词汇文件：只保留当天的单词文件与索引。"""

import datetime
import pathlib

from .data import VOCAB_DIR


def cleanup_old_days(today: datetime.date, vocab_dir: pathlib.Path | None = None) -> int:
    """删除 vocab_dir 下文件名前缀日期早于 today 的 *.md 文件，返回删除数量。

    保留 README.md、今天的文件以及非日期命名的文件；
    vocab_dir 为 None 时使用 data.VOCAB_DIR。
    """
    if vocab_dir is None:
        vocab_dir = VOCAB_DIR
    removed = 0
    for p in vocab_dir.glob("*.md"):
        if p.name == "README.md":
            continue
        try:
            file_date = datetime.date.fromisoformat(p.name[:10])
        except ValueError:
            continue
        if file_date < today:
            p.unlink(missing_ok=True)
            removed += 1
    return removed


def cleanup_old_html(today: datetime.date, repo_root: pathlib.Path | None = None) -> int:
    """删除 repo_root 下非当天的残留 vocab.html，返回删除数量；文件不存在返回 0。

    vocab.html 每天由新流程覆盖，此函数仅清理旧页面残留。
    """
    if repo_root is None:
        repo_root = VOCAB_DIR.parent
    page = repo_root / "vocab.html"
    if not page.exists():
        return 0
    mtime = datetime.date.fromtimestamp(page.stat().st_mtime)
    if mtime < today:
        page.unlink(missing_ok=True)
        return 1
    return 0