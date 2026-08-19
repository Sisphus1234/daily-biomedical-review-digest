import os

from dotenv import load_dotenv


def _get_int(name: str, default: int) -> int:
    v = os.environ.get(name, "").strip()
    try:
        return int(v) if v else default
    except ValueError:
        return default


def load_config() -> dict:
    load_dotenv()

    cfg = {
        "deepseek_api_key": os.environ.get("DEEPSEEK_API_KEY", "").strip(),
        "deepseek_model": os.environ.get("DEEPSEEK_MODEL", "deepseek-chat").strip() or "deepseek-chat",
        "deepseek_base_url": os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip(),
        "pubmed_email": os.environ.get("PUBMED_EMAIL", "").strip(),
        "ncbi_api_key": os.environ.get("NCBI_API_KEY", "").strip(),
        "lookback_days": _get_int("LOOKBACK_DAYS", 5),
        "retmax": _get_int("RETMAX", 30),
        "git_commit": os.environ.get("GIT_COMMIT", "false").strip().lower() == "true",
        "max_text_chars": _get_int("MAX_TEXT_CHARS", 60000),
        "temperature": float(os.environ.get("LLM_TEMPERATURE", "0.2").strip() or "0.2"),
    }

    missing = [k for k, v in cfg.items() if k in ("deepseek_api_key", "pubmed_email") and not v]
    if missing:
        raise SystemExit(
            f"缺少必需环境变量: {', '.join(missing)}。请参考 .env.example 配置后重试。"
        )
    return cfg