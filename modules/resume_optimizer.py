from __future__ import annotations

from modules.ai_service import AIService, as_list
from modules.scoring import keyword_match


def optimize_resume(resume_text: str, jd_text: str) -> dict:
    matched, missing, score = keyword_match(resume_text, jd_text)
    ai = AIService()
    system_prompt = """你是资深招聘顾问和ATS简历优化专家。只输出JSON。
字段：matched_keywords(list), missing_keywords(list), match_score(number), optimized_resume(str), ats_advice(list), rewritten_experiences(list)。
要求：面向中国互联网/科技公司招聘场景，表达自然、具体、可量化，不编造离谱经历。"""
    user_prompt = f"""基础简历：
{resume_text}

目标岗位JD：
{jd_text}

请优化为更容易获得面试的版本。"""
    result = ai.complete_json(system_prompt, user_prompt)
    if result and "_error" not in result:
        result["matched_keywords"] = as_list(result.get("matched_keywords")) or matched
        result["missing_keywords"] = as_list(result.get("missing_keywords")) or missing
        result["match_score"] = int(result.get("match_score", score))
        result["ats_advice"] = as_list(result.get("ats_advice"))
        result["rewritten_experiences"] = as_list(result.get("rewritten_experiences"))
        return result

    optimized = build_local_resume(resume_text, matched, missing)
    return {
        "matched_keywords": matched,
        "missing_keywords": missing,
        "match_score": score,
        "optimized_resume": optimized,
        "ats_advice": [
            "标题和技能区优先放入JD高频关键词，如SQL、Python、A/B测试、漏斗分析、留存分析。",
            "每条经历使用“动作 + 方法 + 指标 + 业务结果”的结构，减少笼统描述。",
            "保留岗位名称、行业词、工具词，避免过度口语化，方便ATS识别。",
        ],
        "rewritten_experiences": rewrite_experiences(matched, missing),
        "ai_error": result.get("_error") if result else "",
    }


def build_local_resume(resume_text: str, matched: list[str], missing: list[str]) -> str:
    keyword_line = "、".join(list(dict.fromkeys(matched + missing[:6])))
    return f"""目标岗位匹配版简历

核心能力：{keyword_line}

个人优势：
- 具备数据分析、业务复盘和增长指标监控经验，能够把数据结论转化为可执行建议。
- 熟悉SQL/Python/可视化看板等分析工具，可支持运营、产品和业务团队进行决策。

优化后经历表达：
- 围绕销售、用户和商品数据建立日常分析口径，持续跟踪GMV、转化率、客单价等核心指标，提升业务复盘效率。
- 支持运营活动复盘，通过漏斗分析定位转化损耗环节，输出可落地的活动优化建议。
- 参与用户增长项目，跟踪转化率、留存率和行为路径，协助团队评估策略效果并迭代方案。
- 搭建数据看板，将分散指标沉淀为可复用监控体系，帮助团队更快发现异常和增长机会。

原始信息保留：
{resume_text}"""


def rewrite_experiences(matched: list[str], missing: list[str]) -> list[str]:
    terms = "、".join(missing[:4]) if missing else "核心业务指标"
    return [
        f"将“整理数据报表”改为“基于SQL/Python沉淀业务指标看板，围绕{terms}持续监控并输出异常分析”。",
        "将“活动复盘”改为“通过漏斗和转化率分析定位活动损耗点，形成可执行的运营优化建议”。",
        "将“参与增长项目”改为“跟踪用户行为、留存和转化指标，评估策略效果并推动下一轮迭代”。",
    ]
