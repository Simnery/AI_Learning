# 1.2.1 AI大模型基本原理及API使用

> 1.2 实操基础 > 1. AI大模型基础

---

## 核心概念


### 前置知识

- 建议先阅读本知识图谱同级目录中的先修节点（见进阶方向中的内部链接）。

### 什么是生成式 AI

AI 分为两大类：

| 类型 | 做什么 | 举例 |
|------|--------|------|
| **分析式 AI**（传统） | 分类、识别、预测 | 垃圾邮件过滤、人脸识别、股价预测 |
| **生成式 AI**（新范式） | 创造新内容 | ChatGPT 写文章、Midjourney 画图、Sora 做视频 |

大语言模型（LLM）是生成式 AI 的代表——给它一段文字（prompt），它生成一段新的文字（completion）。

### LLM 是怎么"学会"的

三步走：

```
1. 预训练（Pre-training）
   万亿级文本 → 学习语法、知识、推理模式
   效果：模型学会了"接话"——给定上文，预测下一个词
   ↓
2. 指令微调（Instruction Tuning）
   用"问题-答案"对训练 → 学会"听懂人话"、遵循指令
   效果：从"接话机器"变成"有用的助手"
   ↓
3. RLHF（人类反馈强化学习）
   人类给回答打分 → 模型学习"什么是好回答"
   效果：回答更有帮助、更安全、更符合人类偏好
```

### Temperature 和 Top-P：控制创造力的旋钮

两个参数控制模型输出的"随机性"：

| 参数 | 范围 | 低值效果 | 高值效果 |
|------|------|---------|---------|
| **Temperature** | 0-2 | 确定性高，每次答案相似（适合代码、数学） | 随机性高，答案多样（适合创意写作） |
| **Top-P** | 0-1 | 只选最可能的词（保守） | 考虑更多候选词（多样） |

**实用建议**：代码/翻译用 Temperature=0.1；闲聊用 0.7-0.9；诗歌/故事用 1.0+。

### API 调用的核心概念

| 概念 | 说明 | 
|------|------|
| **System Prompt** | 系统级角色设定，优先级最高（"你是XX专家"） |
| **User Prompt** | 用户的实际问题 |
| **Token** | 文本的最小单位，1 个汉字≈2 token，1 个英文单词≈1-2 token |
| **Context Window** | 模型一次能"记住"的最大 token 数（GPT-4o 约 128K） |
| **Max Tokens** | 限制模型输出的最大长度 |

---

## 原理讲解

### GPT 进化史：从 GPT-1 到 GPT-5

| 版本 | 时间 | 参数量 | 关键突破 |
|------|------|--------|---------|
| GPT-1 | 2018 | 1.17 亿 | 证明"预训练+微调"有效 |
| GPT-2 | 2019 | 15 亿 | 零样本学习能力初现 |
| GPT-3 | 2020 | 1750 亿 | 上下文学习（Few-shot）成为可能 |
| GPT-3.5 | 2022 | ~1750 亿 | ChatGPT 诞生，RLHF 加持 |
| GPT-4 | 2023 | 未公开（~1.8 万亿） | 多模态、推理能力飞跃 |
| GPT-4o | 2024 | 未公开 | 原生多模态，速度+成本大幅优化 |

**核心规律**：参数量每代约增加 10 倍，在某个临界点后突然涌现新能力（"涌现现象"）。

### 温度的原理（用代码理解）

Temperature 实际改变的是"概率分布"：

```python
# 概念演示（非真实源码）
logits = [2.0, 1.0, 0.5, 0.1]  # 4个候选词的原始分数
# Temperature = 1.0（默认）：
probs = softmax(logits / 1.0)  # [0.50, 0.25, 0.15, 0.10]
# Temperature = 0.5（降温）：
probs = softmax(logits / 0.5)  # [0.72, 0.18, 0.07, 0.03] ← 更极端，选最可能的
# Temperature = 2.0（升温）：
probs = softmax(logits / 2.0)  # [0.36, 0.26, 0.21, 0.17] ← 更平均，更随机
```

---

## 代码实战

### 1. 基础 API 调用（OpenAI）

```bash
pip install openai
```

```python
# openai_basics.py — API 调用的完整示例
from openai import OpenAI

client = OpenAI()  # 从环境变量 OPENAI_API_KEY 读取密钥

# 示例1：System Prompt 设定角色
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "你是一个幼儿园老师，用最温柔的语气回答问题。"},
        {"role": "user", "content": "为什么天是蓝色的？"}
    ],
    temperature=0.7,   # 适中创造力
    max_tokens=200      # 限制输出长度
)
print(response.choices[0].message.content)
# 预期：温柔的、用孩子能懂的语言解释瑞利散射

# 示例2：查看 token 用量
print(f"输入 tokens: {response.usage.prompt_tokens}")
print(f"输出 tokens: {response.usage.completion_tokens}")
print(f"总 tokens: {response.usage.total_tokens}")
```

### 2. 阿里巴巴 DashScope（通义千问）调用

```bash
pip install dashscope
```

```python
# qwen_dashscope.py — 使用阿里云 DashScope 调用通义千问
# 前提：注册阿里云账号，获取 API Key，设置环境变量 DASHSCOPE_API_KEY
import dashscope
from dashscope import Generation

# CASE1：情感分析
response = Generation.call(
    model="qwen-turbo",
    prompt="判断以下文本的情感（积极/消极/中性）：'这个产品太棒了，我非常喜欢！'",
    temperature=0.1,  # 确定性任务用低温度
    result_format='message'
)
if response.status_code == 200:
    print(response.output.choices[0].message.content)
    # 预期：积极

# CASE2：Function Calling（让模型调用函数）
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取指定城市的天气",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名称"}
            },
            "required": ["city"]
        }
    }
}]

response = Generation.call(
    model="qwen-plus",
    messages=[{"role": "user", "content": "今天杭州天气怎么样？"}],
    tools=tools,
    temperature=0.1
)
print(response.output.choices[0].message)
# 预期：返回 tool_calls，包含 get_weather(city="杭州")
```

### 3. Temperature 效果对比

```python
# temperature_demo.py — 同一个问题，不同温度的效果
from openai import OpenAI

client = OpenAI()
question = "用一句话介绍人工智能"

for temp in [0.1, 0.7, 1.5]:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}],
        temperature=temp
    )
    answer = response.choices[0].message.content
    print(f"Temperature={temp}: {answer}\n")

# Temperature=0.1: 人工智能是模拟人类智能的计算机科学分支。  （稳定、标准）
# Temperature=0.7: 人工智能就像是给计算机装上了大脑！         （活泼、生动）
# Temperature=1.5: 从神经脉络到机械灵魂，AI是数字时代的炼金术...（诗意、发散）
```

### 4. 关键代码解读

| 代码段 | 设计意图 |
|--------|---------|
| `role: system` | 设定角色和规则，这是 API 调用的"第一道防线"——先定义"你是谁"，再提问 |
| `temperature=0.1` 用于情感分析 | 确定性任务（分类、提取）用低温，否则同一段文字可能输出不同结果 |
| `tools` 参数 | Function Calling 的核心——不是让模型"假装"调用函数，而是通过 JSON Schema 严格约束调用格式 |
| `model` 的选择 | `gpt-4o-mini` 性价比最高（常规任务），`qwen-turbo` 国内免费额度多，各有适用场景 |

---

### 预期输出

运行上述代码后，终端应看到类似以下结果（具体数值因环境与输入而异）：

```
（示例）关键日志/打印行出现，且无 Traceback
任务状态: success
耗时: <N> ms
```

若报错，优先检查：依赖是否安装、API Key/本地服务是否可用、路径与 Python 版本是否匹配。

## 进阶方向

### 当前局限
- **API 调用有成本**：GPT-4o 约 $2.5/百万输入 token，高并发场景成本需优化
- **Token 限制**：长文档（>128K token）需要分片处理或使用 RAG
- **网络依赖**：调用国外 API 可能不稳定，国内建议阿里云/百度/讯飞等作为主力

### 下一步学什么
- [1.3.1 企业级 AI 部署](../1-3_模型部署及高并发_——_理论知识+案例详解+实操/1-3-1_企业级AI部署从硬件选型到框架选择.md) — 从调 API 到自己部署模型
- [2.2.1 Function Calling 与 MCP](../../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-1_Function_Calling与MCP.md) — 深入工具调用

### 工业界最佳实践
- **多模型路由**：简单任务用 `gpt-4o-mini`，复杂推理用 `gpt-4o` 或 `claude-sonnet-4-6`，降低成本
- **缓存+重试**：相同问题缓存结果；API 超时做指数退避重试
- **流式输出（Streaming）**：长回答用 `stream=True`，用户体验更好（逐字输出）

---

## 常见问题

**Q1：API Key 应该存在哪里？代码里直接写行不行？**

绝对不行。API Key 相当于你的银行卡密码，写在代码里提交到 GitHub 会被自动扫描并盗用。正确做法：用环境变量（`export OPENAI_API_KEY=sk-xxx`）或 `.env` 文件（`.gitignore` 排除）。

**Q2：Temperature 设 0 是不是就一定输出一样？**

不是绝对一样。Temperature=0 只表示模型选择概率最高的 token，但因为 GPU 浮点数精度、并发调度等因素，实际输出仍可能有微小差异。要最大确定性，配合 `seed` 参数使用。

**Q3：国内能用 OpenAI API 吗？有什么替代方案？**

直接调用需要解决网络问题（代理、海外服务器）。国内替代方案：阿里通义千问（DashScope）、百度文心一言、讯飞星火、智谱 GLM、DeepSeek 等。代码写一套，换 API Key 和 endpoint 即可切换。

---

### 自检题

1. System Prompt 和 User Prompt 有什么区别？什么时候该用 System Prompt？
   <details><summary>答案</summary>System Prompt 设定角色和全局规则（"你是XX专家"），优先级最高；User Prompt 是具体问题。当需要约束模型行为（语气、格式、知识范围）时用 System Prompt</details>

2. Token 是什么？为什么它和钱直接相关？
   <details><summary>答案</summary>Token 是模型的计价单位，输入和输出都按 token 收费。1 个汉字≈2 token，1 个英文单词≈1-2 token。长对话历史会累计大量输入 token，成本可能超过输出</details>

3. GPT-3 到 GPT-4 的核心进步是什么？涌现现象怎么理解？
   <details><summary>答案</summary>GPT-4 在推理能力、多语言、多模态上远超 GPT-3。涌现现象：参数量达到某个临界点后，模型突然展现出训练时未明确教的能力（如逻辑推理、代码调试），仿佛"量变引起质变"</details>

---

## 延伸阅读

**推荐资料**（国内可访问）：

- [通义千问 API 文档（阿里云官方）](https://help.aliyun.com/zh/model-studio/) — DashScope 完整文档，含免费额度
- [DeepSeek API 快速上手](https://platform.deepseek.com/) — 国产开源模型 API，价格极低
- [OpenAI API 入门教程（知乎）](https://docs.python.org/3/) — 中文图文教程，从注册到第一个 API 调用

**国外资料**（可能需科学上网）：

- [OpenAI API Documentation](https://platform.openai.com/docs/) — 官方文档，API 参考最权威来源
- [GPT-4 Technical Report](https://arxiv.org/abs/2303.08774) — GPT-4 技术报告
