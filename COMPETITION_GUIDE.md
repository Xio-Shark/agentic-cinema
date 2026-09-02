# 🎬 比赛全景与通关指南 (Competition Master Guide)
### *Google Cloud: Agentic Cinema - The Blockbuster Hackathon*

---

## 一、赛事基本概况与关键节点

- **主办方**：Google Cloud
- **联合生态伙伴**：Grafana Labs, ClickHouse, Parallel, IBM, Replit
- **承办平台**：Devpost
- **官方主页**：[https://agentic-cinema.devpost.com](https://agentic-cinema.devpost.com)
- **总奖金池**：**$75,000 USD**（分为 3 个对等的生态伙伴专项赛道，每个赛道奖金池 **$25,000**）
- **核心截止时间**：
  - **项目提交截止**：**2026年9月10日 05:00 AM (GMT+8)** / 9月9日 5:00 PM (PT)
  - **评审周期**：2026年9月10日 ~ 9月24日
  - **获胜公布**：2026年9月30日前后

---

## 二、官方主题与隐喻解构 (Theme Deconstruction)

本次黑客松的主题为 **“Agentic Cinema: Lights. Camera. Code.”**，要求开发者跳出“单行代码开发”思维，转而以**“好莱坞大片制片厂（Cinema Studio）”**为架构隐喻，利用 **Gemini Enterprise Agent Platform** 与 **托管 MCP (Model Context Protocol)** 构建企业级多智能体协同系统：

| 电影制片隐喻角色 | 对应企业系统架构职责 | 本项目 CineOps Studio 落地实现 |
| :--- | :--- | :--- |
| **Director (总导演)** | 系统编排中枢，统揽全局，将大任务拆解为分镜头剧本并调度下属。 | **Director Agent**：基于 Gemini 2.5 Pro，接收用户目标或系统告警，分解为分镜（Scenes），驱动工作流。 |
| **Technical Producer (技术制片)** | 数据管道与外部工具连接者，负责摄影机、特效、灯光等现场数据。 | **Observability Producer**：通过标准 MCP 协议直连 **Grafana Cloud**，实时调取 Prometheus、Loki 与 Tempo。 |
| **Studio Head (制片厂安全总监)** | 掌控 IAM 权限、合规审查、预算与最终上映发布。 | **Studio Head Agent**：负责高危动作安全拦截、审批鉴权，并生成电影级制片复盘审计报告。 |

---

## 三、赛道选定与战术分析 (Track Strategy)

### 🎯 锁定赛道：**Grafana Labs Track ($25,000)**

#### 1. 为什么选择 Grafana Labs 赛道？
1. **天然的数据资产优势**：团队现有 Grafana Cloud 实例已激活 **12 个核心数据源**（包含 Prometheus、Loki、Tempo、Pyroscope、k6 等），无需冷启动，可直接接入真实企业级遥测数据流。
2. **MCP 与可观测性极其契合**：可观测性排障本质上是“多轮推理 + 工具调用（Tool Calling）”的标准场景。通过 MCP Server 向 Agent 暴露 PromQL、LogQL 与链路追踪接口，能完美展现 MCP 协议的价值。
3. **竞争隔离优势**：Devpost 采用分赛道独立评审机制，选择 Grafana Track 避开了通用赛道的泛 AI 包装，直击企业级 SRE / DevOps 痛点，极具说服力。

---

## 四、评审维度与满分攻防策略 (Judging Criteria & Tactics)

| 评审维度 | 权重 | 评委关注点 | 本项目高分攻防策略 |
| :--- | :---: | :--- | :--- |
| **1. Gemini 深度集成<br/>(Gemini Integration)** | **25%** | 是否深度调用 Gemini 多模态、结构化输出、系统提示词与 Agent 编排特性，而非仅当作简单 Chatbot。 | • 使用 Gemini 2.5 Pro 作为 Director，利用结构化 JSON Schema 严格输出 Storyboard 分镜。<br/>• 结合 Gemini 长上下文与推理链，生成深度根因分析与代码级修复建议。 |
| **2. 伙伴技术结合度<br/>(Partner Technology)** | **25%** | 是否规范、巧妙地集成了 Grafana Cloud 与 MCP 协议。 | • 实现标准符合 MCP 协议规范的 Grafana MCP Server。<br/>• 覆盖 Prometheus (指标)、Loki (日志)、Pyroscope (性能火焰图) 多维联动。 |
| **3. 多 Agent 协同与编排<br/>(Multi-Agent Orchestration)** | **25%** | 智能体之间是否有明确的角色分工、状态机流转、事件通信与异常自愈。 | • 建立 Director $\to$ Observability $\to$ Studio Head 闭环协同机制。<br/>• 提供结构化事件流（Event Stream）与分镜看板，每一步决策透明可追溯。 |
| **4. 演示效果与实用价值<br/>(Production Quality & Demo)** | **25%** | 解决真实企业痛点；UI 体验震撼；视频与文档专业完备。 | • 打造好莱坞电影质感的 CineOps 深色 Web 控制台（带呼吸灯、场记板与实时时间线）。<br/>• 录制 2.5 分钟高节奏英文解说视频，辅以可一键复现的在线/本地 Demo。 |

---

## 五、最终交付材料清单 (Submission Checklist)

在 **2026年9月10日 05:00 (GMT+8)** 截止前必须完成以下 4 项交付：

- [ ] **1. 公开 GitHub 开源代码仓库**
  - 规范的开源许可证（MIT/Apache-2.0）；
  - 清晰完备的 README 与架构图；
  - 干净的代码目录（遵循胶水架构：`services/`, `libs/`, `external/`）。
- [ ] **2. 2~3 分钟英文演示视频 (Video Pitch)**
  - 上传至 YouTube (Unlisted/Public) 或 Loom；
  - 包含：痛点引入 (30s) $\to$ 架构与 MCP 揭秘 (45s) $\to$ 电影级 Live Demo 演示 (60s) $\to$ 商业价值与总结 (15s)。
- [ ] **3. 在线可交互演示 / 快速复现指南 (Live Demo / Replay Guide)**
  - 提供一键启动脚本或在线 Web URL；
  - 具备 Deterministic Demo 模式，确保评审专家无需复杂配置即可秒级体验完整剧本。
- [ ] **4. Devpost 文本申报材料**
  - 故事化文案：Inspiration, What it does, How we built it, Challenges we ran into, Accomplishments, What's next.
