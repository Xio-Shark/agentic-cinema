# 🎨 CineOps Studio: 电影级控制台 UI/UX 设计规范
### *Cyber-Cinema Dark Theme, Storyboard Layout & Motion Design Spec*

---

## 一、视觉设计语言与调色盘 (Visual Language & Palette)

为了呼应 **“好莱坞大片制片厂（Cinema Studio）”** 隐喻，UI 严格遵循**好莱坞监看室（Director Monitor）与专业调色台**的工业美学，避免常见的泛滥紫蓝渐变模板，采用纯粹、沉浸、高对比度的专业深色系：

```
[UI 调色盘规范]
• 背景主色 (Studio Floor)       : #0B0F17 (bg-slate-950 / 深空玄黑)
• 面板底色 (Monitor Glass)       : #131B2A / #1E293B (bg-slate-900 / 磨砂质感)
• 导演高亮金 (Hollywood Amber)   : #F59E0B / #FBBF24 (amber-500/400 - 核心主焦点)
• 场记动作蓝 (Slate Cyan)        : #06B6D4 / #38BDF8 (cyan-500/sky-400 - 工具与网络流)
• 安全放行绿 (Greenlight Emerald): #10B981 / #34D399 (emerald-500 - 自愈与正常指标)
• 警报警戒红 (Red Carpet Alert)  : #EF4444 / #F87171 (red-500 - 故障与安全拦截)
• 文字主色 (Director Script)    : #F8FAFC (slate-50 / 极高可读性)
• 次级辅助色 (Camera Metas)      : #94A3B8 (slate-400 / 状态与时间戳)
```

---

## 二、界面整体三栏布局 (Three-Column Studio Layout)

```
+-------------------------------------------------------------------------------------------------------+
|  🎬 CineOps Studio  |  Director: Gemini 2.5 Pro  |  Track: Grafana Cloud  |  [Live Mode / Replay]   |
+-------------------------------------------------------------------------------------------------------+
|   [左栏: 300px] 剧组与场记板   |          [中栏: Flex-1] 电影分镜与实时行动流          |  [右栏: 380px] 可观测取证与报告  |
|                               |                                                      |                                |
|  📋 场记板 (Slate Header)      |  🎞️ 分镜剧本 (Storyboard Scenes: 1 → 2 → 3)          |  📊 Grafana Live Telemetry     |
|  • Production ID: #SCENE-08   |     [Scene 1: Anomaly] → [Scene 2: Loki] → [Scene 3] |  • Prometheus Error Rate (42%) |
|  • Director: READY            |                                                      |  • Loki Traceback Card         |
|  • Take: #1 (Action!)         |  📜 实时场记行动流 (Action Timeline)                    |  • Pyroscope Flame Profile     |
|                               |     [21:40:12] 🎬 Director: 拆解分镜任务...           |                                |
|  👥 剧组 Agent 状态 (Crew)    |     [21:40:13] 📊 Obs Producer: 调用 grafana_mcp...   |  📜 制片总结报告 (Wrap Report)  |
|  • 🎬 Director [Active 🟢]    |     [21:40:14] 🔌 MCP Result: 捕获连接池泄漏 (20/20)   |  • Root Cause: Pool Leak       |
|  • 📊 Obs Producer [Busy 🟡]  |     [21:40:16] 🛡️ Studio Head: 安全审查 APPROVED!     |  • Self-Healing: Executed ✅   |
|  • 🛡️ Studio Head [Idle ⚪]   |                                                      |  • Time to Recovery: 28.4s     |
|                               |  ⚡ [触发场景 A: 微服务雪崩]  [触发场景 B: Agent 自检]   |  • Audit Signature: Verified   |
+-------------------------------------------------------------------------------------------------------+
```

---

## 三、核心组件与交互规范 (Component Specifications)

### 1. 📋 场记板头部组件 (`ProductionSlate`)
- **视觉**：黑白相间的电影场记板条纹（Clapperboard pattern），搭配醒目的当前场次 `SCENE 1 / TAKE 1`；
- **状态指示器**：顶部常驻当前排障时钟（Timecode: `00:00:28:14`）与状态呼吸灯（`LIVE RECORDING 🔴` / `WRAPPED 🟢`）。

### 2. 🎞️ 分镜任务看板 (`StoryboardDeck`)
- **卡片式横向流转**：将整场排障分为 3~4 个分镜卡片；
- **三种视觉状态**：
  - `UPCOMING`（半透明暗色，带虚线边框）；
  - `SHOOTING / IN PROGRESS`（琥珀金流光边框，内部显示当前负责 Agent 的打字机思考过程）；
  - `WRAPPED / COMPLETED`（翡翠绿边框，显示取得的核心证据与耗时）。

### 3. 📜 电影级实时行动流 (`ActionTimeline`)
- **对话气泡与工具调用的视觉隔离**：
  - **Agent 思考 (Thought)**：斜体、半透明、带脑电波/打字机动效；
  - **MCP Tool 调用**：等宽代码块样式，展示调用的工具名（如 `grafana_query_loki`）与参数，带可展开的 JSON 查看器；
  - **安全审计决定**：醒目的徽章卡片（`APPROVED 🛡️`），带有数字签名散列。

### 4. 📊 Grafana 取证面板 (`GrafanaEvidenceWidget`)
- 动态嵌入精简版时序曲线（Chart.js / SVG 实现的 500 错误波形与自愈跌落曲线）；
- 原始日志高亮预览（红色标记 `FATAL` / `ERROR`，支持点击复制）；
- 最终制片复盘报告（可一键导出 Markdown 或 PDF）。

---

## 四、动态效果与沉浸感设计 (Motion & Sound FX)

1. **打字机流式输出 (Typewriter Stream)**：Agent 的思考与日志逐字流出，呈现真实的现场推理沉浸感；
2. **场景平滑推进 (Scene Transition)**：Scene 完成时，伴随轻微的镜头推进（Zoom In）与高光划过动画；
3. **低侵入性提示音效 (Optional Cinematic Audio)**：
   - 场记板敲击声（开场 Action）；
   - 告警蜂鸣（P0 Alert）；
   - 杀青提示音（Production Wrap）。
