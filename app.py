from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from modules.database import (
    fetch_delivery_records,
    fetch_hr_interactions,
    fetch_resume_optimizations,
    init_db,
    insert_hr_interaction,
    insert_resume_optimization,
    replace_delivery_records,
    update_outcome,
)
from modules.delivery_strategy import rank_jobs
from modules.history_learning import summarize_history
from modules.hr_reply import analyze_hr_reply
from modules.resume_optimizer import optimize_resume
from modules.sample_data import SAMPLE_HR_MESSAGE, SAMPLE_JD, SAMPLE_JOBS, SAMPLE_RESUME

st.set_page_config(
    page_title="AI求职加速系统",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()


def inject_style() -> None:
    st.markdown(
        """
        <style>
        .main .block-container { padding-top: 1.3rem; }
        .metric-card {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 16px;
            background: #ffffff;
        }
        .small-muted { color: #6b7280; font-size: 0.9rem; }
        .reply-box {
            border-left: 4px solid #2563eb;
            background: #f8fafc;
            padding: 14px 16px;
            border-radius: 6px;
            font-size: 1.05rem;
            line-height: 1.7;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar() -> str:
    st.sidebar.title("AI求职加速系统")
    st.sidebar.caption("Job Interview Booster System")
    return st.sidebar.radio(
        "功能导航",
        ["求职总控面板", "简历优化中心", "HR回复中心", "投递策略面板", "历史学习系统"],
    )


def show_dashboard() -> None:
    rows = fetch_hr_interactions()
    history = summarize_history(rows)
    latest_probability = rows[0]["probability"] if rows else 0
    marked = [row for row in rows if row["outcome"] in {"推进成功", "推进失败"}]
    success = [row for row in marked if row["outcome"] == "推进成功"]

    st.title("求职总控面板")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("当前面试概率", f"{latest_probability}%")
    col2.metric("历史推进成功率", f"{history['success_rate']}%")
    col3.metric("HR沟通记录", len(rows))
    col4.metric("成功推进次数", len(success))

    st.subheader("当前优化建议")
    suggestions = history["insights"][:3]
    for item in suggestions:
        st.info(item)

    st.subheader("今日提升目标")
    st.write(
        "1. 用目标JD重新优化一次简历关键词。\n"
        "2. 对每条HR消息只发一条高质量回复，包含匹配点和下一步动作。\n"
        "3. 优先投递关键词匹配高、竞争度低的岗位。"
    )

    recent = fetch_resume_optimizations()
    if recent:
        st.subheader("最近一次简历优化")
        item = recent[0]
        st.write(f"命中关键词：{item['matched_keywords'] or '暂无'}")
        st.write(f"缺失关键词：{item['missing_keywords'] or '暂无'}")


def show_resume_center() -> None:
    st.title("简历优化中心")
    left, right = st.columns(2)
    with left:
        resume_text = st.text_area("基础简历内容", value=SAMPLE_RESUME, height=330)
    with right:
        jd_text = st.text_area("目标岗位JD", value=SAMPLE_JD, height=330)

    if st.button("生成高通过率简历", type="primary", use_container_width=True):
        if not resume_text.strip() or not jd_text.strip():
            st.error("请同时输入简历内容和岗位JD。")
            return
        with st.spinner("正在分析JD关键词并改写简历..."):
            result = optimize_resume(resume_text, jd_text)
            insert_resume_optimization(
                {
                    "resume_text": resume_text,
                    "jd_text": jd_text,
                    "matched_keywords": "、".join(result["matched_keywords"]),
                    "missing_keywords": "、".join(result["missing_keywords"]),
                    "optimized_resume": result["optimized_resume"],
                    "ats_advice": json.dumps(result["ats_advice"], ensure_ascii=False),
                }
            )
            st.session_state["resume_result"] = result

    result = st.session_state.get("resume_result")
    if result:
        st.metric("关键词匹配率", f"{result['match_score']}%")
        if result.get("ai_error"):
            st.warning(result["ai_error"])
        c1, c2 = st.columns(2)
        c1.success("命中关键词：" + ("、".join(result["matched_keywords"]) or "暂无"))
        c2.warning("缺失关键词：" + ("、".join(result["missing_keywords"]) or "暂无"))

        st.subheader("Before / After 对比")
        before, after = st.columns(2)
        before.text_area("原始简历", value=resume_text, height=360, disabled=True)
        after.text_area("优化后简历", value=result["optimized_resume"], height=360)

        st.subheader("ATS优化建议")
        for advice in result["ats_advice"]:
            st.write(f"- {advice}")

        st.subheader("经历改写建议")
        for exp in result["rewritten_experiences"]:
            st.write(f"- {exp}")


def show_hr_center() -> None:
    st.title("HR回复中心")
    resume_info = st.text_area("用户简历信息", value=SAMPLE_RESUME, height=180)
    hr_message = st.text_area("HR消息文本", value=SAMPLE_HR_MESSAGE, height=150)

    if st.button("生成唯一最佳回复", type="primary", use_container_width=True):
        if not hr_message.strip():
            st.error("请输入HR消息。")
            return
        with st.spinner("正在判断HR意图、策略和面试概率..."):
            result = analyze_hr_reply(hr_message, resume_info)
            insert_hr_interaction(
                {
                    "hr_message": hr_message,
                    "user_reply": result["best_reply"],
                    "intent": result["intent"],
                    "strategy": result["strategy"],
                    "probability": result["probability"],
                    "risks": "；".join(result["risks"]),
                    "suggestions": "；".join(result["suggestions"]),
                }
            )
            st.session_state["hr_result"] = result

    result = st.session_state.get("hr_result")
    if result:
        if result.get("ai_error"):
            st.warning(result["ai_error"])
        c1, c2, c3 = st.columns(3)
        c1.metric("HR意图", result["intent"])
        c2.metric("当前策略", result["strategy"])
        c3.metric("当前面试概率", f"{result['probability']}%")

        st.subheader("唯一最佳回复")
        st.markdown(f"<div class='reply-box'>{result['best_reply']}</div>", unsafe_allow_html=True)
        st.text_area("复制回复", value=result["best_reply"], height=110)

        st.subheader("风险点")
        for risk in result["risks"]:
            st.write(f"- {risk}")
        st.subheader("提升建议")
        for suggestion in result["suggestions"][:3]:
            st.write(f"- {suggestion}")


def show_delivery_panel() -> None:
    st.title("投递策略面板")
    resume_text = st.text_area("用于匹配的简历内容", value=SAMPLE_RESUME, height=220)
    st.caption("岗位列表使用内置示例数据，可在代码中扩展为爬虫、CSV导入或SaaS岗位池。")

    if st.button("计算优先投递顺序", type="primary", use_container_width=True):
        ranked = rank_jobs(resume_text, SAMPLE_JOBS)
        replace_delivery_records(ranked)
        st.session_state["ranked_jobs"] = ranked

    ranked = st.session_state.get("ranked_jobs") or [dict(row) for row in fetch_delivery_records()]
    if ranked:
        df = pd.DataFrame(ranked)
        st.dataframe(
            df[["company", "title", "salary", "match_score", "competition", "priority_score", "reason"]],
            use_container_width=True,
            hide_index=True,
        )
        best = ranked[0]
        st.success(f"最高优先级：{best['company']} - {best['title']}。{best['reason']}")


def show_history() -> None:
    st.title("历史学习系统")
    rows = fetch_hr_interactions()
    summary = summarize_history(rows)
    c1, c2 = st.columns(2)
    c1.metric("历史记录数", summary["total"])
    c2.metric("已标记样本成功率", f"{summary['success_rate']}%")

    st.subheader("AI策略复盘")
    for item in summary["insights"]:
        st.info(item)
    st.subheader("应避免的回复模式")
    for item in summary["avoid"]:
        st.write(f"- {item}")

    st.subheader("HR沟通记录")
    for row in rows:
        with st.expander(f"#{row['id']} {row['intent']} | {row['strategy']} | {row['probability']}% | {row['outcome']}"):
            st.write("HR消息：")
            st.write(row["hr_message"])
            st.write("用户回复：")
            st.write(row["user_reply"])
            outcome = st.selectbox(
                "标记结果",
                ["未标记", "推进成功", "推进失败"],
                index=["未标记", "推进成功", "推进失败"].index(row["outcome"]),
                key=f"outcome_{row['id']}",
            )
            if st.button("保存标记", key=f"save_{row['id']}"):
                update_outcome(row["id"], outcome)
                st.success("已保存。刷新后会更新统计。")


def main() -> None:
    inject_style()
    page = sidebar()
    if page == "求职总控面板":
        show_dashboard()
    elif page == "简历优化中心":
        show_resume_center()
    elif page == "HR回复中心":
        show_hr_center()
    elif page == "投递策略面板":
        show_delivery_panel()
    else:
        show_history()


if __name__ == "__main__":
    main()
