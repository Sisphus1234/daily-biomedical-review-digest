"""重建 index.html 为最新真实精读。"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src.render import _md_to_html, REPO_ROOT  # noqa: E402

NOTES = REPO_ROOT / "notes"
notes = [p for p in NOTES.glob("*.md") if p.name != "README.md"]
notes.sort(reverse=True)
if not notes:
    raise SystemExit("notes 目录为空")
latest = notes[0]
md = latest.read_text(encoding="utf-8")
body = _md_to_html(md)
date = latest.name[:10]

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>每日生物医学综述精读 · {date}</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; max-width: 900px; margin: 0 auto; padding: 24px; line-height: 1.8; color: #1a1a1a; background: #fafafa; }}
  h1 {{ font-size: 1.6em; border-bottom: 2px solid #2c7be5; padding-bottom: 8px; }}
  h2 {{ font-size: 1.3em; color: #2c7be5; margin-top: 32px; border-left: 4px solid #2c7be5; padding-left: 10px; }}
  h3 {{ font-size: 1.1em; margin-top: 24px; }}
  blockquote {{ border-left: 4px solid #d0d7de; margin: 8px 0; padding: 8px 16px; background: #f0f3f6; color: #333; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
  th, td {{ border: 1px solid #d0d7de; padding: 8px; text-align: left; vertical-align: top; font-size: 0.92em; }}
  th {{ background: #f0f3f6; }}
  a {{ color: #2c7be5; }}
  .footer {{ margin-top: 48px; padding-top: 16px; border-top: 1px solid #e5e7eb; color: #999; font-size: 0.85em; }}
</style>
</head>
<body>
{body}
<div class="footer">每日精读自动生成 · 每日 09:15 更新 · 仅供学习参考，请以原文为准</div>
</body>
</html>
"""

(REPO_ROOT / "index.html").write_text(TEMPLATE.format(date=date, body=body), encoding="utf-8")
print(f"index.html regenerated from {latest.name}, bytes: {(REPO_ROOT / 'index.html').stat().st_size}")