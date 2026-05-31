# 1.1.3 多模态前沿：从Agent构建到视频AIGC

> 1.1 理论知识 > 1. AI大模型基础

---

## 核心概念

### 什么是多模态

**模态（Modality）** 指的是信息的形式：文字是一种模态，图片是另一种，声音、视频又各是一种。人类天生就是多模态的——我们听+看+读+说同时进行。**多模态 AI** 就是让模型也能同时理解和生成多种形式的信息。

| 模态 | 输入（理解） | 输出（生成） |
|------|------------|------------|
| 文本 | ✅ GPT、文心一言 | ✅ 所有 LLM |
| 图像 | ✅ GPT-4V、Gemini | ✅ DALL-E、Midjourney、Stable Diffusion |
| 音频 | ✅ Whisper、通义听悟 | ✅ TTS 语音合成 |
| 视频 | ✅ Gemini、GPT-4V | ✅ Sora、Kling（可灵）、Runway |

### 多模态 Agent 是什么

多模态 Agent = 普通 Agent（思考+行动循环）+ 多模态感知能力。它不仅读文字，还能"看"图片、"听"音频。比如：你发一张冰箱内部的照片，它能分析里面有什么食材，然后推荐菜谱。

### 视频 AIGC 是什么

**AIGC（AI Generated Content）** 是用 AI 生成内容。**视频 AIGC** 特指用 AI 从零生成视频——你输入一段文字描述（"一只猫在月球上跳舞"），AI 输出一段视频。代表模型：OpenAI Sora、快手可灵（Kling）、Runway Gen-3。

### 为什么重要

多模态是 AI 进化的必经之路。人类 80% 的信息获取靠视觉，如果 AI 只能读文字，它永远是"半盲"的。视频 AIGC 更是正在重塑内容创作行业——广告、影视、教育都在被颠覆。

### 前置知识

- [1.1.2 Agent 基础](1-1-2_Agent从可控性到自主反思.md)（了解 ReAct 框架）
- 后续：[2.3.4 视觉与多模态模型](../../02_AI应用技术/2-3_模型训练与微调理论知识+案例详解+实操/2-3-4_视觉与多模态模型.md)

---

## 原理讲解

### 多模态 Agent 的构建要点

**核心思路**：把视觉/听觉能力封装成工具（Tool），让 Agent 像调用搜索工具一样调用"看图工具"。

```
用户发来一张图片："这辆二手车值多少钱？"
                    │
      ┌─────────────▼─────────────┐
      │ 多模态 Agent               │
      │                           │
      │ Thought: 需要分析图片内容   │
      │ Action: 调用视觉模型看图    │
      │   ↓                       │
      │   视觉模型返回：             │
      │   "2018款丰田卡罗拉，白色，   │
      │    前保险杠有划痕，里程约8万km" │
      │   ↓                       │
      │ Action: 搜索二手车行情      │
      │   ↓                       │
      │ Final Answer: "根据图片和   │
      │   市场行情，估价约6-8万元"    │
      └───────────────────────────┘
```

**三个关键设计**：

| 设计点 | 说明 |
|--------|------|
| 统一输入分发 | 不同模态（图、音、视频）先经各自编码器处理后统一送入 LLM |
| 工具封装 | 视觉模型、ASR（语音识别）、TTS（语音合成）各封装为独立 Tool |
| 结果融合 | Agent 无需关心数据来自哪种模态，统一推理 |

### 视频检索原理

视频检索 = 把视频变成可搜索的文本 + 向量。

```
原视频（30分钟）
    │
    ├─→ 抽关键帧（每秒1帧 → 1800张图片）
    │      ↓
    │   图片用 CLIP 模型转向量 → 可"以图搜视频"
    │
    ├─→ 语音转文字（ASR → 逐句文本）
    │      ↓
    │   文本用 Embedding 转向量 → 可"搜说话内容"
    │
    └─→ OCR 识别画面中的文字（字幕、PPT、路牌等）
           ↓
        文本也转向量 → 可"搜画面中的字"
```

三者合并存入向量数据库，用户搜索时从三个维度同时匹配，找到最相关的视频片段。

### 视频生成核心原理（扩散模型）

> ⚠️ 本节为概念了解，视频生成需要大量 GPU 资源，暂无代码示例。

**扩散模型** 的思路是"先破坏，再重建"：

```
训练阶段：                       推理阶段：
清晰图片 → 逐步加噪声 → 纯噪声    纯噪声 → 逐步去噪 → 生成图片
  🖼️   →  🌫️   →  🌫️🌫️  →  ⬜     ⬜  →  🌫️🌫️  →  🌫️  →  ✨（新图）
```

视频生成的额外挑战：不仅每帧要真实，**帧与帧之间还要连贯**（时序一致性）。

**主流方案**：

| 模型 | 厂商 | 特点 |
|------|------|------|
| Sora | OpenAI | 基于 Diffusion Transformer，生成 1 分钟视频，物理规律理解好 |
| Kling（可灵） | 快手 | 国内可用，1080p，最长 2 分钟，支持图生视频 |
| Runway Gen-3 | Runway | 电影级画质，适合专业创作，支持多模态控制 |

---

## 代码实战

### 1. 多模态 Agent：看图分析

```bash
pip install openai
```

```python
# multimodal_agent.py — 用 GPT-4V 实现看图分析
import openai
import base64

client = openai.OpenAI()

def analyze_image(image_path: str, question: str) -> str:
    """将图片编码为 base64，发送给多模态模型分析"""
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    
    response = client.chat.completions.create(
        model="gpt-4o",  # 支持视觉的模型
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {"type": "image_url", 
                 "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
            ]
        }]
    )
    return response.choices[0].message.content

# 使用示例（需要一张本地图片 test.jpg）
# result = analyze_image("test.jpg", "这张图片里有什么？详细描述")
# print(result)
```

### 2. 视频检索概念演示：用关键帧 + Embedding 搜索

```bash
pip install openai sentence-transformers numpy
```

```python
# video_search_demo.py — 视频检索概念演示
import numpy as np
from sentence_transformers import SentenceTransformer

# 加载 embedding 模型（轻量、中文友好）
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')

# 模拟视频的关键帧描述（实际项目中这些来自 ASR + 视觉模型）
video_segments = [
    {"time": "00:00", "text": "今天我们来学习 Python 的基础语法"},
    {"time": "02:30", "text": "变量和数据类型：整数、浮点数、字符串"},
    {"time": "05:00", "text": "条件判断 if-else 的使用方法和注意事项"},
    {"time": "08:15", "text": "循环语句 for 和 while 的区别"},
    {"time": "12:00", "text": "函数定义：def 关键字和参数传递"},
]

# 将所有片段转为向量
descriptions = [seg["text"] for seg in video_segments]
embeddings = model.encode(descriptions)

# 用户搜索
query = "怎么用 if else 判断条件？"
query_embedding = model.encode([query])[0]

# 计算余弦相似度
similarities = np.dot(embeddings, query_embedding) / (
    np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
)

# 找到最匹配的片段
best_idx = np.argmax(similarities)
print(f"搜索结果：{video_segments[best_idx]['time']} — {video_segments[best_idx]['text']}")
print(f"相似度：{similarities[best_idx]:.3f}")
# 预期输出：05:00 — 条件判断 if-else 的使用方法和注意事项
```

### 3. 关键代码解读

| 代码段 | 设计意图 |
|--------|---------|
| `base64` 编码图片 | 多模态 API 通过 HTTP 传输图片，base64 是通用方案；生产环境可用 URL 直传 |
| `data:image/jpeg;base64,` 前缀 | URL 内嵌图片的标准格式，告诉 API "这是一张 JPEG 图片" |
| `BAAI/bge-small-zh-v1.5` | 中文 embedding 模型，512 维，速度快；生产环境可用 `bge-large` 提高精度 |
| 余弦相似度手算 | 展示原理；实际项目用 `sklearn.metrics.pairwise.cosine_similarity` 更方便 |

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

### 当前局限（视频生成）
- **时序一致性难保证**：生成 10 秒以上视频时，前后帧可能出现物体变形、消失
- **算力成本极高**：Sora 级别的视频生成需要数百块 H100 GPU 集群
- **物理规律理解弱**：AI 生成的视频可能违反重力、光影等物理常识
- **国内可用性**：Sora 未对国内开放，优先关注可灵（Kling）、即梦（Dreamina）等国内方案

### 下一步学什么
- [视觉与多模态模型（2.3.4）](../../02_AI应用技术/2-3_模型训练与微调理论知识+案例详解+实操/2-3-4_视觉与多模态模型.md) — 深入 CLIP、ViT 等多模态模型架构
- [图像识别技术与缺陷检测（3.5.3）](../../03_AI框架及工具平台/3-5_PyTorch与视觉检测/3-5-3_图像识别技术与缺陷检测.md) — 从原理到工业落地

### 工业界趋势
- **多模态 RAG**：不仅检索文本，还检索图片、表格、视频片段，综合生成答案
- **端侧多模态**：苹果、高通在推本地运行的小型多模态模型（隐私、低延迟）
- **视频生成 + Agent**：Agent 负责写脚本、分镜、审核，AI 负责生成画面，人只做最终决策

---

## 常见问题

**Q1：多模态模型和普通 LLM 有什么区别？**

普通 LLM 只能处理文本（文字进文字出）。多模态模型能同时处理文本+图片+音频+视频。关键在于多模态模型内部有一个"翻译层"，把不同模态的数据都转成统一的向量表示，再一起推理。

**Q2：我想自己做视频生成，需要什么条件？**

最低门槛：一张 RTX 4090（24GB 显存）可跑开源方案如 AnimateDiff、CogVideoX（短视频）。更高要求：多卡集群 + LoRA 微调。实用建议：先用快手可灵、即梦等国内 API 体验，确认需求后再考虑本地部署。

**Q3：视频检索和普通文本检索有什么不同？**

视频检索需要**多路召回**：文本路（ASR 语音转文字）+ 视觉路（关键帧 CLIP 向量）+ 元数据路（标题、标签）。三路结果合并排序，比纯文本检索复杂得多。

---

### 自检题

1. 为什么多模态 Agent 需要把视觉封装成 Tool，而不是直接让模型"看图"？
   <details><summary>答案</summary>Agent 需要显式决策何时调用什么能力。把视觉封装成 Tool 后，Agent 可以用 ReAct 框架决定"现在该看图片了"，控制调用时机和成本</details>

2. 视频检索的"多路召回"指哪几路？分别解决什么问题？
   <details><summary>答案</summary>文本路（ASR转文字→语义搜索）、视觉路（关键帧→以图搜图）、元数据路（标题标签→关键词匹配）。三者互补：文本路找"说了什么"，视觉路找"出现什么画面"，元数据路做精确匹配</details>

3. 扩散模型的"加噪→去噪"训练方式有什么巧妙之处？
   <details><summary>答案</summary>不需要成对数据（不需要"原图+精美图"）。只需要大量真实图片，随机加噪声后训练模型学会"去噪"，相当于模型学会了图片的"本质特征"——知道一只猫长什么样，才能从噪声中恢复出猫</details>

---

## 延伸阅读

**推荐资料**（国内可访问）：

- [多模态大模型综述（知乎）](https://docs.python.org/3/) — 中文综述，覆盖 GPT-4V、Gemini、文心一图等主流多模态模型
- [CLIP 论文解读（B站）](https://www.bilibili.com/video/BV1SL4y1s7jH) — 视频讲解 CLIP 模型原理，多模态入门必看
- [快手可灵官网](https://kling.kuaishou.com/) — 国内可直接使用的视频生成工具，体验 AIGC 最直接的方式

**国外资料**（可能需科学上网）：

- [Sora 技术报告](https://openai.com/research/video-generation-models-as-world-simulators) — OpenAI Sora 官方技术报告，了解前沿视频生成思路
- [Gemini 多模态能力展示](https://deepmind.google/technologies/gemini/) — Google DeepMind 的多模态旗舰模型
