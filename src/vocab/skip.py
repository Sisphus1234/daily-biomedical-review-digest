"""跳过词管理：默认功能词 + CET-4 已掌握词 + 环境变量自定义词。

供选词逻辑（pick_words 的 skip 参数）使用，用于过滤已掌握的简单词汇。
"""

import os
import pathlib

DEFAULT_SKIP = {
    "the", "be", "a", "an", "of", "and", "or", "to", "in", "on", "at", "by",
    "for", "with", "from", "is", "are", "was", "were", "been", "have", "has",
    "had", "do", "does", "did", "not", "no", "yes", "you", "your", "he", "she",
    "it", "its", "we", "they", "i", "my", "me", "him", "her", "them", "us",
    "this", "that", "these", "those", "what", "which", "who", "whom", "when",
    "where", "why", "how", "as", "if", "but", "so", "then", "there", "here",
    "their", "will", "more", "can", "one", "than", "his", "our", "also",
    "very", "only", "even", "some", "any", "all", "each", "every", "other",
    "another", "such", "most", "many", "much", "few", "little", "own", "same",
    "still", "just", "up", "down", "out", "off", "over", "under", "before",
    "after", "between", "without", "through", "into", "around", "near", "far",
}

DATA_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "data"
CET4_PATH = DATA_DIR / "cet4_words.txt"


def load_skip_set(cfg: dict) -> set[str]:
    """加载完整跳过词集合，返回小写单词集合。

    由三部分组成：
    1. DEFAULT_SKIP：纯功能词，始终保留。
    2. data/cet4_words.txt：CET-4 已掌握词，由环境变量 VOCAB_SKIP_CET4 控制
       （"true" 加载，默认 true；"false" 不加载）。数据文件缺失时静默降级。
    3. VOCAB_SKIP_WORDS：逗号分隔的自定义词。注意：原 VOCAB_SKIP_WORDS 语义
       为"覆盖默认跳过词"，此处为兼容改为合并（自定义词追加进集合而非替换）。
    """
    skip = set(DEFAULT_SKIP)

    if os.environ.get("VOCAB_SKIP_CET4", "true").strip().lower() != "false":
        if CET4_PATH.exists():
            try:
                skip.update(CET4_PATH.read_text(encoding="utf-8").split())
            except OSError:
                pass

    skip_raw = os.environ.get("VOCAB_SKIP_WORDS", "").strip()
    if skip_raw:
        skip.update(w.strip().lower() for w in skip_raw.split(",") if w.strip())

    return skip