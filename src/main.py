"""每日精读流水线入口。

用法：
  python -m src.main                 # 运行今日精读
  python -m src.main --date 2026-08-19
  python -m src.main --dry-run       # 只选文不调用 LLM
  python -m src.main --force         # 忽略去重记录重新精读
  python -m src.main --commit        # 完成后自动 git 提交推送
"""

import argparse
import datetime
import json
import os
import pathlib
import subprocess
import sys

from . import llm, pubmed, scoring
from .config import load_config
from .render import (DATA_DIR, NOTES_DIR, cleanup_old_notes, update_index,
                     write_note, _authors_str, _doi_from_articleids)


def _build_paper(rec: dict, today: datetime.date) -> dict:
    pubdate = rec.get("sortpubdate") or rec.get("pubdate", "")
    if isinstance(pubdate, str):
        pubdate = pubdate.split(" ")[0]
    return {
        "pmid": str(rec.get("uid")),
        "title": rec.get("title", ""),
        "journal": rec.get("fulljournalname", ""),
        "pubdate": pubdate,
        "authors": rec.get("authors", []),
        "doi": _doi_from_articleids(rec),
        "date": today.isoformat(),
    }


def _git(cfg: dict, *args: str) -> None:
    subprocess.run(["git", *args], check=True, capture_output=True)


def _commit_and_push(cfg: dict, message: str) -> None:
    _git(cfg, "add", "-A")
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
    if not status.strip():
        print("没有产生变更，跳过提交。")
        return
    _git(cfg, "commit", "-m", message)
    _git(cfg, "push")


def main() -> int:
    parser = argparse.ArgumentParser(description="每日生物医学综述精读")
    parser.add_argument("--date", help="指定日期 YYYY-MM-DD，默认今天")
    parser.add_argument("--dry-run", action="store_true", help="只选文，不调用 LLM")
    parser.add_argument("--force", action="store_true", help="忽略已读记录重新精读")
    parser.add_argument("--commit", action="store_true", help="完成后自动 git 提交并推送")
    args = parser.parse_args()

    cfg = load_config()
    if args.commit:
        cfg["git_commit"] = True
    today = datetime.date.fromisoformat(args.date) if args.date else datetime.date.today()

    print(f"[1/5] 检索最近 {cfg['lookback_days']} 天发表的 Review 综述 ...")
    records = pubmed.search_latest_reviews(cfg)
    print(f"      候选 {len(records)} 篇")

    if not records:
        print("      没有找到候选论文，今日跳过。")
        return 0

    seen = scoring.load_seen(DATA_DIR) if not args.force else set()
    prelim = scoring.score_records(records, seen, today)

    if not prelim:
        print("      候选均已在近期精读过，今日跳过。")
        return 0

    print(f"      候选 {len(prelim)} 篇，拉取前 10 篇摘要用于生物医学相关性筛选 ...")
    top_pmids = [c["pmid"] for c in prelim[:10]]

    fulltext_candidates: dict[str, str] = {}
    for pmid in top_pmids[:5]:
        full = pubmed.fetch_pmc_fulltext(cfg, pmid)
        if full:
            fulltext_candidates[pmid] = full

    abstracts = pubmed.fetch_abstracts(cfg, top_pmids)
    top = scoring.select_best(records, seen, today, abstracts, fulltext_candidates)

    if not top:
        print("      候选均未通过生物医学相关性筛选，今日跳过。")
        return 0

    print(f"[2/5] 选中: {top['title']}（{top['journal']}，{top['pubdate']}，得分 {top['score']}）")
    rec = next(r for r in records if str(r.get("uid")) == top["pmid"])

    print("[3/5] 获取原文 ...")
    if top["pmid"] in fulltext_candidates:
        text, label = fulltext_candidates[top["pmid"]][: cfg["max_text_chars"]], "PMC 开放获取全文"
    else:
        text, label = pubmed.pick_abstract_or_fulltext(cfg, top["pmid"])
    if not text:
        print("      无法获取摘要或全文，跳过该篇。")
        return 2
    print(f"      来源: {label}（{len(text)} 字符）")

    if args.dry_run:
        print("[4/5] DRY-RUN 跳过 LLM 精读。")
        paper = _build_paper(rec, today)
        print(json.dumps({
            "pmid": paper["pmid"], "title": paper["title"],
            "journal": paper["journal"], "doi": paper["doi"], "score": top["score"],
        }, ensure_ascii=False, indent=2))
        return 0

    print("[4/5] DeepSeek 精读中（约 30-90 秒）...")
    reading = llm.deep_read(cfg, _build_paper(rec, today), text, label)
    print("      精读完成。")

    paper = _build_paper(rec, today)
    path = write_note(paper, reading, label)
    seen.add(paper["pmid"])
    scoring.save_seen(DATA_DIR, seen)

    keep_days = max(0, int(os.environ.get("KEEP_DAYS", "0") or "0"))
    removed = cleanup_old_notes(today, keep_days)
    if removed:
        print(f"      已清理 {removed} 篇非当天旧精读（仅保留最近 {keep_days} 天）")

    update_index()
    print(f"[5/5] 已写入: {path}")

    if cfg["git_commit"]:
        _commit_and_push(cfg, f"docs: 每日精读 {paper['date']} - {paper['title'][:60]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())