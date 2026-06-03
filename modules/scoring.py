from __future__ import annotations

import re

CORE_KEYWORDS = [
    "python",
    "sql",
    "数据分析",
    "用户增长",
    "a/b测试",
    "ab测试",
    "漏斗分析",
    "留存",
    "转化率",
    "数据看板",
    "可视化",
    "电商",
    "业务建议",
    "协作",
    "复盘",
    "归因",
]


def normalize_text(text: str) -> str:
    return text.lower().replace("／", "/").replace("，", " ").replace("。", " ")


def extract_keywords(text: str) -> list[str]:
    normalized = normalize_text(text)
    found = []
    for kw in CORE_KEYWORDS:
        if kw in normalized:
            found.append(kw)
    chinese_terms = re.findall(r"[\u4e00-\u9fff]{2,8}", text)
    for term in chinese_terms:
        if term in found:
            continue
        if any(signal in term for signal in ["分析", "增长", "转化", "留存", "看板", "业务", "用户"]):
            found.append(term)
    return list(dict.fromkeys(found))


def keyword_match(resume_text: str, jd_text: str) -> tuple[list[str], list[str], int]:
    resume_norm = normalize_text(resume_text)
    jd_keywords = extract_keywords(jd_text)
    matched = [kw for kw in jd_keywords if kw.lower() in resume_norm]
    missing = [kw for kw in jd_keywords if kw not in matched]
    score = round(len(matched) / max(len(jd_keywords), 1) * 100)
    return matched, missing, score


def estimate_interview_probability(intent: str, strategy: str, hr_message: str) -> int:
    base = {
        "约面试": 72,
        "薪资沟通": 63,
        "初筛": 52,
        "背景调查": 58,
        "无意向测试": 35,
    }.get(intent, 50)
    if strategy in {"强推进", "推进"}:
        base += 8
    if "时间" in hr_message or "方便" in hr_message or "面试" in hr_message:
        base += 7
    if "薪资" in hr_message or "期望" in hr_message:
        base -= 3
    return max(0, min(100, base))
