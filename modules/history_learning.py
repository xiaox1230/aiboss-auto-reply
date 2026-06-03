from __future__ import annotations

from collections import Counter
from sqlite3 import Row


def summarize_history(rows: list[Row]) -> dict:
    total = len(rows)
    if total == 0:
        return {
            "total": 0,
            "success_rate": 0,
            "insights": ["暂无历史记录。先在HR回复中心生成回复，并在这里标记结果。"],
            "avoid": ["避免只回复“好的”“可以”，每次都要留下推进动作。"],
        }

    success_rows = [row for row in rows if row["outcome"] == "推进成功"]
    failed_rows = [row for row in rows if row["outcome"] == "推进失败"]
    success_rate = round(len(success_rows) / max(len(success_rows) + len(failed_rows), 1) * 100)
    success_strategies = Counter(row["strategy"] for row in success_rows)
    failed_intents = Counter(row["intent"] for row in failed_rows)

    insights = []
    if success_strategies:
        strategy, count = success_strategies.most_common(1)[0]
        insights.append(f"历史上“{strategy}”策略推进效果最好，已成功 {count} 次。")
    else:
        insights.append("还没有明确的成功策略样本，建议先积累3条以上标记记录。")

    if failed_intents:
        intent, count = failed_intents.most_common(1)[0]
        insights.append(f"失败样本中“{intent}”场景最多，后续需要更谨慎处理。")

    insights.append("高质量回复通常包含：岗位兴趣、个人匹配点、下一步动作。")
    avoid = [
        "薪资沟通过早给单点报价。",
        "约面试时不提供明确时间。",
        "对泛泛试探不反问JD和团队信息。",
    ]
    return {
        "total": total,
        "success_rate": success_rate,
        "insights": insights,
        "avoid": avoid,
    }
