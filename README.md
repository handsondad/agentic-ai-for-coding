# 🌿 nature-dex

> **Know nature. See more. Grow curious.**

一个面向儿童自然启蒙的 **AI Agent 知识陪伴系统**，帮助孩子认识身边的动物和植物，完成"提问 → 识别 → 学习 → 记录 → 复习"的完整闭环。

---

## 目录

- [项目定位](#项目定位)
- [为什么是 AI Agent](#为什么是-ai-agent)
- [核心能力模块](#核心能力模块)
- [系统架构](#系统架构)
- [Agent 工作流](#agent-工作流)
- [知识库设计](#知识库设计)
- [数据模型](#数据模型)
- [MVP 规划](#mvp-规划)
- [技术栈](#技术栈)
- [儿童场景约束](#儿童场景约束)
- [开发路线](#开发路线)
- [快速开始](#快速开始)
- [目录结构](#目录结构)

---

## 项目定位

nature-dex 不是一个普通的知识库，而是一个 **AI Agent 知识陪伴系统**。

核心目标是让 AI 充当五个角色，陪伴孩子完成完整的自然学习闭环：

| AI 角色 | 负责什么 |
|--------|---------|
| 🌱 **自然老师** | 给孩子讲解动物和植物 |
| 🔍 **观察助手** | 引导孩子去看、去问、去记录 |
| 🗂️ **分类助手** | 帮孩子把看到的东西归类 |
| 📈 **成长陪伴者** | 根据年龄和兴趣持续推荐内容 |
| 👨‍👩‍👧 **家长协同助手** | 给家长补充科学解释和安全提醒 |

---

## 为什么是 AI Agent

普通知识库只能"查"；AI Agent 可以"主动陪孩子学"。

**普通问答**：孩子问"这是什么花？"，系统回答"这是蒲公英……" → 结束。

**Agent 模式**：
```
孩子：这是什么花？

Agent：你看到的是黄色花，还是白色绒球呢？
       它长在草地边还是花坛里？
       你想把它记录进今天的观察日记吗？
       我可以告诉你怎么把它和菊花区分开。
       你上周也看过类似植物，要不要比较一下？
```

这才是 Agent——从"答题器"变成"下一步行动建议器"。

---

## 核心能力模块

### 1. 🔎 识别 Agent

负责"看见的东西是什么"。

- **输入**：图片 / 语音描述 / 文字描述 / 地点 & 季节信息
- **输出**：候选物种 + 置信度 + 区分特征 + 后续确认问题

```
用户上传一张花的图片：
  候选1：蒲公英
  候选2：苦苣菜
  Agent 追问：
    - 花是单独一朵，还是很多小花聚在一起？
    - 叶子是不是贴着地面长？
    - 看到白色绒球了吗？
```

### 2. 🗣️ 儿童讲解 Agent

负责把知识转成孩子能听懂的话。

| 版本 | 示例 |
|-----|-----|
| 成人版 | 蒲公英是菊科多年生草本植物。 |
| 儿童版 | 蒲公英像一朵小太阳，花谢以后会变成白白的绒球，风一吹就飞走啦。 |

支持按年龄分层输出（4–6岁 / 7–9岁 / 10岁+），自动附带"观察点"。

### 3. 👣 观察引导 Agent

负责把"知识"变成"行动"。

```
孩子看到一只蜗牛时，Agent 会说：
  - 你可以先看看它有没有伸出触角。
  - 它爬过的地方会不会留下亮亮的痕迹？
  - 不要用手去拉它的壳哦。
  - 你想记录它是在墙上还是草地上吗？
```

### 4. 📚 知识检索 / 分类 Agent

连接知识库，支持：
- 物种查找和相似物种比较
- 多层分类解释
- 按地点 / 季节 / 颜色 / 习性过滤

### 5. 📓 记录与成长 Agent

负责长期记忆和陪伴。

- 自动生成观察日记
- 定期复习推送
- 展示成长轨迹

```
你已经认识 5 种常见鸟啦。
你总是把麻雀和燕子弄混，我们来玩一个区分小游戏。
这个月你观察最多的是公园里的植物。
```

### 6. 👨‍👩‍👧 家长协同 Agent

孩子和家长使用两套视图：

| 孩子端 | 家长端 |
|-------|-------|
| 简短解释 + 互动提问 + 小任务 | 学术补充 + 安全建议 + 引导提示 + 推荐延伸活动 |

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端层                                    │
│   Web / 小程序 / PWA                                              │
│   聊天 | 图片上传 | 物种卡 | 观察记录 | 成长档案                     │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Orchestration 层                         │
│                                                                   │
│  Router Agent → Identify Agent → Explain Agent                   │
│              → Observe Agent  → Record Agent                     │
│              → Review Agent   → Compare Agent                    │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                       Knowledge Layer                             │
│   结构化物种库 | 多模态媒体库 | 分类标签系统                          │
│   季节/地点索引 | 用户观察记录库                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
┌───────────────────────────────────────┬─────────────────────────┐
│             Model Layer               │       Tool Layer         │
│  通用大模型（对话/解释/规划）             │  species_search()        │
│  多模态模型（图片理解）                  │  identify_from_image()   │
│  Embedding 模型（知识检索）             │  compare_species()       │
│  分类/排序模型（候选物种召回）            │  create_observation()    │
│                                       │  fetch_child_profile()   │
│                                       │  recommend_next_task()   │
│                                       │  safety_check()          │
└───────────────────────────────────────┴─────────────────────────┘
```

---

## Agent 工作流

### 场景 1：孩子拍照问"这是什么？"

```
1. 用户上传图片 + 文本"这是什么？"
2. Router Agent → 判断是"识别请求"
3. 调用识别工具 → 候选物种列表
4. 检索知识库 → 候选资料
5. Agent 决策：直接回答 or 发起澄清问题
6. 输出儿童化解释 + 区分点 + 观察任务 + 是否加入记录
```

输出示例：
> 它很像蒲公英，因为它有黄色的小花，叶子贴近地面。
> 你可以再看看：它之后会不会变成白色的小绒球？
> 要不要把它记到今天的自然观察里？

### 场景 2：孩子说"我今天在小区看到了三只鸟"

```
1. 判断为"记录意图"
2. Agent 追问最少必要信息（物种/位置/是否拍照）
3. 自动生成观察记录草稿
4. 不确定物种 → 挂起为"待确认"
5. 保存到孩子的观察档案
```

### 场景 3：系统主动推荐

```
最近是春天，你家附近公园可以找找蒲公英和柳树新芽。
你还没记录过会飞的昆虫，今天可以试着找蝴蝶或蜻蜓。
```

---

## 知识库设计

知识库的核心定位：**不是"给人看"的，而是"给 Agent 调用"的。**

### 三层结构

#### 1. 结构化层（精确筛选 & 工具调用）

物种核心字段：`id` · `name_zh` · `name_en` · `scientific_name` · `type` · `category` · `habitat` · `season` · `color` · `safety_level` · `observation_difficulty` · `age_level`

#### 2. 文本知识块层（RAG 检索）

每个物种拆成多个 chunk，Agent 按意图取不同 chunk：
- 基础介绍
- 识别特征
- 相似物种区别
- 儿童化描述
- 家长补充
- 安全提醒
- 观察任务建议

#### 3. 多模态标签层（图片检索 & 识别辅助）

标签维度：主色 · 花形 · 叶形 · 羽毛颜色 · 翅膀形态 · 常见背景环境 · 声音标签

---

## 数据模型

### 核心五大实体

```sql
-- 1. 物种
species (
  id, name_zh, name_en, scientific_name, type, category, subcategory,
  summary_child, summary_parent, safety_notice,
  common_locations, common_seasons
)

-- 2. 观察记录
observation_records (
  id, user_id, species_id, identified_status,
  observed_at, location, note_text, image_url, voice_url, weather
)

-- 3. 用户档案
user_profiles (
  id, child_name, birth_year, interests, level,
  home_city, parent_id
)

-- 4. 学习任务
tasks (
  id, title, type, age_range, season, location_type,
  instructions, safety_notice
)

-- 5. 对话状态
conversations (
  id, user_id, session_id,
  current_topic_species_id, current_mode, short_memory_json
)
```

### 推荐存储方案

| 用途 | 技术选型 |
|-----|---------|
| 结构化数据 | PostgreSQL |
| 向量检索 | pgvector / Milvus / Weaviate |
| 图片 / 音频 | 对象存储（S3 / OSS） |
| 会话状态 & 短期记忆 | Redis |
| 全文关键词搜索（可选） | Meilisearch |

---

## MVP 规划

第一版聚焦一个强闭环，不做全能 Agent：

```
上传/提问 → 识别/讲解 → 引导观察 → 保存记录
```

### MVP 功能
1. 物种问答（文字描述 + 检索）
2. 图片识别 + 候选确认（多轮澄清）
3. 观察记录自动生成
4. 基于记录的简单推荐

### MVP 数据范围
先只覆盖一个场景：**小区 + 公园常见 50 种物种**，保证内容质量。

### MVP 页面
- 首页（今日推荐 + 入口）
- 聊天页（核心交互）
- 物种详情页
- 观察记录页
- 我的成长页

---

## 技术栈

### 前端
- **Next.js** + **Tailwind CSS**（移动端优先，可扩展为 PWA）
- 小程序适配层（后续阶段）

### 后端
- **Python FastAPI** + 自定义 tool calling orchestration（MVP 首选，比重框架更稳）
- Agent 框架可选：LangGraph / LlamaIndex / Semantic Kernel

### 模型层
- 对话模型：支持 function calling 的大模型
- 多模态模型：支持图片理解
- Embedding 模型：物种知识检索
- 可选视觉分类模型：初筛候选物种

---

## 儿童场景约束

与普通 AI Agent 的最大差异在于**安全性与表达约束**，属于强制要求，不可妥协：

### ✅ 必须做到
- **置信度表达**：识别结果须说明不确定性
  - ✔ "我猜它像……"
  - ✔ "还需要看一下叶子才能确认"
  - ✔ "不要仅凭这次回答去采摘或食用"
- **安全提醒内建**：涉及野外采摘 / 接触昆虫 / 有毒植物 / 流浪动物，必须规则提醒
- **年龄分层内容**：至少分三层（4–6岁 / 7–9岁 / 10岁+）

### ❌ 禁止做的
- 过度拟人化导致误导：
  - ✗ "花朵故意把虫子骗过来"（误导因果）
  - ✔ "种子像在旅行"（比喻可爱但无误导）
- 无置信度的武断识别
- 省略安全提示（即使孩子没问）

---

## 开发路线

| 阶段 | 目标 |
|-----|-----|
| **第 1 阶段** | 定义物种 schema，录入 30–50 种常见物种，写儿童版 + 家长版描述，建立分类和标签体系 |
| **第 2 阶段** | 基础问答 Agent：检索物种知识，切换儿童/家长版回答，给出观察建议 |
| **第 3 阶段** | 识别与确认：上传图片 → 候选物种 → 多轮澄清 → 保存识别结果 |
| **第 4 阶段** | 观察记录系统：自动生成观察日记，与物种知识绑定，形成用户成长档案 |
| **第 5 阶段** | 推荐与复习：季节/地点任务推荐，自动复习混淆物种，成长轨迹展示 |

---

## 快速开始

### 前置条件

- Python 3.11+
- Node.js 18+（前端）
- Docker（可选，用于本地集成测试）
- [mise](https://mise.jdx.dev/) — 工具版本管理

### 克隆项目

```bash
git clone https://github.com/handsondad/agentic-ai-for-coding.git nature-dex
cd nature-dex
```

### 初始化开发环境

```bash
# 安装依赖
make setup

# 复制环境变量模板
cp .env.example .env
# 编辑 .env，填入大模型 API Key、数据库连接等配置
```

### 启动服务

```bash
# 启动后端
make dev

# 运行测试
make test
```

---

## 目录结构

```
.
├── README.md                          # 本文档
├── WORKFLOW.md                        # Copilot Agent 工作规范
├── Makefile                           # 开发命令集合
├── .env.example                       # 环境变量模板
│
├── .github/
│   ├── copilot-instructions.md        # Copilot 编码规范
│   ├── ISSUE_TEMPLATE/                # Issue 模板
│   └── workflows/                     # CI/CD 流水线
│
├── docs/
│   ├── architecture.md                # 系统架构文档
│   ├── species-schema.md              # 物种数据结构规范
│   └── agent-tools.md                 # Agent Tool 设计文档
│
├── src/
│   ├── agent/                         # Agent 编排逻辑
│   │   ├── router.py                  # Router Agent
│   │   ├── identify.py                # 识别 Agent
│   │   ├── explain.py                 # 儿童讲解 Agent
│   │   ├── observe.py                 # 观察引导 Agent
│   │   ├── record.py                  # 记录 Agent
│   │   └── recommend.py               # 推荐 Agent
│   ├── tools/                         # Agent 可调用工具
│   │   ├── species_search.py
│   │   ├── identify_from_image.py
│   │   ├── compare_species.py
│   │   ├── create_observation.py
│   │   └── safety_check.py
│   ├── knowledge/                     # 知识库管理
│   │   ├── species_store.py
│   │   └── embedding.py
│   ├── memory/                        # 用户记忆 & 会话状态
│   │   └── store.py
│   └── api/                           # API 路由层
│       └── routes.py
│
├── data/
│   └── species/                       # 物种知识库（结构化数据）
│
└── tests/
    ├── unit/
    ├── integration/
    └── conftest.py
```

---

## 许可证

本项目基于 [Apache License 2.0](LICENSE) 开源。
