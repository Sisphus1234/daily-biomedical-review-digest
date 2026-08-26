"""DeepSeek 精读：为每日单词生成精炼中文释义、考点提示与当日学习建议。"""

import json
import time

from ..llm import _extract_json, call_deepseek

_SYSTEM_PROMPT = """你是资深考研英语词汇老师，熟悉考研英语一/二与六级真题。

任务：针对给定的一批考研高频词，为每个词生成精读信息。
要求：
1. 释义精炼准确，覆盖常见义项，重点标注"熟词僻义"（考研常考但易忽略的义项）。
2. 考点提示给出记忆点：词根词缀、常见固定搭配、真题常考用法或易混词辨析。
3. 全程用简体中文输出。

只输出一个 JSON 对象，不要输出任何其他文字。结构：
{
  "words": [
    {"word": "英文单词", "zh": "精炼中文释义（合并义项，标注熟词僻义）", "tip": "记忆/考点提示，30-60字"}
  ],
  "summary": "今日整体学习建议，2-3 句话"
}
"""

_REQUIRED_FIELDS = ("words", "summary")


def refine_words(cfg: dict, batch: list[dict], max_attempts: int = 3) -> dict:
    """为一批单词生成精读信息 JSON；失败自动重试自纠。"""
    payload = [{"word": w["word"], "freq": w["freq"], "zh": w["zh"]} for w in batch]
    user_prompt = json.dumps(payload, ensure_ascii=False, indent=2)
    last_err = None
    content = None
    for attempt in range(1, max_attempts + 1):
        try:
            content = call_deepseek(cfg, _SYSTEM_PROMPT, user_prompt)
            data = _extract_json(content)
            missing = [f for f in _REQUIRED_FIELDS if f not in data]
            if missing:
                raise ValueError(f"DeepSeek 输出缺少字段: {missing}")
            words = {w["word"].lower(): w for w in data["words"]}
            for w in batch:
                key = w["word"].lower()
                if key not in words:
                    words[key] = {"word": w["word"], "zh": w["zh"], "tip": ""}
            return {"words": [words[w["word"].lower()] for w in batch],
                    "summary": data.get("summary", "")}
        except Exception as e:  # noqa: BLE001 - 网络/解析错误一律重试
            last_err = e
            if attempt == max_attempts:
                break
            time.sleep(1.5 * (2 ** (attempt - 1)))
            user_prompt += (
                "\n\n上次输出不符合要求，请只输出符合给定 JSON 结构的对象。"
                f"\n错误：{last_err}"
                + (f"\n上次输出：{content}" if content else "")
            )
    raise RuntimeError(f"DeepSeek 词汇精读连续 {max_attempts} 次失败: {last_err}")
