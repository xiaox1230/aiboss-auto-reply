from __future__ import annotations

from modules.scoring import keyword_match


def rank_jobs(resume_text: str, jobs: list[dict]) -> list[dict]:
    ranked = []
    for job in jobs:
        matched, missing, match_score = keyword_match(resume_text, job["jd"])
        competition = int(job.get("competition", 60))
        priority = round(match_score * 0.68 + (100 - competition) * 0.32)
        ranked.append(
            {
                **job,
                "matched_keywords": "、".join(matched) or "暂无明显命中",
                "missing_keywords": "、".join(missing[:6]) or "无明显缺失",
                "match_score": match_score,
                "priority_score": priority,
                "reason": build_reason(match_score, competition, matched, missing),
            }
        )
    return sorted(ranked, key=lambda item: item["priority_score"], reverse=True)


def build_reason(match_score: int, competition: int, matched: list[str], missing: list[str]) -> str:
    if match_score >= 70 and competition <= 60:
        level = "优先投递，关键词匹配较高且竞争压力可控"
    elif match_score >= 55:
        level = "建议投递，但投递前应补齐JD关键词"
    else:
        level = "谨慎投递，当前简历命中率偏低"
    hit = "、".join(matched[:5]) or "暂无核心词"
    gap = "、".join(missing[:3]) or "缺口较少"
    return f"{level}。已命中：{hit}；需强化：{gap}。"
