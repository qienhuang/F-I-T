# 如何从 MCC 重建 FIT

状态：**核心文档**。给新读者的一份“可重建”导言：如何从最小核心推导出完整框架。

导航：[`core 索引`](./README.md) | [`核心卡片`](./fit_core_card.md) | [`MCC`](./MCC.md) | [`MCC 依赖图`](./MCC_graph.md) | [`Phase Algebra`](./phase_algebra.md) | [`Phi3 稳定性`](./phi3_stability.md) | [`v2.4 规格（中文）`](../v2.4.zh_cn.md)

## 受众

本文件面向：
- 想深入理解 FIT（不仅是套用）的研究者
- 未来可能贡献/扩展 FIT 的协作者
- 想精确定位“不同意点”的批评者

## 重建原则

> FIT 的设计目标是“可重建”，而不只是“可阅读”。

只要你接受 6 条 MCC 断言以及 EST 纪律，你就能推导出其余内容。本文给出一条干净的重建路径。

## Step 0：接受起点

你只需要一个基础承诺：

> **MCC-1（Force 传播）**：在演化系统中，变化由可传播驱动力触发。若驱动力无法跨层级/子系统传播，系统只会发生表层变化。

若拒绝此点，FIT 不适用；若接受，继续。

## Step 1：推出 Information 与 Constraint

从 MCC-1 出发，问：“当 Force 成功传播时会发生什么？”

两个后果出现：
1. 有些结构被写入并持久（MCC-2：Information 持久性）
2. 有些状态变得不可达（MCC-3：Constraint 累积）

这不是新增公理，而是把“Force 重塑结构”展开成可操作的骨架。

## Step 2：推出 Phase 结构

从 MCC-2 + MCC-3 出发，问：“结构形成在时间上是平滑的吗？”

经验与理论上通常不是。系统会在不同阶段呈现不同动力学类型，因此需要：
- MCC-4：阶段化演化
- 最小相位基：Phi1/Phi2/Phi3（见 [`phase_algebra.md`](./phase_algebra.md)）

## Step 3：把相变变成可登记对象

从 MCC-4 出发，问：“我们如何知道发生了相变？”

在 EST 下，答案不能是直觉。必须可操作、可审计，于是得到 MCC-5：
- PT-MSS：只有当 Force redistribution、Information re-encoding、Constraint reorganization 在观测窗 `W` 内共同出现时，才登记相变。

见 [`phase_algebra.md`](./phase_algebra.md)。

## Step 4：推出晚期不可逆性

从 MCC-5 出发，问：“反复相变与协调之后会发生什么？”

经验上，进入协调晚期的系统会越来越难回到早期结构，因此得到 MCC-6：
- 不可逆性是概率性的（回退变稀少），不是绝对“不能变”。

晚期稳定性的工程化判据见 [`phi3_stability.md`](./phi3_stability.md)。

## Step 5：展开到命题注册表

MCC 的骨架可以展开为 [`docs/zh_cn/v2.4.zh_cn.md`](../v2.4.zh_cn.md) 中的命题集。

注意：
- 命题编号与分类以 v2.4 规格为准
- 本导言不做 1:1 的 “MCC -> P#” 映射
- 命题是 estimator-scoped 的展开，不是新公理

实用连接方法：
1. 先用 MCC 判断你在做哪类主张（F / I / C / Phase / 不可逆性）
2. 在 v2.4 规格中选择对应命题族
3. 声明 estimator scope（EST），并做可接受性与稳健性报告

## Step 6：应用 EST 纪律

任何 FIT 主张都必须：
1. estimator-scoped（声明测什么）
2. admissibility-checked（估计器满足 FIT 标准）
3. coherence-gated（跨估计器一致性门控）
4. robustness-reported（参数敏感性报告）

估计器诊断见 [`docs/est/diagnostics.md`](../../est/diagnostics.md)。

## Step 7：生成领域应用

有了 MCC + EST，你可以分析任何演化系统：
1. 定义该领域的 Force
2. 定义 Information 与 Constraint 的估计器
3. 分类当前相位（Phi1/Phi2/Phi3）
4. 寻找 PT-MSS 信号
5. 用 SC-1/SC-2/SC-3 评估晚期稳定性

证据层通常位于 `experiments/` 与领域文档中。
