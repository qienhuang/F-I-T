![Logo](imgs/banner_v2.png)

# F-I-T（力–信息–时间）动力学框架

## 一个用于分析物理、生物、认知、社会和AI系统演化的最小化、可证伪框架。

[[English]](README.md) | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18012401.svg)](https://doi.org/10.5281/zenodo.18012401) | [![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/) | [![Read v2.4](https://img.shields.io/badge/Read-v2.4-red)](docs/v2.4.md)

---

## 从这里开始（选择你的路径）

| 如果你是... | 从这里开始 |
|-------------|------------|
| **FIT 新手**（5分钟） | [核心卡片](docs/core/fit_core_card.md) — 一页了解原语 + 直觉 |
| **评估框架** | [FIT 的主张](#fit-的主张与非主张) → [Tier-1 证据](#tier-1-证据玩具系统) |
| **从事 AI 安全** | [AI 安全索引](docs/ai_safety/README.md) → [FIT 用于 AI 安全](docs/ai_safety/fit_ai_safety_mapping.md) |
| **运行实验** | [工具包](#工具包) → [Li² 复现](experiments/li2_scaling_law/README.md) |
| **阅读完整规范** | [v2.4 规范](docs/v2.4.md) (EN) / [v2.4 中文](docs/zh_cn/v2.4.zh_cn.md) |

---

## 核心思想

许多系统的失败不是因为缺乏力量或信息，而是因为**高影响的改变在纠正发生之前就已变得不可逆**。

FIT 将 **tempo**（行动时间尺度与纠正时间尺度之间的关系）视为一等变量。

**五个原语**：

| 原语 | 捕获的内容 |
|------|------------|
| **状态 (S)** | 系统配置 |
| **力 (F)** | 有向影响 / 漂移 |
| **信息 (I)** | 熵减少 / 知识增益 |
| **约束 (C)** | 可达状态空间缩减 |
| **时间 (T)** | 从 F–I 交互中涌现的特征尺度 |

**纪律**：所有主张必须绑定到显式的估计器元组。无估计器 → 无主张。

---

## FIT 的主张与非主张

| FIT 不主张 | FIT 主张 |
|------------|----------|
| ❌ "万物理论" | ✅ 讨论演化的最小元语言 |
| ❌ 替代 FEP、构造理论等 | ✅ 可通过计算/实证实验证伪 |
| ❌ 预测精确轨迹的能力 | ✅ 初步 Tier-1 验证显示有前景的结果 |
| ❌ 所有命题在所有领域都已验证 | ✅ AI 安全应用是可操作的 |

---

## Tier-1 证据（玩具系统）

| 系统 | 结果 | 命题 |
|------|------|------|
| **Langton's Ant** | 97.5% 理论–观测匹配 | 相变 / nirvana 预测 |
| **Conway's GoL** | 0% 违例 | P7 信息界 |
| **Conway's GoL** | ρ = 0.775 | P10 估计器一致性 |

![Conway's Game of Life: Tier-1 验证快照](experiments/figures/conway_status_overview.png)

*图：Conway 生命游戏 Tier-1 验证（详见 [v2.4 规范](docs/v2.4.md)）。*

**Tier-2 状态**：Grokking 实验可评估且可复现；基线在严格低 FPR 约束下尚未成为稳定的硬指标。见 [tier2_grokking](experiments/tier2_grokking/README.md) 和 [grokking_hard_indicators_v0.2](experiments/grokking_hard_indicators_v0_2/README.md)。

---

## 论文

| 主题 | 链接 |
|------|------|
| **FIT 起源与设计目标**（从这里开始） | [Zenodo](https://doi.org/10.5281/zenodo.18142211) |
| **AI 安全：不可逆操作与节奏错配** | [Zenodo](https://doi.org/10.5281/zenodo.18142151) |
| **AI 安全（grokking）：受控涅槃** | [Zenodo](https://doi.org/10.5281/zenodo.18155425) / [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6023634) |
| **AI 安全（grokking）：硬指标协议** | [Zenodo](https://doi.org/10.5281/zenodo.18380476) |
| **马尔可夫沙箱 (math.PR)** | [Zenodo](https://doi.org/10.5281/zenodo.18264166) |
| **超越道德宪章** | [Zenodo](https://doi.org/10.5281/zenodo.18341340) |
| **为什么公司转型太晚** | [Zenodo](https://doi.org/10.5281/zenodo.18287053) |

---

## 案例研究

自包含的 FIT 分析（即读即用）。每个案例都有明确的边界和可观测信号。

| 案例 | 聚焦 |
|------|------|
| [Grokking 缩放律 (Li²)](experiments/li2_scaling_law/README.md) | ML 相变 |
| [AlphaFold DB 置信度区间](experiments/real_world/afdb_swissprot_tier2p11_confidence_regimes/README.md) | 真实世界仪器边界 |
| [智能手机与注意力](docs/cases/CASE_01_Phone_Attention_System.md) | 注意力动力学 + 约束累积 |
| [内容平台内卷](docs/cases/CASE_02_Content_Platform_Involution.md) | 反馈循环 + 协调失败 |
| [企业 IT 演化](docs/cases/CASE_03_Enterprise_IT_Evolution.md) | 基础设施锁定 + 节奏错配 |
| [学习：从记忆到理解](docs/cases/CASE_04_Learning_From_Memory_to_Understanding.md) | Grokking 作为相变 |
| [双连续多尺度设计](docs/cases/CASE_05_Data_Driven_Inverse_Design_Bicontinuous_Multiscale.md) | 边界等同微结构库 |
| [BioArc 架构搜索](docs/cases/CASE_06_BioArc_Constrained_Architecture_Search.md) | 约束下的预算探索 |
| [运动想象 BCI](docs/cases/CASE_07_Motor_Imagery_BCI_Monitorability.md) | 低 FPR 预算下的可监控性 |

---

## 工具包

可运行、CPU 优先的构建块。每个都产出可审计的产物。

| 工具包 | 用途 |
|--------|------|
| [工具包索引](tools/README.md) | 所有可运行演示的入口 |
| [FIT 代理警报工具包](tools/fit_proxy_alarm_kit/README.md) | 非 LLM 专家 + 标签预算 + 固定 FPR |
| [FIT 约束探索工具包](tools/fit_constrained_explorer_kit/README.md) | 硬约束下的预算搜索 |
| [FIT EWBench 工具包](tools/fit_ewbench_kit/README.md) | 提示套件运行器 + 日志 + 报告 |
| [FIT Hopfield 实验室工具包](tools/fit_hopfield_lab_kit/README.md) | 玩具联想记忆实验室 + 相图 |
| [探索器索引（FIT-Explorer + 扩展）](docs/explorers/README.md) | 预算方法搜索规范 + 扩展入口 |
| [World-Evolution 探索（v0.1）](docs/world_evolution/README.md) | 玩具演化世界 + 有效变量/告警方法搜索 demo |
| [Math-Discovery 引擎（v0.1）](docs/math_discovery/README.md) | 对表征/引理/策略的可审计探索（以规范为先） |
| [GMB v0.4](docs/benchmarks/gmb_v0_4/README.md) | Grokking 警报可接受性基准 |

---

## AI 安全专题

| 资源 | 描述 |
|------|------|
| [AI 安全索引](docs/ai_safety/README.md) | 主入口 |
| [FIT 用于 AI 安全](docs/ai_safety/fit_ai_safety_mapping.md) | 5分钟概览 + 2小时自评检查表 |
| [自指 IO 标准](docs/ai_safety/self_referential_io.md) | IO 约束规范 |
| [CPU 优先本地代理](papers/cpu-first-local-agent-on-16gb-deepseek-distill.v0.2.md) | 16GB RAM 蓝图 |
| [慢演化代理架构（v0.2）](docs/agents/README.md) | FIT/EST 对齐的 agent 架构规范 + 可运行的预验证清单 |
| [Dr.One 演示](examples/dr_one_demo/README.md) | 自编辑循环 + 可监控性门 |
| [DeepSeek R1 案例笔记](docs/ai_safety/deepseek_r1_fit_case_note.md) | R1 风格 RL + 风险控制 |

### Dr.One：基线 vs 受控

![Dr.One 策略评估：基线 vs 受控](examples/dr_one_demo/results/figures/dr_one_gating_readwrite_v1.svg)

*如果低 FPR 警报可行，控制器可以在不停止计算的情况下扣留不安全操作的执行权限。可复现性：[MATRIX_PROTOCOL.md](examples/dr_one_demo/results/MATRIX_PROTOCOL.md)*

---

## 规范版本

| 版本 | 描述 | 链接 |
|------|------|------|
| **v2.4.1**（当前） | EST + Tier-1 验证 | [docs/v2.4.md](docs/v2.4.md) |
| v2.3 | Tier-1 验证 | [docs/v2.3.md](docs/v2.3.md) |
| v2.1 | 遗留讨论版 | [docs/v2.1.md](docs/v2.1.md) |

**稳定性**：2.x 核心已稳定；修订由反例驱动。见[版本策略](docs/core/Versioning_Policy.md)。

---

## 路线图

| 里程碑 | 目标 |
|--------|------|
| **M0** | 稳定 2.x 规范；发布 Tier-1 脚本 |
| **M1** | 参考实现；5–8 个命题有可复现状态 |
| **M2** | 连续时间 FIT（SDE 层）；约束累积定理 |
| **M3** | 量子 FIT（Lindbladian 层） |
| **M4** | 统一 v3.0（离散 / 连续 / 量子） |
| **M5** | 应用：AI 安全、复杂性科学、制度设计 |

**完整路线图**：[docs/roadmap.v2.4.md](docs/roadmap.v2.4.md)

---

## 仓库地图

```
docs/           规范和笔记
  ai_safety/    自指 IO 和治理
  benchmarks/   规范 + 预注册模板（如 GMB v0.4）
  explorers/    预算方法搜索（FIT-Explorer）
experiments/    可运行演示和验证产物
papers/         草稿和特定场所的写作
proposals/      实践者试点和模板
skills/         Codex CLI 技能（可选）
tools/          可运行工具包
```

---

## 引用

**Zenodo（所有版本）**：https://doi.org/10.5281/zenodo.18012401  
**最新版（v2.4.1）**：https://doi.org/10.5281/zenodo.18112020

见 [CITATION.cff](CITATION.cff) 获取复制/粘贴格式。

---

## 元数据

**作者**：Qien Huang（独立研究者）  
**邮箱**：qienhuang@hotmail.com   
**许可证**：CC BY 4.0   
**仓库**：https://github.com/qienhuang/F-I-T   
**ORCID**：https://orcid.org/0009-0003-7731-4294   

**AI 辅助起草声明**：部分起草工作由大语言模型辅助完成。作者对所有内容负全责。

![footer_banner](imgs/footer_banner.png)
