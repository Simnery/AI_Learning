---
name: 0003_anki-english
description: 创建 Anki 英语学习卡片。支持单词提取、音标、释义、例句，批量/单个导入 Anki。当用户要求创建英语单词卡、导入生词到 Anki、批量制卡时调用。
allowed-tools: Bash Read Write Edit
---

**格式规则**：Skill 是模板，禁止硬编码具体值。deck 名、模型名等由用户配置。

---

# Anki 英语学习卡片

## 环境搭建

1. 安装 **Anki 桌面版**（[apps.ankiweb.net](https://apps.ankiweb.net)，不是 AnkiWeb 网页版）
2. Anki 菜单：**工具 → 附加组件 → 获取插件** → 输入 `2055492159` → 重启 Anki
3. Python 依赖：`pip install requests`（或用 stdlib `urllib` 版本：`anki_tool/` 目录下有 stdlib 版）

**验证**：
```bash
python -c "import requests; r=requests.post('http://localhost:8765', json={'action':'version','version':6}, timeout=3); print('OK, version:', r.json()['result'])"
```

---

## 笔记类型：English Word

### 字段（7 个，固定顺序）

| # | 字段 | 内容 | 说明 |
|---|------|------|------|
| 1 | Word | 单词/术语 | 如 `RAG`、`Prompt Engineering` |
| 2 | Pronunciation | 标准 IPA 音标 | `/ræɡ/`、`/prɒmpt ˌendʒɪˈnɪərɪŋ/` |
| 3 | Audio | 单词发音 | `[sound:word_xxx.mp3]`，TTS 自动生成 |
| 4 | Definition | 英文定义（中文在括号里） | `Retrieval-Augmented Generation（检索增强生成）——LLM 生成前...` |
| 5 | ExampleEN | 英文例句 + 句发音 | `[sound:sent_xxx.mp3] English sentence...` |
| 6 | ExampleCN | 中文翻译 | 纯文本，**无**中文 TTS |
| 7 | Notes | 学习路径、知识图谱关联 | HTML 格式，`<b>` 标签 + `<br>` 换行 |

### 卡片模板（统一格式）

**正面**（Front）：
```html
<div class="card-box">
<div class="box-label">word</div>
<div class="word-big">{{Word}}</div>
{{#Pronunciation}}<div class="ipa">{{Pronunciation}}</div>{{/Pronunciation}}
{{#Audio}}<div class="audio-btn">{{Audio}}</div>{{/Audio}}
</div>
```

**背面**（Back）：
```html
<div class="card-box">
<div class="box-label">word</div>
<div class="word-big">{{Word}}</div>
{{#Pronunciation}}<div class="ipa">{{Pronunciation}}</div>{{/Pronunciation}}
{{#Audio}}<div class="audio-btn">{{Audio}}</div>{{/Audio}}
</div>

<div class="card-box">
<div class="box-label">definition</div>
<div class="box-text">{{Definition}}</div>
</div>

{{#ExampleEN}}<div class="card-box">
<div class="box-label">example sentence</div>
<div class="box-text">{{ExampleEN}}</div>
</div>
{{/ExampleEN}}

{{#ExampleCN}}<div class="card-box">
<div class="box-label">chinese translation</div>
<div class="box-text">{{ExampleCN}}</div>
</div>
{{/ExampleCN}}

{{#Notes}}<hr><div class="notes">{{Notes}}</div>{{/Notes}}
```

**CSS**（样式）：
```css
.card { text-align: center; padding: 12px 0; }
.card-box { background: #f8f9fa; border-radius: 10px; padding: 14px 18px; margin: 8px 12px; text-align: center; }
.box-label { font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.word-big { font-size: 30px; font-weight: bold; color: #1a1a2e; }
.ipa { font-size: 17px; color: #888; margin-top: 4px; }
.audio-btn { margin-top: 8px; }
.box-text { font-size: 16px; color: #333; line-height: 1.7; text-align: left; }
.notes { font-size: 14px; color: #aaa; text-align: left; padding: 0 12px; }
.notes b { color: #666; }
```

### 创建模型的代码（一次性）

```python
requests.post("http://localhost:8765", json={
    "action": "createModel", "version": 6,
    "params": {
        "modelName": "English Word",
        "inOrderFields": ["Word","Pronunciation","Audio","Definition","ExampleEN","ExampleCN","Notes"],
        "css": """<上述 CSS>""",
        "cardTemplates": [{
            "Name": "English Card",
            "Front": """<上述正面模板>""",
            "Back": """<上述背面模板>"""
        }]
    }
})
```

---

## 卡片内容规范

### Definition 格式

**英文在前，中文在括号里**：
- ✅ `Prompt Engineering（提示工程）——通过精心设计输入文本...`
- ✅ `Retrieval-Augmented Generation（检索增强生成）——LLM 生成前...`
- ❌ `提示工程（Prompt Engineering）`（中文在前，禁用）

### IPA 音标规范

**必须用标准 IPA**，禁止自编近似音标：
- ✅ `/prɒmpt/` `/ˌendʒɪˈnɪərɪŋ/` `/həˌluːsɪˈneɪʃən/`
- ❌ `/prompt/` `/en-juh-neer-ing/` `/huh-loo-suh-nay-shun/`

常用 IPA 符号：`ɒ æ ʌ ə ɪ iː ʊ uː eɪ aɪ əʊ θ ð ʃ ʒ tʃ dʒ`

### 缩写词处理（强制规范）

**适用范围**：Word 字段为纯大写且 ≤5 字符的卡片（如 RAG、GPU、API、MCP、LLM）
**排除**：全称词（如 `Prompt Engineering`、`Diffusion Model`）不触发缩写处理——`word == word.upper()` 已自动过滤

**强制格式**（Definition 字段）：
```
[sound:full_xxx.mp3] FullEnglishTerm（中文翻译）——详细解释
```

| 部分 | 说明 | 示例 |
|------|------|------|
| `[sound:full_xxx.mp3]` | 全称 TTS 音频 | 脚本自动生成 |
| `FullEnglishTerm` | 完整英文术语 | `Retrieval-Augmented Generation` |
| `（中文翻译）` | 中文对应术语 | `（检索增强生成）` |
| `——详细解释` | 中文解释 | `——LLM 生成前先从外部知识库检索...` |

**判定规则**：
- ✅ `[sound:full_abc123.mp3] Retrieval-Augmented Generation（检索增强生成）——LLM生成前...`
- ❌ 缺少音频：`Retrieval-Augmented Generation（检索增强生成）——...`
- ❌ 缩写重复：`[sound:xxx] RAGAS（RAG评估框架）——...` → 应去掉前面的 RAGAS，只保留 `[sound:xxx] RAG Assessment（RAG评估框架）——...`
- ❌ 英文全称错误：`AI Agent（智能体）——...` （MCP 的正确定义应是 `Model Context Protocol（模型上下文协议）——...`）

**简写读音规则**：
```python
if word == word.upper() and len(word) <= 5:
    lower = word.lower()
    vowels = sum(1 for c in lower if c in 'aeiouy')
    tts_text = lower if vowels >= 2 else ' '.join(word)
    # RAG→rag (读词), GPU→g p u (逐字母), MCP→m c p (纯辅音)
```

**修复工具**：
- 批量修复音频：`python scripts/anki_fix_acronyms.py`（内置 KNOWN 映射表，自动用正确全称下载 TTS）
- 修复定义格式：编辑 `cards/chX_cards.json`，找到对应卡片，修改 Definition 字段
- ⚠️ 关键是 TTS 文本必须是全称（如 `Model Context Protocol`），不能是缩写（如 `MCP`）——否则 TTS 会逐字母拼读
- 单卡修复：`python scripts/anki_edit.py WORD --field Definition "[sound:xxx.mp3] FullTerm（中文）——解释"`

### Notes 内容标准

- **长度**：≥500 字，AI 小白可直接当学习笔记
- **格式**：HTML 标签，`<b>` 加粗标题，`<br>` 换行
- **结构**：
  ```
  <b>学习路径</b><br>知识图谱章节定位 + 为什么重要
  <b>核心概念</b><br>深层技术解释（非一句话定义）
  <b>关键要点</b><br>量化数据、对比表格、具体步骤
  <b>延伸节点</b><br>交叉引用其他章节
  ```
- **数据源**：JSON 文件是唯一权威数据源。编辑 JSON → `anki_sync.py` 同步 Anki`

### 例句音频

- **ExampleEN**：必须带 `[sound:...]` 前缀（整句英文朗读）
- **ExampleCN**：纯文本，**不加**中文 TTS

---

## 发音音频（TTS）

双源兜底：Google TTS（主）+ 有道词典（备）。含 3 次重试 + 指数退避。

```python
import hashlib, base64, time

def download_tts(text, lang="en", retries=2):
    # Provider 1: Google
    for attempt in range(retries):
        try:
            qs = urllib.parse.urlencode({'ie':'UTF-8','client':'tw-ob','tl':lang,'q':text[:200]})
            url = f'https://translate.google.com/translate_tts?{qs}'
            req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                if len(data) > 100:  # valid audio
                    time.sleep(1.5)
                    return data
        except: time.sleep(1)
    # Provider 2: Youdao fallback
    qs = urllib.parse.urlencode({'audio': text[:100], 'type': 2})  # type=2 American
    url = f'https://dict.youdao.com/dictvoice?{qs}'
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read()

def store_audio(text, prefix):
    safe = prefix[:20].replace(' ', '_').replace("'", "")
    h = hashlib.md5(text.encode()).hexdigest()[:6]
    fname = f'{safe}_{h}.mp3'
    data = download_tts(text)
    anki('storeMediaFile', filename=fname, data=base64.b64encode(data).decode('utf-8'))
    return f'[sound:{fname}]'
```

**智能缩写 TTS**：
```python
if word == word.upper() and len(word) <= 5:
    lower = word.lower()
    vowels = sum(1 for c in lower if c in 'aeiouy')
    tts_text = lower if vowels >= 2 else ' '.join(word)  # RAG→rag (读词), AIGC→A I G C (逐字母)
else:
    tts_text = word
```

---

## 强制工作流（每次必须按此执行，禁止跳过步骤）

### 工具清单

| 脚本 | 用途 | 运行位置 |
|------|------|---------|
| `scripts/anki_regen.py` | 批量导入 JSON→Anki。默认增量。⚠️ `--full` 删光重建（危险，丢手动修复） | `cd anki_tool/` |
| `scripts/anki_sync.py` | 同步 JSON 字段到 Anki（不动音频）`--word X` 只同步指定卡 | `cd anki_tool/` |
| `scripts/anki_edit.py` | 编辑单卡任意字段 | `cd anki_tool/` |
| `scripts/anki_add.py` | 交互式添加单卡 | `cd anki_tool/` |
| `scripts/anki_fix_acronyms.py` | 批量修复缩写词全称音频 | `cd anki_tool/` |
| `scripts/anki_model.py` | 查看/管理笔记类型 | `cd anki_tool/` |

**目录结构**：`templates/`(模板) | `cards/`(数据源,git跟踪) | `scripts/`(工具,git跟踪) | `export/`(apkg,gitignore; zip,git跟踪)

**核心原则**：
- `cards/chX_cards.json` 是唯一数据源。**禁止**直接改 Anki 里的内容
- 每次修改必须是：编辑 JSON → 验证 → 同步 Anki
- 同步用 `anki_sync.py`（不动音频），不用 `anki_regen.py --full`（会重下 TTS）
- **一个 Word 只能出现在一个牌组**中。跨章重复时保留最早章节（ch1>ch2>...>ch6），从其余 JSON 和 Anki 中删除

---

### 工作流 1：修复单张卡片

> 触发：用户要求修复某张卡的音频、释义、例句、音标

```
1. 确认目标：卡片 Word 名称 + 要改的字段 + 所属牌组
   ⚠️ 同一 Word 可能存在于多个牌组（如 BM25 在 ch1/ch2/ch5/ch6）
   查所属牌组：python -c "import json,urllib.request;r=json.loads(urllib.request.urlopen(urllib.request.Request('http://localhost:8765',data=json.dumps({'action':'findNotes','version':6,'params':{'query':'Word:XXXX'}}).encode(),headers={'Content-Type':'application/json'})).read());print(r['result'])"
   或用 anki_edit.py --list 查看
2. 确认要操作哪个牌组的版本（通常选最相关章节的）
3. 查当前状态：python scripts/anki_edit.py WORD --list
4. 执行修改（**核心原则：JSON 是唯一数据源**）：
   a. 定位 JSON：打开 cards/chX_cards.json，找到该 Word 对应的条目
   b. 修改内容：
      - 改 Notes    → 直接编辑 Notes 字段
      - 改 Definition → 修改 Definition 字段文本
      - 改 Pronunciation → 修改 Pronunciation 字段
      - 改 ExampleEN/ExampleCN → 修改对应字段（改 ExampleEN 后需重新生成 TTS）
   c. 验证 JSON：python -c "import json; json.load(open('cards/chX_cards.json'))"
   d. 同步 Anki：python scripts/anki_sync.py cards/chX_cards.json Notes --word WORD
      如果需要同时改多个字段：python scripts/anki_sync.py cards/chX_cards.json Notes Definition Pronunciation --word WORD
   e. 音频特殊处理（唯一例外）：音频由 TTS 自动生成，JSON 中 Audio="" 表示需要生成
      - 只需修复音频 → python scripts/anki_edit.py WORD --audio ""   （直接重新下载 TTS，不动 JSON）
      - 改了 ExampleEN 需要新句子音频 → python scripts/anki_edit.py WORD --example "新例句" （自动 TTS + 写回 JSON）
5. 确认结果：在 Anki 浏览中按牌组过滤验证卡片内容已更新
```

### 工作流 2：批量修改 Notes（深度学习化）

> 触发：用户要求扩充 Notes 内容

```
1. 确认范围：修改整章？或指定某几张卡？
2. 定位牌组：确认要修改的 cards/chX_cards.json（ch1-ch6，注意跨章重复）
3. 编辑 JSON：用 IDE 打开文件，找到目标卡片的 Notes 字段，按要求修改
4. 验证 JSON：python -c "import json; json.load(open('cards/chX_cards.json'))"  ← 必须通过
5. 同步 Anki：python scripts/anki_sync.py cards/chX_cards.json Notes
   - 整章同步：python scripts/anki_sync.py cards/chX_cards.json Notes
   - 单卡同步（只影响到对应牌组）：python scripts/anki_sync.py cards/chX_cards.json Notes --word LLM
6. 验证：在 Anki 浏览中按牌组过滤，抽查 2-3 张卡片确认生效
```

**Notes 编辑规范**：
- 长度 ≥500 字，使用 `<b>` 加粗标题 + `<br>` 换行
- 结构：`<b>学习路径</b>` → `<b>核心概念</b>` → `<b>关键要点</b>` → `<b>延伸节点</b>`
- 禁止使用 ASCII `"` 引号（用 `「」` 替代）。写完后用 `json.load()` 验证
- 内容必须来自知识图谱原文，不可自行编造

### 工作流 3：添加新卡片

> 触发：用户要求添加新单词

```
1. 确定归属：属于哪个牌组？(01~06)。先查是否已存在于其他牌组（跨章重复）→ 已有则询问用户要添加到哪个
2. 编辑 JSON：打开 cards/chX_cards.json，在对应位置插入新条目
   模板：{"Word":"","Pronunciation":"","Audio":"","Definition":"","ExampleEN":"","ExampleCN":"","Notes":""}
3. 填写内容：IPA 音标、英文在前释义、中英对照例句、≥500字笔记
4. 验证 JSON：python -c "import json; json.load(open('cards/chX_cards.json'))"
5. 导入 Anki：python scripts/anki_regen.py cards/chX_cards.json --deck "0X-牌组名"
   （增量模式：只导入新增的，已有卡不动）
6. 验证：在 Anki 中确认新卡片出现
```

### 工作流 4：批量导入整章

> 触发：用户要求导入一整章卡片

```
1. 检查 Anki：Anki 桌面版是否启动？AnkiConnect 是否可达？
2. 验证 JSON：python -c "import json; json.load(open('cards/chX_cards.json'))"
3. 执行导入：python scripts/anki_regen.py cards/chX_cards.json --deck "0X-牌组名"
   - 默认增量：跳过已存在的卡片，只导入新的
   - 全量覆盖：加 --full 参数（会重下所有 TTS，慎用）
4. 展示结果：成功 N 张 / 跳过 M 张 / 失败 K 张
5. 导出备份：python scripts/anki_model.py  # 检查牌组
```

### 工作流 5：修复缩写词定义（批量或单卡）

> 触发：缩写卡片缺少全称音频、或定义格式不符合规范

**格式标准**（见「缩写词处理」章节）：Definition = `[sound:full_xxx.mp3] FullEnglishTerm（中文）——解释`

```
1. 定位缩写卡：python scripts/anki_fix_acronyms.py --dry-run（预览所有待修复）
2. 单卡修复：
   a. 找到卡片 → 检查 Definition 格式是否正确
   b. 如果英文全称错误或缺漏 → 编辑 cards/chX_cards.json，修正 Definition
      ✅ [sound:full_xxx.mp3] Model Context Protocol（模型上下文协议）——...
      ❌ AI Agent（智能体）——...  （MCP 的正确全称是 Model Context Protocol）
   c. 验证 JSON → 同步 Notes：python scripts/anki_sync.py cards/chX_cards.json Notes
3. 批量修复音频：python scripts/anki_fix_acronyms.py（自动下载全称TTS，添加到已正确格式化的定义前）
4. 验证：在 Anki 浏览中查看 MCP 等缩写卡，确认全称发音正常
```

### 工作流 6：更新笔记类型（添加新字段）

> 触发：需要给笔记类型增加字段（如 Etymology、Tag）

```
1. 查看当前字段：python scripts/anki_model.py "English Word"
2. 添加字段：python scripts/anki_model.py "English Word" --add FieldName
3. 手动更新模板：Anki → 浏览 → 卡片... → 在模板中插入 {{FieldName}}
4. 更新 JSON 数据源：在每个卡片数据中添加对应字段
5. 更新 Skill 文档：在本文件中记录新字段
6. 更新备份：python scripts/anki_model.py "English Word" 确认字段列表
```

### 工作流 7：压缩导出文件（便于上传 & git 追踪）

> 触发：apkg 文件生成或更新后，压缩为单个 zip 便于上传和版本管理

```
1. 检查 apkg 文件：ls -lh anki_tool/export/*.apkg
2. 压缩（PowerShell）：
   powershell -Command "Compress-Archive -Path '{项目根}/anki_tool/export/*.apkg' -DestinationPath '{项目根}/anki_tool/export/anki_6chapters_all.apkg.zip' -CompressionLevel Optimal"
3. 验证压缩包：ls -lh anki_tool/export/anki_6chapters_all.apkg.zip
4. 提交追踪：git add anki_tool/export/anki_6chapters_all.apkg.zip
```

> apkg 本身已是 zip 格式，压缩率接近 0%，仅起合并归档作用。

---

## 前置检查（每次操作前）

```bash
# 1. Anki 运行中？
curl -s http://localhost:8765 > /dev/null || echo "请启动 Anki"

# 2. 模型存在？
python scripts/anki_model.py "English Word" | head -3

# 3. JSON 有效？
python -c "import json; json.load(open('cards/chX_cards.json'))" && echo "OK"
```

## TTS 双源兜底

Google TTS（主，智能缩写：含 2+ 元音→读词如 RAG→/ræɡ/，纯辅音→逐字母如 AIGC→"A I G C"）+ 有道词典（备）。含 3 次重试 + 1.5s 间隔。

## 常见问题

| 问题 | 解决 |
|------|------|
| AnkiConnect 连不上 | Anki 桌面版启动？插件安装？端口 8765 被占？ |
| 卡片正面空白 | modelName 是否匹配？field 名称大小写是否正确？ |
| TTS 读缩写为逐字母 | 用智能判断（元音数）自动处理 |
| 模板更新不生效 | `updateModelTemplates` 需用 dict 格式（非 list） |
| JSON 导入报错 | 控制字符或 CJK 引号问题 → 用 `json.dump()` 重写 |
| 增量模式跳过已存在卡 | 默认行为。用 `--full` 强制全量重建（重下 TTS） |
