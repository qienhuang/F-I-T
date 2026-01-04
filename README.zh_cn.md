![Logo](imgs/banner_v2.png)

# F-I-T（Force–Information–Time）动力学框架

> 一个以“约束”为核心的跨尺度演化元语言：把系统演化问题压缩到 $ F $（力）、$ I $（信息）、$ T $（时间/节奏）以及 $ C $（约束）、$ S $（状态），并要求所有主张可操作、可证伪、可审计。

[[English]](README.md)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18012401.svg)](https://doi.org/10.5281/zenodo.18012401)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

**Zenodo（所有版本，概念 DOI）**：https://doi.org/10.5281/zenodo.18012401  
**最新规范版本（v2.4.1）**：https://doi.org/10.5281/zenodo.18112020  

**已发布论文（Zenodo）**：
- FIT（Force-Information-Time）Dynamics: Origin and Design Goals：https://doi.org/10.5281/zenodo.18142211
- Irreversible Operations and Tempo Mismatch in AI Learning Systems：https://doi.org/10.5281/zenodo.18142151

---

## 入口（建议从这里开始）

- **当前规范（v2.4.1，EST + Tier-1 验证）**：`docs/v2.4.md`（英文），`docs/zh_cn/v2.4.zh_cn.md`（中文）
- **两周试跑（面向团队）**：`proposals/tempo-io-pilot.md` + `proposals/tempo-io-pilot-pack/`
- **自指涉能力的 IO 控制标准**：`docs/ai_safety/self_referential_io.md` + `docs/ai_safety/io_sr_mapping.md`
- **可运行 demo**：`examples/self_referential_io_demo.ipynb` + `examples/run_demo.py`
- **复现入口（Tier-1）**：`docs/reproducibility/README.md`

---

## 为什么 F-I-T？

我试图回答一个跨尺度重复出现的问题：从物理与生命到组织与 AI，为什么层级结构会出现、稳定、再聚合？为什么很多系统不是“没能力”，也不是“没信息”，而是**节奏错配**——高影响变化在治理/纠偏赶上之前就变得不可逆？

FIT 的核心主张不是“再造一个世界观”，而是提供一套可审计的工作语言：当你声称某个系统“在变好/变坏/在相变/在锁死”，你必须明确：
你用什么状态表示、什么边界条件、什么估计器，以及在什么时间窗口里得出结论。

---

## Tier-1 证据（玩具系统）

- **Langton’s Ant（开放边界）**：位移预测与观测匹配 97.5%，支持关键相变/吸引子相关命题  
- **Conway’s Game of Life**：P7 信息上界 0% 违规，P10 估计器一致性 ρ=0.775；P2 在当前估计器下被挑战

![Conway's Game of Life: Tier-1 validation snapshot (FIT v2.4).](experiments/figures/conway_status_overview.png)

---

## 联系方式

**作者**：Qien Huang（Independent Researcher）  
**邮箱**：qienhuang@hotmail.com  
**ORCID**：https://orcid.org/0009-0003-7731-4294  
**许可证**：CC BY 4.0  

