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