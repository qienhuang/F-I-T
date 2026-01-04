![Logo](imgs/banner_v2.png)

# F‑I‑T（Force–Information–Time）动力学框架

## 一个以约束为核心的跨尺度演化视角（物理/生物/认知/社会/AI）

[[English]](README.md)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18012401.svg)](https://doi.org/10.5281/zenodo.18012401)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Read v2.4](https://img.shields.io/badge/Read-v2.4-red)](docs/v2.4.md)

**Zenodo（全集 DOI，自动指向最新）**：https://doi.org/10.5281/zenodo.18012401  
**最新发布（v2.4.1）**：https://doi.org/10.5281/zenodo.18112020  
**当前规范（v2.4.1）**：[docs/v2.4.md](docs/v2.4.md)  
**框架提出**：2025‑12‑10（最初版本）

**作者**：Qien Huang（独立研究者）  
**邮箱**：qienhuang@hotmail.com  
**许可证**：CC BY 4.0  
**仓库**：https://github.com/qienhuang/F-I-T  
**ORCID**：https://orcid.org/0009-0003-7731-4294

## 规范（从这里开始）

- **当前规范（v2.4.1，EST + Tier‑1 验证）**：[docs/v2.4.md](docs/v2.4.md)（EN），[docs/zh_cn/v2.4.zh_cn.md](docs/zh_cn/v2.4.zh_cn.md)（中文）
- **上一版（v2.3，Tier‑1 验证）**：[docs/v2.3.md](docs/v2.3.md)
- **早期讨论版（v2.1）**：[docs/v2.1.md](docs/v2.1.md)
- **变更记录**：[CHANGELOG.md](CHANGELOG.md)

## 快速概览

**问题背景**：不同学科往往用彼此割裂的语言描述“演化/发展/学习/崩溃”（热力学、信息论、复杂性科学、机器学习等）。各自有效，但缺少跨域可对齐的最小语法与可证伪结构。

**FIT 的回应**：把“演化”压缩成五个原语（**力/信息/时间/约束/状态**）与六条原则，并给出 18 个可证伪命题；所有命题必须绑定到显式的估计器元组（状态表征 + 边界 + 估计器 + 窗口）。

**核心洞见**：许多系统失败不是因为“缺少力量/信息”，而是因为高影响变更变得不可逆的速度超过了纠错速度。

**五原语（形式化摘要）**：

| 原语 | 定义 | 直观解释 |
|------|------|----------|
| **状态 (S)** | $S_t \in \mathcal{S}$ | 时间 $t$ 的系统构型 |
| **力 (F)** | $\mathbb{E}[S_{t+1} - S_t \mid S_t] = \alpha F(S_t, t)$ | 广义漂移 / 定向影响 |
| **信息 (I)** | $I_{\text{gain}} := H(P_0) - H(P_1)$ | 熵减少 / 知识增益 |
| **约束 (C)** | $C(t) := \log \lvert \mathcal{S} \rvert - \log \lvert \mathcal{S}_{\text{accessible}}(t) \rvert$ | 可达状态空间收缩 |
| **时间 (T)** | 有序索引 $t$ 与特征时间尺度 | 由 F–I 相互作用涌现的节奏谱 |

**v2.4 的关键特性**：
- **EST（Estimator Selection Theory）**：8 条可审计的可接受性公理（A1–A8），用于约束估计器选择，降低“估计器黑客”批评
- **18 个可证伪命题**：有明确的成功/失败标准
- **Tier‑1 验证**：兰顿蚂蚁（开放边界）97.5% 理论‑观测匹配；生命游戏 P7 约束‑信息界 0% 违例
- **AI safety 主线**：tempo mismatch + Irreversible Operations（IO）作为独立于 alignment/robustness 的失败模式

**阅读完整规范**：[docs/v2.4.md](docs/v2.4.md)

## 实用入口（给业者/研究者）

- **两周试跑（团队用）**：[proposals/tempo-io-pilot.md](proposals/tempo-io-pilot.md) + [proposals/tempo-io-pilot-pack/](proposals/tempo-io-pilot-pack/)
- **自指涉 IO 控制标准（S‑RIOCS）**：[docs/ai_safety/self_referential_io.md](docs/ai_safety/self_referential_io.md) + [docs/ai_safety/io_sr_mapping.md](docs/ai_safety/io_sr_mapping.md)
- **可运行 demo**：[examples/self_referential_io_demo.ipynb](examples/self_referential_io_demo.ipynb) + [examples/run_demo.py](examples/run_demo.py)
- **arXiv 锚定稿（IO × tempo mismatch）**：[papers/irreversible-operations-tempo-mismatch.arxiv.compact.md](papers/irreversible-operations-tempo-mismatch.arxiv.compact.md)

## Tier‑1 证据（玩具系统）

- **兰顿蚂蚁（开放边界）**：净位移 97.5% 理论‑观测匹配；支持相变/吸引子/“涅槃态”相关预测
- **康威生命游戏**：P7 信息界 0% 违例；P10 估计器一致性 rho = 0.775；P2 约束单调性在当前估计器下被挑战

![康威生命游戏：Tier‑1 验证快照（FIT v2.4）](experiments/figures/conway_status_overview.png)

*图：康威生命游戏 Tier‑1 验证快照（细节见 [docs/v2.4.md](docs/v2.4.md)）。*

## 为什么是 F‑I‑T？

我尝试用一个统一语言回答同一个问题：从量子与分子到细胞、个体、组织、国家与文明——为什么层级结构会涌现？为什么很多演化过程呈现“振荡 → 稳定 → 聚合 → 再稳定”的节律？为什么许多系统并非缺少资源或信息，而是“做事节奏”错了？

最早的压缩是把演化视为三变量相互作用：

- **Force (F)**：驱动或约束状态变化的作用（相互作用、选择压、制度约束、目标函数梯度等）
- **Information (I)**：能跨时间保持并产生因果影响的结构（代码、形式、模式、模型等）
- **Time (T)**：不是背景标尺，而是由 F–I 互动产生的特征时间尺度谱（节奏）

**FIT 是一个元框架，而不是某一具体领域的专门理论。**  
它的用途是：先把“演化/发展/起源/崩溃/创新”等问题压缩到 (F, I, T)，再讨论层级、临界点与转变路径。

<details>
<summary>展开：v1.0 直觉版（历史快照）</summary>

### 核心定义与基本命题（摘要）

1. **F‑I‑T 是什么**：观察、分析、解释复杂系统演化的元框架，将系统演化分解为 **力**、**信息**、**时间** 的交互。
2. **基本命题**：力塑形信息；信息一旦固化在其时间尺度内稳定，并反过来作为约束/驱动影响后续演化。演化是这一循环的持续迭代。

</details>

## 为什么“节奏”重要

许多复杂系统失败，不是因为缺少力量或信息，而是因为高影响变更变得不可逆的速度超过了系统纠错速度。

FIT 把 tempo（纠错/评估/回滚的时间尺度）当作一等变量。

## 路线图

- [docs/roadmap.v2.4.md](docs/roadmap.v2.4.md)

## 仓库地图

- `docs/`：框架规范与路线图
- `proposals/`：两周试跑与落地材料
- `docs/ai_safety/`：AI safety 的 IO/tempo 治理标准
- `examples/`、`experiments/`：可运行 demo 与验证脚本
- `papers/`：论文草稿与对外文章
- `CITATION.cff`：引用信息

## 引用

请优先引用 Zenodo DOI：

- Zenodo（全集 DOI）：https://doi.org/10.5281/zenodo.18012401
- 最新发布（v2.4.1）：https://doi.org/10.5281/zenodo.18112020

## 许可证

本仓库文本与文档使用 **CC BY 4.0** 许可证发布。

## AI 辅助声明

部分起草/编辑工作使用了大语言模型工具；作者对所有内容、主张与错误负全责。

![footer_banner](imgs/footer_banner.png)
