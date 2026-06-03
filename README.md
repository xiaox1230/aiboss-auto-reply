# AI求职加速系统（Job Interview Booster System）

一个可运行的 Streamlit + Python + SQLite 应用，用 AI 优化简历命中率、HR 回复率、面试推进率和 offer 概率。

## 快速启动

```bash
pip install -r requirements.txt
streamlit run app.py
```

如需调用 OpenAI 或 DeepSeek API，请复制 `.env.example` 为 `.env` 并填写：

```bash
OPENAI_API_KEY=你的密钥
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

DeepSeek 可使用：

```bash
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat
```

没有配置 API Key 时，系统会使用本地规则引擎兜底，仍可完整运行。

## 模块

- 求职总控面板：概率总览、建议、今日目标
- 简历优化中心：JD 关键词匹配、ATS 建议、经历改写、优化版简历
- HR 回复中心：意图分析、对话策略、唯一最佳回复、面试概率评分
- 投递策略面板：岗位排序、命中率、竞争度、推荐理由
- 历史学习系统：成功/失败记录、策略复盘

## 项目结构

```text
app.py
modules/
  ai_service.py
  database.py
  resume_optimizer.py
  hr_reply.py
  scoring.py
  delivery_strategy.py
  history_learning.py
  sample_data.py
data/
  job_booster.sqlite
```
