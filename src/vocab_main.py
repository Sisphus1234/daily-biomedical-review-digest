"""每日考研词汇流水线入口。

用法：
  python -m src.vocab_main               # 运行今日词汇
  python -m src.vocab_main --date 2026-08-26
  python -m src.vocab_main --dry-run     # 只选词，不调用词典 API / DeepSeek
  python -m src.vocab_main --force       # 忽略"今日已生成"记录重新生成
  python -m src.vocab_main --per-day 15  # 临时指定每日词数
  python -m src.vocab_main --commit      # 完成后自动 git 提交推送
"""

import argparse
import datetime
import os
import pathlib
import subprocess
import sys

from dotenv import load_dotenv

from .vocab import data as vdata
from .vocab import dictapi, llm as vllm, render as vrender

HIGH_FREQ_COUNT = 2444
TOTAL_COUNT = 5530

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


def _get_int(name: str, default: int) -> int:
    v = os.environ.get(name, "").strip()
    try:
        return int(v) if v else default
    except ValueError:
        return default


def load_vocab_config() -> dict:
    """读取词汇任务配置（不强制要求 DeepSeek key，dry-run 可无 key）。"""
    load_dotenv()
    skip_raw = os.environ.get("VOCAB_SKIP_WORDS", "").strip()
    skip = {w.strip().lower() for w in skip_raw.split(",")} if skip_raw else set(DEFAULT_SKIP)
    skip.discard("")
    return {
        "deepseek_api_key": os.environ.get("DEEPSEEK_API_KEY", "").strip(),
        "deepseek_model": os.environ.get("DEEPSEEK_MODEL", "deepseek-chat").strip() or "deepseek-chat",
        "deepseek_base_url": os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip(),
        "temperature": float(os.environ.get("LLM_TEMPERATURE", "0.2").strip() or "0.2"),
        "vocab_per_day": _get_int("VOCAB_PER_DAY", 15),
        "vocab_start": _get_int("VOCAB_START", 0),
        "vocab_skip": skip,
        "git_commit": os.environ.get("GIT_COMMIT", "false").strip().lower() == "true",
    }


def _git(*args: str) -> None:
    subprocess.run(["git", *args], check=True, capture_output=True)


def _commit_and_push(message: str) -> None:
    _git("add", "-A")
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
    if not status.strip():
        print("没有产生变更，跳过提交。")
        return
    _git("commit", "-m", message)
    _git("push")


def main() -> int:
    parser = argparse.ArgumentParser(description="每日考研词汇")
    parser.add_argument("--date", help="指定日期 YYYY-MM-DD，默认今天")
    parser.add_argument("--dry-run", action="store_true", help="只选词，不调用外部接口")
    parser.add_argument("--force", action="store_true", help="忽略今日已生成记录重新生成")
    parser.add_argument("--per-day", type=int, help="临时指定每日词数")
    parser.add_argument("--commit", action="store_true", help="完成后自动 git 提交并推送")
    args = parser.parse_args()

    cfg = load_vocab_config()
    if args.commit:
        cfg["git_commit"] = True
    if args.per_day:
        cfg["vocab_per_day"] = args.per_day

    today = datetime.date.fromisoformat(args.date) if args.date else datetime.date.today()
    date_str = today.isoformat()

    words = vdata.load_word_list()
    progress = vdata.load_progress()
    cache = vdata.load_cache()

    cursor = progress.get("cursor", cfg["vocab_start"])
    if progress.get("last_date") is None:
        cursor = cfg["vocab_start"]

    if not args.force and progress.get("last_date") == date_str:
        print(f"今日（{date_str}）词汇已生成，跳过。使用 --force 可重新生成。")
        return 0

    per_day = cfg["vocab_per_day"]
    picked, new_cursor, cycle = vdata.pick_words(words, cursor, per_day, cfg["vocab_skip"])

    if not picked:
        print("没有可选单词（可能全部被跳过），请调整 VOCAB_SKIP_WORDS。")
        return 1

    day_num = progress.get("total_generated", 0) // per_day + 1
    print(f"[1/4] 第 {day_num} 天，今日 {len(picked)} 词（词频区间 #{picked[0]['rank']}-#{picked[-1]['rank']}）")

    if args.dry_run:
        print("[2/4] DRY-RUN 跳过词典 API 与 DeepSeek。")
        for w in picked:
            print(f"      #{w['rank']} {w['word']}（真题 {w['freq']} 次）: {w['zh']}")
        return 0

    if not cfg["deepseek_api_key"]:
        print("缺少 DEEPSEEK_API_KEY，无法生成精读。参考 .env.example 配置。", file=sys.stderr)
        return 1

    print("[2/4] 获取词典释义（IPA / 英文释义 / 例句）...")
    for w in picked:
        info = dictapi.fetch_word(w["word"], cache)
        if info:
            w["ipa"] = info["ipa"]
            w["defs"] = info["defs"]
            w["dict_source"] = info["source"]

    print("[3/4] DeepSeek 生成中文精读与考点提示 ...")
    refined = vllm.refine_words(cfg, picked)
    ref_map = {r["word"].lower(): r for r in refined["words"]}
    for w in picked:
        r = ref_map.get(w["word"].lower(), {})
        if r.get("zh"):
            w["zh"] = r["zh"]
        w["tip"] = r.get("tip", "")
    summary = refined.get("summary", "")

    cum = progress.get("total_generated", 0) + len(picked)
    progress_note = (
        f"累计进度 {cum}/{TOTAL_COUNT}（其中高频区 {HIGH_FREQ_COUNT} 个已覆盖 "
        f"{min(cum, HIGH_FREQ_COUNT)}）"
        + ("；已完成一轮，开始第二轮。" if cycle else "")
    )
    meta = {
        "progress_note": progress_note,
        "summary": summary,
        "dict_source": picked[0].get("dict_source", "") if picked else "",
    }

    path = vrender.write_day(picked, date_str, meta)
    print(f"[4/4] 已写入: {path}")

    progress["cursor"] = new_cursor
    progress["last_date"] = date_str
    progress["total_generated"] = cum
    if cycle:
        progress["cycles"] = progress.get("cycles", 0) + 1
    vdata.save_progress(progress)
    vdata.save_cache(cache)
    vrender.update_index()

    if cfg["git_commit"]:
        _commit_and_push(f"docs: 每日考研词汇 {date_str}（第 {day_num} 天，{len(picked)} 词）")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"运行失败: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
