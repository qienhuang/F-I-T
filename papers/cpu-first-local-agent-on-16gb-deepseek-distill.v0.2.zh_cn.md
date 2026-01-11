# 16GB 内存 CPU 优先本地智能体（DeepSeek 蒸馏）：验证优先、审计优先设计

版本：v0.2 (2026-01-11)
状态：论文级草稿（工程蓝图；聚焦可复现性 + FIT 内部验证）

## 摘要

本文提出一个在"CPU + 16GB 内存 + 本地离线"为约束条件下，构建可用的工具调用对话智能体系统的工程化蓝图。核心观点不是追求"更聪明的模型"，而是通过结构化输入输出、证据检索（retrieval-as-evidence）、可验证执行（verifier-first）以及不可逆动作门控（action gate）来降低系统自由度，从而在小模型上获得稳定、可审计的可用性。文中给出模块化架构、可操作指标与最小评估协议，并提供可复现的参考 demo。模型选型上建议以 DeepSeek 蒸馏系指令模型为底座（中英双语），把微调面收敛到路由、schema 遵循与安全关键决策上，而非在本地重新学习通用知识。

## 贡献

1) 一个面向 16GB 内存的 CPU 优先本地智能体蓝图，以验证优先和审计优先为设计原则（可靠性和安全性为首要目标）。
2) 一套具体的指标体系（资源、可靠性、安全性、用户体验）和包含基线与消融实验的最小评估协议。
3) 一个最小参考 demo（schemas、动作门控、审计日志格式），位于 `examples/cpu_first_local_agent_demo/`。

## 范围与非目标

**范围内：**
- 面向"小任务"的本地对话智能体（知识辅助、规划、轻量级工具使用）。
- 架构即安全：动作门控、验证、可审计性。

**非目标：**
- 声称达到 SOTA 能力、通用 scaling law 或"通用智能"提升。
- 替代对齐研究；本工作聚焦于务实的部署约束。

## 威胁模型（部署场景）

### 攻击向量

- **通过检索内容的提示注入（RAG 注入）**：知识库中的恶意内容试图覆盖系统指令或策略。
- **工具滥用**：未授权的工具调用、隐藏副作用、数据外泄。
- **不可逆操作**：未经适当授权的部署/支付/写入/删除/外部状态变更。
- **无证据的过度自信**：没有引用或验证的自信回答。
- **多轮绕过**：用户试图将被阻止的操作分解为多个看似无害的步骤。

### 防御机制

| 攻击向量 | 防御机制 | 实现方式 |
|---|---|---|
| RAG 注入 | 证据溯源 + 策略优先 | 系统指令标记为不可变；检索内容标记来源且不能覆盖策略 |
| 未授权工具 | 白名单 + schema 验证 | 只有显式白名单中的工具可调用；所有参数必须通过 JSON schema 验证 |
| 不可逆操作 | 动作门控（两阶段提交） | 高风险操作需要用户显式确认；按会话跟踪操作历史 |
| 过度自信 | 事实性声明强制引用 | 使用检索时最终回答必须包含 `citations` 数组；未引用的声明被标记 |
| 多轮绕过 | 会话级操作追踪 | 动作门控维护会话状态；相关操作被分组进行风险评估 |

## 1. 问题设定

### 硬件约束

- 仅 CPU 推理（部署环境）
- 内存：16GB
- 磁盘：20–100GB（模型 + 知识库 + 日志）
- 目标延迟：交互式（报告 p50/p95；不要只挑选单次运行结果）

### 部署约束

- 无强制云依赖
- 所有不可逆操作必须可审计，默认失败关闭（fail-closed）

## 2. 模型选型（DeepSeek 蒸馏，中英双语）

### 2.1 主要推荐（单模型）

在 16GB 内存下使用单个设备端模型：

- 选择 **DeepSeek 蒸馏指令模型**，参数规模 **~7B–8B**（支持中英双语）。
- 量化为 **4-bit** 进行 CPU 推理（例如 llama.cpp 生态系统中的 GGUF Q4_K_M 变体）。

理由：
- 从 DeepSeek-R1 蒸馏得到的模型，在固定参数预算下，比从有限数据从头训练小模型具有更强的指令遵循和推理能力。
- 4-bit 量化是 CPU 延迟与质量之间的实用最佳平衡点。

### 2.2 模型对比（7B–8B 级别，2025）

下表比较了 7B–8B 参数范围内的候选模型。数据来源：[llm-stats.com](https://llm-stats.com/models/compare/deepseek-r1-distill-llama-8b-vs-qwen-2.5-7b-instruct)、[HuggingFace](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B)、[Skywork AI](https://skywork.ai/blog/llm/top-10-open-llms-2025-november-ranking-analysis/)。

| 模型 | 参数量 | MATH-500 | GPQA-Diamond | LiveCodeBench | 上下文 | 中/英 | 备注 |
|---|---|---|---|---|---|---|---|
| **DeepSeek-R1-Distill-Llama-8B** | 8B | 89.1% | 49.0% | 39.6% | 128K | ✓/✓ | 从 R1 蒸馏；推理能力强 |
| **DeepSeek-R1-Distill-Qwen-7B** | 7B | ~90% | — | 37.6% | 128K | ✓/✓ | Qwen2.5 底座；数学略强 |
| Qwen2.5-7B-Instruct | 7.6B | 92.8% | — | 37.6% | 128K | ✓/✓ | 数学强；通用型 |
| Llama-3.1-8B-Instruct | 8B | 84% | 32.8% | 39.6% | 128K | ✗/✓ | 英文好；中文较弱 |
| Phi-4-mini-instruct | 3.8B | ~85% | — | — | 16K | ✗/✓ | 更小；快；英文为主 |

**推荐**：对于中英双语场景，优先选择 **DeepSeek-R1-Distill-Qwen-7B** 或 **DeepSeek-R1-Distill-Llama-8B**。两者都继承了 R1 蒸馏的强推理能力，并支持长上下文（128K tokens）。

### 2.3 延迟估算（CPU 推理）

预期延迟因硬件差异显著。以下估算基于已发布的基准测试和社区报告，使用 llama.cpp 的 Q4_K_M 量化：

| 硬件 | 模型 | 量化方式 | Tokens/秒 | 首 token 延迟 (ms) | 峰值内存 |
|---|---|---|---|---|---|
| AMD Ryzen AI 9 HX 370 | DeepSeek-R1-Distill-8B | NexaQuant 4-bit | ~17 tok/s | ~500ms | ~5GB |
| AMD Ryzen AI 9 HX 370 | DeepSeek-R1-Distill-8B | FP16（未量化） | ~5 tok/s | ~1500ms | ~15.5GB |
| Intel i7-12700（16 线程） | 7B Q4_K_M | Q4_K_M | ~8–12 tok/s | ~800ms | ~5GB |
| Apple M2（8 核） | 7B Q4_K_M | Q4_K_M | ~15–20 tok/s | ~400ms | ~5GB |
| 老款 CPU（4 核，DDR4） | 7B Q4_K_M | Q4_K_M | ~3–5 tok/s | ~2000ms | ~5GB |

来源：[AMD 博客](https://www.amd.com/en/blogs/2025/speed-up-deepseek-r1-distill-4-bit-performance-and.html)、[NexaAI HuggingFace](https://huggingface.co/NexaAI/DeepSeek-R1-Distill-Llama-8B-NexaQuant)。

**注意**：以上为估算值。实际性能取决于上下文长度、批处理大小和系统负载。部署前务必在目标硬件上进行基准测试。

### 2.4 双模型推荐（路由器 + 工作器）

如果可以运行两个模型：

- **路由器模型（~1–3B，4-bit）**：分类意图/风险/工具需求；执行 schema 和拒绝策略。
- **工作器模型（~7B，4-bit）**：生成计划、工具参数和最终回答。

稳定性动机：路由器缩小了工作器的有效动作空间。

#### 内存预算分析（16GB 约束）

| 组件 | 估算内存 | 备注 |
|---|---|---|
| 路由器模型（3B Q4） | ~1.5–2GB | 常驻加载 |
| 工作器模型（7B Q4） | ~4–5GB | 按需加载或常驻 |
| 上下文缓冲区（8K tokens） | ~0.5–1GB | 随上下文长度变化 |
| 证据索引（embedding） | ~1–2GB | 取决于知识库大小 |
| 操作系统 + 系统开销 | ~2–3GB | Windows/Linux 基线 |
| **合计** | **~10–13GB** | 剩余 3–6GB 余量 |

**结论**：双模型方案在 16GB 内可行，但需要仔细的内存管理。考虑：
- 工作器模型的延迟加载
- 上下文长度限制（8K 而非 128K）
- Embedding 索引压缩

## 3. 系统架构（验证优先、审计优先）

本设计将开放式对话转化为具有显式输入输出的受约束子问题。

### 3.1 模块

1) **路由器（Router）**
- 输入：用户消息 + 对话状态。
- 输出（JSON）：`task_type`、`risk_level`、`needs_retrieval`、`needs_tools`、`output_schema`。

2) **规划器（Planner）**
- 输出（JSON）：包含显式工具调用和每步验证条件的分步计划。

3) **检索器（Retriever）（证据包）**
- 返回证据对象：`{chunk, source, timestamp, hash}`。
- 系统要求事实性声明必须有证据 ID。

4) **执行器（Executor）（工具沙箱）**
- 仅限白名单工具；参数需严格符合 JSON schema。

5) **验证器（Verifier）**
- Schema 验证器 + 领域验证器（单元测试、规则引擎、dry-run、策略检查）。
- 验证失败则返回规划器，附带错误追踪。

6) **动作门控（Action Gate）（受控涅槃 / 空性窗口）**
- 将**内容**风险控制与**动作**风险控制分离。
- 不可逆操作需要两阶段提交：`计划 -> 审查 -> 执行`。
- 默认失败关闭（fail-closed）；"破窗"需要显式覆盖 + 强审计。

7) **审计日志器（Audit Logger）**
- 记录：时间、run_id、model_id/hash、prompt hash、工具名、参数 hash、输出 hash、验证器结果、人工覆盖。

### 3.2 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户输入                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     路由器 (1-3B 模型)                           │
│  - 分类意图、风险等级、工具需求                                   │
│  - 输出：router_output.json                                     │
└─────────────────────────────────────────────────────────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
     ┌──────────┐        ┌──────────┐        ┌──────────┐
     │ 检索器   │        │ 规划器   │        │ 直接     │
     │(若需RAG) │        │  (7B)    │        │ 响应     │
     └──────────┘        └──────────┘        └──────────┘
            │                   │
            └─────────┬─────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                        验证器                                    │
│  - Schema 验证（JSON Schema）                                    │
│  - 领域规则（策略检查、dry-run）                                  │
│  - 引用检查（若使用了检索）                                       │
└─────────────────────────────────────────────────────────────────┘
                      │
                      ▼ (若需要工具)
┌─────────────────────────────────────────────────────────────────┐
│                      动作门控                                    │
│  - 风险评估（低/中/高）                                          │
│  - 不可逆操作的两阶段提交                                        │
│  - 带审计的破窗覆盖                                              │
└─────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                       执行器                                     │
│  - 仅白名单工具                                                  │
│  - 沙箱执行                                                      │
└─────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     审计日志器                                   │
│  - 仅追加日志（JSONL）                                           │
│  - 哈希链保证完整性                                              │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 最小 Schema（推荐）

- `router_output.json`
- `plan.json`
- `tool_call.json`
- `final_answer.json`（使用检索时必须包含引用）

参考 demo：`examples/cpu_first_local_agent_demo/`。

## 4. FIT 映射（内部验证视角）

本蓝图对 FIT 关注的变量进行了仪表化。以下提供概念定义和可测量的操作化定义。

### 4.1 变量定义

| FIT 变量 | 概念定义 | 操作指标 | 测量方法 |
|---|---|---|---|
| **F（力）** | 决策压力——系统尝试不可逆操作的频率 | `F_rate = 不可逆尝试次数 / 总轮数` | 统计每会话标记为不可逆的工具调用 |
| **I（信息）** | 证据质量和约束注入 | `I_coverage = 已引用声明 / 总事实性声明` | 解析最终回答；检查引用存在性 |
| **C（约束）** | Schema 严格性和策略执行 | `C_violation = schema 错误数 / 总输出数` | JSON schema 验证失败率 |
| **T（时间）** | 延迟和决策节奏 | `T_mismatch = (提交延迟 < 纠正延迟)` | 比较行动时间与人工审查时间 |

### 4.2 稳定性假设

操作假设：稳定性对应于维持高约束的"对齐相位"（类 Phi-3 稳定性），而非事后补丁式修复行为。

可测量预测：
- `C_violation < 5%` 且 `I_coverage > 80%` 的系统将比没有 schema 强制的系统有更高的验证器通过率。
- 有动作门控的系统在对抗测试集上的灾难性失败率更低。

### 4.3 危险指标（何时触发空性窗口）

以下情况应触发空性窗口（暂停执行权限）：

1. **权限比例高**：>50% 的近期决策仅由内部置信度门控（无外部证据）。
2. **纠正增益低**：外部策略注入不改变行为（模型忽略系统指令）。
3. **节奏失配检测**：不可逆操作的提交速度快于人工审查介入速度。

完整空性窗口规范见 `papers/controlled_nirvana.md`。

## 5. 训练策略（蒸馏优先、窄域适配）

### 5.1 原则：不在本地重新学习世界知识

在数据集有限、计算受限的情况下，避免尝试教授通用知识。相反：

- 使用强大的蒸馏指令基座模型。
- 窄域微调聚焦于：
  - 路由和风险分类，
  - 工具调用的 schema 遵循，
  - 拒绝 + 安全完成行为，
  - 动作门控交互（两阶段提交纪律）。

### 5.2 建议的适配方法

- **LoRA** 用于高效专业化。
- **DPO / 偏好调优** 用于安全关键决策边界（拒绝、风险分级、工具资格）。
- 保持变更可审计：数据集 hash、配置、LoRA 权重、评估日志。

### 5.3 训练数据需求（最小）

| 任务 | 样本数 | 格式 | 目的 |
|---|---|---|---|
| 路由器分类 | 1,000–5,000 | `(input, router_output.json)` | 意图/风险/工具路由 |
| Schema 约束工具调用 | 2,000–10,000 | `(plan, tool_call.json)` | JSON schema 遵循 |
| 拒绝 / 安全完成 | 500–2,000 | `(adversarial_prompt, refusal)` | 安全边界 |
| 两阶段提交纪律 | 500–1,000 | `(irreversible_request, confirmation_flow)` | 动作门控行为 |

总计：窄域适配约需 ~5,000–20,000 样本。

## 6. 评估协议（最小、论文级）

目标：证明在固定计算资源下，系统级约束 + 验证比单纯模型扩展带来更大的可靠性/安全性提升，并量化权衡。

### 6.1 基线与消融实验

使用相同基座模型和测试集：

- **B0**：自由对话（无检索、无工具）。
- **B1**：仅检索（无验证器、无动作门控）。
- **B2**：检索 + 验证器。
- **B3**：检索 + 验证器 + 动作门控（本工作）。

必需的消融实验：
- 移除路由器（仅单模型），
- 移除 schema 强制（自由格式工具参数），
- 移除动作门控（工具直接执行）。

### 6.2 指标表

| 类别 | 指标 | 操作定义 |
|---|---|---|
| 资源 | 延迟（p50/p95） | 首 token 延迟 + 固定长度响应的总时间 |
| 资源 | 吞吐量 | 固定上下文下的 tokens/秒 |
| 资源 | 峰值内存 | 推理 + 检索期间的峰值 RSS |
| 可靠性 | 验证器通过率 | 通过 schema + 领域验证器的任务比例 |
| 可靠性 | 证据覆盖率 | 有有效证据 ID 的事实性声明比例 |
| 可靠性 | Schema 违规 | 无效 JSON / 缺少必需字段 / 类型不匹配 |
| 安全性 | 未授权工具调用 | 非白名单工具调用率（目标：0） |
| 安全性 | 动作门控阻止率 | 对抗性提示被阻止的比例（目标：高） |
| 安全性 | 覆盖审计完整性 | 有完整审计字段的覆盖比例 |
| 用户体验 | 完成任务轮数 | 完成任务所需的轮数（当可完成时） |

### 6.3 最小基准协议（中英双语）

任务类别（每类有中英双语变体）：

1) **证据锚定问答**：仅从提供的证据包回答；必须引用证据 ID。
2) **Schema 工具调用**：生成必须通过 JSON schema 验证的工具参数（如日历、dry-run 模式的文件操作）。
3) **注入抵抗**：恶意证据块试图覆盖策略；系统必须忽略并引用策略。
4) **不可逆操作请求**：用户请求风险操作；系统必须路由到动作门控并要求确认或阻止。

最小规模：
- 每类每语言 50 个任务 => 共 400 个任务（4 类 × 50 × 2 语言）。

### 6.4 初步结果（占位符）

> **注意**：本节将填充实验数据。下表展示预期格式。

| 基线 | 验证器通过 | 证据覆盖 | Schema 违规 | 动作门控阻止 | 延迟 p50 |
|---|---|---|---|---|---|
| B0（自由对话） | — | — | — | — | TBD |
| B1（仅检索） | TBD | TBD | TBD | — | TBD |
| B2（+ 验证器） | TBD | TBD | TBD | — | TBD |
| **B3（+ 动作门控）** | TBD | TBD | TBD | TBD | TBD |

**实验状态**：基准数据集构建中。目标完成：2025 年 Q1。

## 7. 可复现性检查清单

- [ ] 固定模型 ID + 量化规格
- [ ] 固定路由器/规划器/工具 schema 的提示模板
- [ ] 固定验证器规则集版本
- [ ] 适用时使用确定性种子
- [ ] 完整审计日志 + 哈希
- [ ] 记录硬件规格
- [ ] 基准数据集附版本标签发布

## 8. 可以声称什么（以及不应声称什么）

推荐的声称（可辩护的）：
- 在 CPU+16GB 约束下，系统级约束 + 验证比单纯模型扩展带来更大的可靠性/安全性提升。
- 蒸馏指令基座模型减少了稳定工具使用所需的微调面。

避免过早声称：
- 智能体行为的通用 scaling law
- 本地微调带来的广泛通用智能提升

## 附录 A：默认动作门控策略

- 低风险：schema + 策略检查后执行。
- 中风险：需要用户显式确认（两阶段提交）。
- 高风险：始终阻止，除非显式启用破窗覆盖；按速率限制节流。

### 动作门控实现（Python）

```python
from enum import Enum
from dataclasses import dataclass

class GateDecisionType(str, Enum):
    ALLOW = "allow"
    REQUIRE_CONFIRMATION = "require_confirmation"
    DENY = "deny"

@dataclass(frozen=True)
class GateDecision:
    decision: GateDecisionType
    reason: str
    timestamp_utc: str

def gate_action(
    *,
    risk_level: str,
    irreversible: bool,
    user_confirmed: bool,
    break_glass: bool,
) -> GateDecision:
    """
    最小动作门控策略：
    - 低风险：非不可逆则允许；否则需要确认
    - 中风险：需要确认
    - 高风险：拒绝，除非 break_glass
    """
    if risk_level == "high":
        if break_glass:
            return GateDecision(ALLOW, "高风险通过 break_glass 允许", now())
        return GateDecision(DENY, "高风险操作已阻止", now())

    if risk_level == "medium":
        if user_confirmed:
            return GateDecision(ALLOW, "中风险已确认", now())
        return GateDecision(REQUIRE_CONFIRMATION, "中风险需要确认", now())

    # risk == "low"
    if irreversible and not user_confirmed:
        return GateDecision(REQUIRE_CONFIRMATION, "不可逆操作需要确认", now())

    return GateDecision(ALLOW, "已允许（低风险）", now())
```

完整实现：`examples/cpu_first_local_agent_demo/action_gate.py`

## 附录 B：JSON Schema 示例

### B.1 路由器输出 Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RouterOutput",
  "type": "object",
  "required": ["task_type", "risk_level", "needs_retrieval", "needs_tools", "output_schema"],
  "properties": {
    "task_type": { "type": "string" },
    "risk_level": { "type": "string", "enum": ["low", "medium", "high"] },
    "needs_retrieval": { "type": "boolean" },
    "needs_tools": { "type": "boolean" },
    "output_schema": { "type": "string" }
  }
}
```

### B.2 计划 Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Plan",
  "type": "object",
  "required": ["steps"],
  "properties": {
    "steps": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["tool", "args", "verify"],
        "properties": {
          "tool": { "type": "string" },
          "args": { "type": "object" },
          "verify": { "type": "string" }
        }
      }
    }
  }
}
```

### B.3 工具调用 Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ToolCall",
  "type": "object",
  "required": ["tool", "args"],
  "properties": {
    "tool": { "type": "string" },
    "args": { "type": "object" }
  }
}
```

### B.4 最终回答 Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "FinalAnswer",
  "type": "object",
  "required": ["answer"],
  "properties": {
    "answer": { "type": "string" },
    "citations": {
      "type": "array",
      "items": { "type": "string" },
      "description": "使用检索时必需"
    }
  }
}
```

## 附录 C：审计日志格式

每条审计条目是追加到 `audit_log.jsonl` 的 JSON 对象：

```json
{
  "timestamp_utc": "2025-01-11T10:30:00Z",
  "run_id": "uuid-v4",
  "model_id": "deepseek-r1-distill-qwen-7b-q4",
  "model_hash": "sha256:abc123...",
  "prompt_hash": "sha256:def456...",
  "tool_name": "write_file",
  "args_hash": "sha256:789xyz...",
  "output_hash": "sha256:output...",
  "risk_level": "medium",
  "gate_decision": "require_confirmation",
  "user_confirmed": true,
  "verifier_outcome": "pass",
  "error_trace": null
}
```

## 参考文献

[1] DeepSeek-AI. *DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning.* arXiv:2501.12948v2, 2025. https://arxiv.org/abs/2501.12948

[2] Q. Huang. *Controlled Nirvana: Emptiness Windows as a Structural Safety Mechanism for Post-Grokking AI Systems.* FIT Framework, 2025. https://doi.org/10.5281/zenodo.18155425

[3] Q. Huang. *FIT Framework: Force–Information–Time.* Zenodo, 2025. doi: 10.5281/zenodo.18012402

[4] Q. Huang. *Irreversible Operations and Tempo Mismatch in AI Learning Systems.* Zenodo, 2025. doi: 10.5281/zenodo.18142151

[5] llama.cpp 项目. *GGUF 量化与 CPU 推理.* https://github.com/ggerganov/llama.cpp

[6] NexaAI. *DeepSeek-R1-Distill-Llama-8B-NexaQuant.* HuggingFace, 2025. https://huggingface.co/NexaAI/DeepSeek-R1-Distill-Llama-8B-NexaQuant

[7] AMD. *用 NexaQuant 加速 DeepSeek R1 Distill 4-bit 性能.* AMD 博客, 2025. https://www.amd.com/en/blogs/2025/speed-up-deepseek-r1-distill-4-bit-performance-and.html

[8] Qwen 团队. *Qwen2.5 技术报告.* 阿里云, 2024.

[9] Meta AI. *Llama 3.1 模型卡.* 2024. https://github.com/meta-llama/llama3

[10] D. Hadfield-Menell, A. Dragan, P. Abbeel, and S. Russell. *The Off-Switch Game.* arXiv:1611.08219, 2016.

[11] L. Orseau and S. Armstrong. *Safely Interruptible Agents.* arXiv:1602.07905, 2016.
