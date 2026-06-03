from __future__ import annotations

from modules.ai_service import AIService, as_list
from modules.scoring import estimate_interview_probability


def analyze_hr_reply(hr_message: str, resume_info: str) -> dict:
    local_intent = infer_intent(hr_message)
    local_strategy = infer_strategy(local_intent, hr_message)
    local_probability = estimate_interview_probability(local_intent, local_strategy, hr_message)
    ai = AIService()
    system_prompt = """你是求职沟通策略专家。只输出JSON。
字段：intent(str), strategy(str), best_reply(str), probability(number), risks(list), suggestions(list)。
intent只能是：初筛、约面试、薪资沟通、背景调查、无意向测试。
strategy只能是：推进、稳住、反问、延迟、强推进。
best_reply只能有1条，2到4句，自然、不模板化，必须推进面试或提升好感。"""
    user_prompt = f"""HR消息：
{hr_message}

用户简历信息：
{resume_info}

请输出最优回复策略。"""
    result = ai.complete_json(system_prompt, user_prompt)
    if result and "_error" not in result:
        return {
            "intent": result.get("intent", local_intent),
            "strategy": result.get("strategy", local_strategy),
            "best_reply": result.get("best_reply", build_local_reply(local_intent, hr_message)),
            "probability": int(result.get("probability", local_probability)),
            "risks": as_list(result.get("risks")),
            "suggestions": as_list(result.get("suggestions")),
        }

    return {
        "intent": local_intent,
        "strategy": local_strategy,
        "best_reply": build_local_reply(local_intent, hr_message),
        "probability": local_probability,
        "risks": build_risks(local_intent),
        "suggestions": build_suggestions(local_intent),
        "ai_error": result.get("_error") if result else "",
    }


def infer_intent(message: str) -> str:
    text = message.lower()
    if any(word in text for word in ["面试", "时间", "方便", "视频", "电话"]):
        return "约面试"
    if any(word in text for word in ["薪资", "期望", "base", "待遇"]):
        return "薪资沟通"
    if any(word in text for word in ["背调", "证明", "离职原因", "上家公司"]):
        return "背景调查"
    if any(word in text for word in ["看看", "了解一下", "在看机会", "是否考虑"]):
        return "初筛"
    if any(word in text for word in ["暂时", "不确定", "先收集", "人才库"]):
        return "无意向测试"
    return "初筛"


def infer_strategy(intent: str, message: str) -> str:
    if intent == "约面试":
        return "强推进"
    if intent == "薪资沟通":
        return "稳住"
    if intent == "背景调查":
        return "反问"
    if intent == "无意向测试":
        return "反问"
    return "推进"


def build_local_reply(intent: str, message: str) -> str:
    if intent == "约面试":
        return "您好，我对这个岗位很感兴趣，也觉得自己的数据分析和业务协作经验比较匹配。今天下午或明天上午我都方便沟通，您看哪个时间更合适？"
    if intent == "薪资沟通":
        return "您好，我目前更希望先确认岗位匹配度和团队预期，再给出更准确的薪资范围。结合我的数据分析、增长复盘和看板建设经验，如果双方匹配，我相信薪资可以在合理区间内沟通。"
    if intent == "背景调查":
        return "您好，可以的，我愿意配合必要的背景信息确认。想先了解一下这一步主要核实哪些内容，以及是否已经进入下一轮面试评估阶段？"
    if intent == "无意向测试":
        return "您好，我确实在关注更匹配的机会，尤其是能深入参与业务增长和数据决策的岗位。方便的话，您可以发我岗位职责和团队情况，我会尽快判断匹配度并回复您。"
    return "您好，我最近有在关注新的机会，这个方向和我过往的数据分析、活动复盘、增长指标跟踪经验比较匹配。方便的话您可以发我岗位JD，我也可以补充说明最相关的项目经历。"


def build_risks(intent: str) -> list[str]:
    return {
        "约面试": ["时间回复不明确会降低推进效率。"],
        "薪资沟通": ["过早报死薪资可能让HR直接筛掉。"],
        "背景调查": ["信息给得过多但不反问流程，容易失去主动权。"],
        "无意向测试": ["对方可能只是泛泛收集候选人，需要用反问确认真实岗位。"],
        "初筛": ["只说“有兴趣”不够，需要补充匹配点。"],
    }.get(intent, ["当前信息不足，需要继续确认岗位匹配度。"])


def build_suggestions(intent: str) -> list[str]:
    return {
        "约面试": ["直接给出2个可面试时间。", "补一句岗位匹配点，增强HR安排意愿。"],
        "薪资沟通": ["先把薪资锚定到岗位匹配后沟通。", "避免低于预期或高到离谱的单点报价。"],
        "背景调查": ["配合但确认流程阶段。", "只提供必要信息。"],
        "无意向测试": ["反问JD和团队信息。", "用具体方向表达兴趣，避免显得被动。"],
        "初筛": ["主动索要JD。", "用1句概括最相关经历。"],
    }.get(intent, ["补充岗位信息后再推进。"])
