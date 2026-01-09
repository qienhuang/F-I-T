![Logo](imgs/banner_v2.png)

# F-I-T（Force–Information–Time）动力学框架

## 一个以约束为核心、面向物理/生物/认知/社会/AI 演化的元语言

[[English]](README.md)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18012401.svg)](https://doi.org/10.5281/zenodo.18012401)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/) [![Read v2.4](https://img.shields.io/badge/Read-v2.4-red)](docs/v2.4.md)

**Zenodo（所有版本）**：https://doi.org/10.5281/zenodo.18012401 | **最新版（v2.4.1）**：https://doi.org/10.5281/zenodo.18112020

**已发布论文（Zenodo）**：
- **建议先读（入口）— FIT (Force-Information-Time) Dynamics: Origin and Design Goals:** https://doi.org/10.5281/zenodo.18142211
- **AI 安全— Irreversible Operations and Tempo Mismatch in AI Learning Systems:** https://doi.org/10.5281/zenodo.18142151
- **AI 安全（grokking）— Controlled Nirvana: Emptiness Windows as a Structural Safety Mechanism for Post-Grokking AI Systems:** https://doi.org/10.5281/zenodo.18155425

**案例研究：**
- [**Li² Grokking scaling law 复现（基于 Li² 论文；独立验证）**](experiments/li2_scaling_law/README.md)
- [**智能手机与注意力系统**](docs/zh_cn/cases/CASE_01_Phone_Attention_System.md)
- [**内容平台与内卷**](docs/zh_cn/cases/CASE_02_Content_Platform_Involution.md)
- [**学习：从记忆到理解**](docs/zh_cn/cases/CASE_04_Learning_From_Memory_to_Understanding.md)

*注：人名仅作为论文作者引用；不暗示任何从属关系或背书。*

---

**当前规范（v2.4.1）**：[docs/v2.4.md](docs/v2.4.md)
**框架建立**：2025 年 12 月 10 日（原始版本）

**作者**：Qien Huang（独立研究者）
**邮箱**：qienhuang@hotmail.com
**许可证**：CC BY 4.0
**仓库**：https://github.com/qienhuang/F-I-T
**ORCID**：https://orcid.org/0009-0003-7731-4294

## 规范文档（从这里开始）

> **首次阅读推荐顺序**：核心卡 → 当前规范（v2.4）→ 入口文档

- **最快入口（核心卡，v2.4.1+）**：[docs/zh_cn/core/fit_core_card.md](docs/zh_cn/core/fit_core_card.md)
- **当前规范（v2.4.1，EST + Tier-1 验证）**：[docs/v2.4.md](docs/v2.4.md)（EN），[docs/zh_cn/v2.4.zh_cn.md](docs/zh_cn/v2.4.zh_cn.md)（中文）
- **上一版（v2.3，Tier-1 验证）**：[docs/v2.3.md](docs/v2.3.md)
- **讨论版（v2.1）**：[docs/v2.1.md](docs/v2.1.md)
- **更新日志**：[CHANGELOG.md](CHANGELOG.md)
- **版本策略**：[docs/core/Versioning_Policy.md](docs/core/Versioning_Policy.md)

> **稳定性说明**：2.x 核心已稳定；修订由反例驱动。详见 [版本策略](docs/core/Versioning_Policy.md)。

## 为什么 F-I-T？

从量子、分子到细胞、个体、组织、国家乃至文明——为什么会出现清晰的层级结构？为什么演化常常呈现"振荡—稳定—聚合—再稳定"的重复节奏？为什么很多系统的失败不是因为能力不足或信息缺失，而是因为**节奏错了**？

我试图把"演化"压缩到三个最小变量：

- **Force（F）**：驱动或约束系统变化的作用（交互、选择压力、制度约束、目标函数梯度）
- **Information（I）**：能在时间中保持并产生因果效应的结构（编码、形态、模式、模型）
- **Time（T）**：不是背景刻度，而是 F 与 I 相互作用涌现出的特征时间尺度谱（节奏）

**F-I-T 是元框架，不是某个具体领域的理论。**
它的用法：先把任何"演化/发展/起源/崩溃/创新"问题还原到 `(F, I, T)`，再讨论层级、临界点与转变路径。

---

## FIT 声明什么（以及不声明什么）

**FIT 不声明**：
- ❌ 复杂系统的"万有理论"
- ❌ 取代现有框架（自由能原理、Constructor Theory 等）
- ❌ 能预测复杂系统的精确轨迹
- ❌ 所有命题已在所有领域得到验证

**FIT 声明**：
- ✅ 一套用于跨领域讨论演化的最小元语言
- ✅ 可通过计算与实证实验证伪
- ✅ 初步 Tier-1 验证在受控系统中显示出有希望的结果
- ✅ 在 AI 安全与复杂性科学中的应用是可行的

---

## FIT v2.4 概览

**问题**：现代科学通过碎片化的视角（热力学、信息论、复杂性科学、机器学习）来研究演化。它们各自成功，但缺乏跨领域综合所需的共享公理。

**FIT 的回应**：把"演化"压缩到五个原语和六条原则。生成 18 条可证伪命题，绑定到显式估计器元组。

**核心洞察**：许多系统失败不是因为缺乏能力或信息，而是因为高影响变化在纠偏发生之前就变得不可逆。FIT 把节奏（纠偏时间尺度）作为一阶变量。

**五个原语**：

| 原语 | 定义 | 解释 |
|------|------|------|
| **状态（S）** | $S_t \in \mathcal{S}$ | 时刻 $t$ 的系统配置 |
| **力（F）** | $\mathbb{E}[S_{t+1} - S_t \mid S_t] = \alpha F(S_t, t)$ | 广义漂移 / 定向影响 |
| **信息（I）** | $I_{\text{gain}} := H(P_0) - H(P_1)$ | 熵减少 / 知识增益 |
| **约束（C）** | $C(t) := \log \lvert \mathcal{S} \rvert - \log \lvert \mathcal{S}_{\text{accessible}}(t) \rvert$ | 可达状态空间缩减 |
| **时间（T）** | 有序索引 $t$，带特征尺度 | 由 F–I 交互涌现 |

**v2.4 关键特性**：
- **估计器选择理论（EST）**：8 条可接受性公理（A1–A8），防止"估计器黑客"批评
- **18 条可证伪命题**，带显式成功/失败标准
- **Tier-1 验证**：Langton's Ant 理论–观测匹配 97.5%，Conway's GoL P7 边界 0% 违规
- **AI 安全轨道**：节奏错配 + 不可逆操作作为独特失效模式

**阅读完整规范**：[docs/v2.4.md](docs/v2.4.md)

## 入口（实践导向）

- **FIT 与 AI 安全（从这里开始）**：[docs/ai_safety/fit_ai_safety_mapping.md](docs/ai_safety/fit_ai_safety_mapping.md) — 5 分钟概览 + 2 小时自检清单
- **两周试跑（面向团队）**：[proposals/tempo-io-pilot.md](proposals/tempo-io-pilot.md) + [proposals/tempo-io-pilot-pack/](proposals/tempo-io-pilot-pack/)
- **自指涉能力的 IO 控制标准**：[docs/ai_safety/self_referential_io.md](docs/ai_safety/self_referential_io.md) + [docs/ai_safety/io_sr_mapping.md](docs/ai_safety/io_sr_mapping.md)
- **可运行 demo**：[examples/self_referential_io_demo.ipynb](examples/self_referential_io_demo.ipynb) + [examples/run_demo.py](examples/run_demo.py)
- **Tier-2.5 演示（预注册）**：[experiments/real_world/nyc_311_tier2p5/](experiments/real_world/nyc_311_tier2p5/) — NYC 311 服务请求；将 FIT 指标应用于真实世界数据（非验证声明）
- **arXiv 锚定草稿（IO × 节奏错配）**：[papers/irreversible-operations-tempo-mismatch.arxiv.compact.md](papers/irreversible-operations-tempo-mismatch.arxiv.compact.md)

### Tier-2.5（NYC 311）— 决策视图

![NYC 311 Tier-2.5（预注册演示）：window-normalized rho 与 backlog（HPD；created-date 边界=2024；in-scope vs closure tail）](experiments/real_world/nyc_311_tier2p5/figures/run003_v3_W14_H14/decision_view.png)

这是一个**预注册演示**（不是"真实世界验证"声明）。垂直标记指示 **created-date 边界**：arrivals 按构造过滤到 2024 年，而 closures 可能延续到 2025 年（closure tail；在该边界设定下对 H1 属于 out of scope）。

**当前解读（HPD 2024；W=14, H=14）**：coherence gate 通过，但 H1 为 **INCONCLUSIVE**，因为在 created-date 边界内 **rho 始终 < 1**（in-scope 的 tempo mismatch 事件数为 0）。

可复现性 + 护栏：[prereg_v3.yaml](experiments/real_world/nyc_311_tier2p5/prereg_v3.yaml) 和 [experiment README](experiments/real_world/nyc_311_tier2p5/README.md)。

## Tier-1 证据（玩具系统）

- **Langton's Ant（开放边界）**：净位移理论–观测匹配 97.5%；支持关键相变/涅槃相关预测
- **Conway's Game of Life**：P7 信息边界（0% 违规），P10 估计器一致性（rho = 0.775）；P2 约束单调性在当前估计器下被挑战

![Conway's Game of Life: Tier-1 validation snapshot (FIT v2.4).](experiments/figures/conway_status_overview.png)

*图：Conway's Game of Life Tier-1 验证快照（详见 [docs/v2.4.md](docs/v2.4.md)）*

## 路线图

| 里程碑 | 目标 | 时间窗 |
|--------|------|--------|
| **M0** | 稳定 2.x 规范；发布 Tier-1 验证脚本（GoL、Langton's Ant） | 0–3 月 |
| **M1** | Python 参考实现；5–8 条命题可复现状态 | 3–9 月 |
| **M2** | 连续时间 FIT（SDE 层）；证明约束累积定理 | 6–18 月 |
| **M3** | 量子 FIT（Lindbladian 层）；演示 P2/P3 的量子类比 | 9–24 月 |
| **M4** | 合并离散/连续/量子为统一 v3.0 | 18–36 月 |
| **M5** | 应用：AI 安全、复杂性科学、制度设计 | 持续 |

**完整路线图**：[docs/roadmap.v2.4.md](docs/roadmap.v2.4.md)

## 仓库结构

- `docs/` — 规范与笔记
- `proposals/` — 实践者试跑与模板
- `docs/ai_safety/` — 自指涉 IO 与治理文档
- `examples/` 和 `experiments/` — 可运行 demo 与验证产物
- `papers/` — 草稿与特定投稿文件
- `CITATION.cff` — 本仓库的引用元数据

## 引用

使用 `CITATION.cff` 获取复制粘贴格式，或通过 Zenodo 引用：

- Zenodo（所有版本）：https://doi.org/10.5281/zenodo.18012401
- 最新版（v2.4.1）：https://doi.org/10.5281/zenodo.18112020

## 许可证

本仓库中的文本和文档采用 **CC BY 4.0** 许可。

## AI 辅助写作声明

部分起草与编辑由大语言模型辅助完成。作者对所有内容、声明和错误负全责。

![footer_banner](imgs/footer_banner.png)
