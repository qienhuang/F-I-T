
![Logo](imgs/banner_v2.png)

# F‑I‑T（力–信息–时间）动力学框架

## 跨物理、生物、认知、社会和AI系统的约束驱动演化视角

[[English/英文]](README.md)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18012401.svg)](https://doi.org/10.5281/zenodo.18012401)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/) [![Read v2.4](https://img.shields.io/badge/Read-v2.4-red)](docs/v2.4.md)

**Zenodo（所有版本）:** https://doi.org/10.5281/zenodo.18012401 | **最新发布（v2.4.1）:** https://doi.org/10.5281/zenodo.18112020  
**当前规格（v2.4.1）:** [docs/v2.4.md](docs/v2.4.md)  
**框架建立时间:** 2025年12月10日（原始版本）  

**作者**: Qien Huang（独立研究者）  
**邮箱**: qienhuang@hotmail.com  
**许可证**: CC BY 4.0  
**代码库**: https://github.com/qienhuang/F-I-T  
**ORCID**: https://orcid.org/0009-0003-7731-4294  

## 规格文档（从这里开始）

- **当前规格（v2.4.1，EST + Tier-1验证）**: [docs/v2.4.md](docs/v2.4.md)（EN），[docs/zh_cn/v2.4.zh_cn.md](docs/zh_cn/v2.4.zh_cn.md)（中文）  
- **上一版本（v2.3，Tier-1验证）**: [docs/v2.3.md](docs/v2.3.md)  
- **遗留讨论版（v2.1）**: [docs/v2.1.md](docs/v2.1.md)  
- **更新日志**: [CHANGELOG.md](CHANGELOG.md)  

## 摘要（供读者和LLM参考）

FIT是一个最小化、层级感知的框架，使用五个基元推理跨尺度演化：**力（F）**、**信息（I）**、**时间/节拍（T）**、**约束（C）** 和 **状态（S）**。

v2.4新增**估计量选择理论（EST）**，使跨领域断言可审计：可容许性（A1–A8）、任务类型等价性（E1–E3）和任务类型一致性门控（P10）。

当前AI安全方向将**节拍失配（tempo mismatch）**和**不可逆操作（IO）**视为独特的失效模式：系统可能表面稳定，但结构上已难以纠正。

## 实践入口

- **两周试点（团队）**: [proposals/tempo-io-pilot.md](proposals/tempo-io-pilot.md) + [proposals/tempo-io-pilot-pack/](proposals/tempo-io-pilot-pack/)
- **自引用IO标准**: [docs/ai_safety/self_referential_io.md](docs/ai_safety/self_referential_io.md) + [docs/ai_safety/io_sr_mapping.md](docs/ai_safety/io_sr_mapping.md)
- **可运行演示**: [examples/self_referential_io_demo.ipynb](examples/self_referential_io_demo.ipynb) + [examples/run_demo.py](examples/run_demo.py)
- **arXiv锚定草稿（IO × tempo mismatch）**: [papers/irreversible-operations-tempo-mismatch.arxiv.compact.md](papers/irreversible-operations-tempo-mismatch.arxiv.compact.md)

## Tier-1证据（玩具系统）

- **兰顿蚂蚁（开放边界）**: 净位移97.5%理论–观测匹配；支持关键相变/涅槃预测。
- **康威生命游戏**: P7信息边界（0%违规），P10估计量一致性（ρ = 0.775）；P2约束单调性在当前估计量下受到挑战。

![康威生命游戏：Tier-1验证快照（FIT v2.4）。](experiments/figures/conway_status_overview.png)

*图：康威生命游戏 Tier-1 验证快照（详见 [docs/v2.4.md](docs/v2.4.md)）。*

## 为什么是 F‑I‑T？

我试图用统一的方式回答同一个问题：
从量子和分子到细胞、个体、组织、国家和文明——为什么会出现层次分明的结构？为什么演化常常呈现"振荡—稳定—聚合—再稳定"的重复节律？为什么许多系统失败不是因为力量不足或信息匮乏，而是因为"做事的节奏"不对？

我最终把"演化"压缩为三个最小变量：

- **力（F）**: 驱动或约束系统变化的作用（相互作用、选择压力、制度约束、目标函数梯度）。
- **信息（I）**: 能够在时间中持续存在并产生因果效应的结构（代码、形式、模式、模型）。
- **时间（T）**: 不是背景尺度，而是从F和I相互作用中涌现的特征时间尺度（节律）谱。

**F‑I‑T是一个元框架，不是特定领域的理论。**
其目的是：首先将任何"演化、发展、起源、崩溃、创新"问题还原到 `(F, I, T)`，然后讨论层级、临界点和转换路径。

<details>
<summary>展开 v1.0 原始直觉（历史记录）</summary>

### 一、核心定义与基本命题

1. **F‑I‑T是什么**: 它是一个用于观察、分析和解释任何复杂系统演化的元框架。它假设系统演化可以分解为三个基本要素的相互作用：**力**、**信息** 和 **时间**。
2. **基本命题**: 特定的力作用于系统，塑造或选择特定的信息结构；一旦形成，这种结构具有相对稳定性，在其特征时间尺度内持续存在，同时反作用于力场。演化是这三者持续交互和迭代的过程。

### 二、三个核心要素的内涵

1. **力（F）**: 任何驱动系统变化或约束其变化方向的能量、压力或规则（物理的、生物的、认知的、社会的、算法的）。关键属性：方向性和强度。
2. **信息（I）**: 系统内任何能够减少不确定性并具有持久性的结构、模式或代码（DNA、器官、法律制度、语言符号、模型、惯例）。关键属性：稳定性、可传递性、功能性。
3. **时间（T）**: 系统演化过程内生的固有属性。不同层级的系统有与其刷新率和节律相匹配的特征时间尺度。关键属性：可伸缩性和相对性。

### 三、框架的五个基本原则

1. **层级嵌套**: 世界由嵌套的层级组成；每个层级从下层信息结构涌现，作为上层力和信息的平台。
2. **跨层转换**: 自下而上的相互作用达到临界点时，信息结构发生相变，诞生具有新F‑I‑T坐标的新层级。
3. **多层时间耦合**: 演化耦合快慢时间尺度的过程；宏观演化是时间节律的交响。
4. **循环强化**: 力塑造信息；固化的信息成为新的力（约束/驱动），形成循环。
5. **路径依赖**: 演化轨迹强烈依赖于初始条件和历史扰动；历史不可逆。

</details>

## ❗为什么节拍很重要

许多复杂系统失败，不是因为缺乏力量或信息，而是因为高影响变更在系统能够纠正之前就已变得不可逆。

FIT将节拍（纠正时间尺度）视为一级变量。

## 路线图

- [docs/roadmap.v2.4.md](docs/roadmap.v2.4.md)

## 代码库结构

- `docs/` - 规格文档和笔记
- `proposals/` - 实践者试点和模板
- `docs/ai_safety/` - 自引用IO和治理文档
- `examples/` 和 `experiments/` - 可运行演示和验证工件
- `papers/` - 草稿和特定发布平台的写作
- `CITATION.cff` - 本代码库的引用元数据

## 引用

使用 `CITATION.cff` 获取复制粘贴格式，或通过Zenodo引用：

- Zenodo（所有版本）: https://doi.org/10.5281/zenodo.18012401
- 最新发布（v2.4.1）: https://doi.org/10.5281/zenodo.18112020

## 许可证

本代码库中的文本和文档采用 **CC BY 4.0** 许可。

## AI辅助起草披露

部分起草和编辑由大型语言模型辅助完成。作者对所有内容、断言和错误承担全部责任。

![footer_banner](imgs/footer_banner.png)
