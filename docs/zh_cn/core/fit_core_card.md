# FIT 核心卡片（Core Card，v2.4.1+）

状态：**核心文档**（一页操作化入口）。完整规格与 EST 细节见 [`docs/zh_cn/v2.4.zh_cn.md`](../v2.4.zh_cn.md)；v2.4.1 的增量更新说明目前以英文为准：[`docs/v2.4.1.md`](../../v2.4.1.md)。

导航：[`core 索引`](./README.md) | [`MCC`](./MCC.md) | [`Phase Algebra`](./phase_algebra.md) | [`Φ₃ 稳定性`](./phi3_stability.md) | [`重建导言`](./reconstruction_guide.md)

记号：相位写作 `Φ₁/Φ₂/Φ₃`（在文件名/代码中用 `Phi1/Phi2/Phi3`）。

## 1）一句话定义

> **FIT 是一个以“阶段（Phase）”为基本对象的框架：在显式 estimator scope 下，分析结构如何形成、如何稳定、以及如何在演化系统中变得（近似）不可逆；其核心变量是 Force、Information、Time 与涌现的 Constraints。**

## 2）最小变量（F / I / T / C）

### Force（F）

可传播的驱动力，能够跨层级/子系统传递并重塑结构。若 Force 不能传播，系统只能发生局部扰动。

### Information（I）

能在时间上稳定保存的结构。短期拟合或瞬态模式默认不算 Information。

### Time（T）

演化的节拍/方向，决定不可逆性与等待代价。Time 不只是参数；它充当稳定性的过滤器。

### Constraint（C）

由稳定结构引起的可达状态空间收缩。Constraints 不是外部规则，而是稳定结构的副产物。

## 3）Phase（Phi）是一级对象

> Phase 不是“时间片段”；它是在给定约束结构下的一类动力学类型（EST-scoped）。

核心文档使用的最小相位基（canonical labels）：
- **Φ₁（Accumulation）**：Force 存在，但无法稳定写入结构。
- **Φ₂（Crystallization）**：局部结构稳定；子系统仍弱协调。
- **Φ₃（Coordination）**：全局约束调制子结构；稳定性可转移。

操作化定义与组合规则见 [`phase_algebra.md`](./phase_algebra.md)。

## 4）PT-MSS（最小相变判据）

只在一个声明的观测窗 `W` 内，三类信号同时出现时才登记“相变”：
1. **Force redistribution**（传播路径改变）
2. **Information re-encoding**（表征/载体改变）
3. **Constraint reorganization**（约束代理非平滑重组）

具体判据见 [`phase_algebra.md`](./phase_algebra.md)。

## 5）MCC（最小自洽核心）

若读者接受 6 条 MCC 断言，即得到了 FIT 的最小骨架；其余内容都是在 estimator scope 下的展开。

见 [`MCC.md`](./MCC.md) 与 [`MCC_graph.md`](./MCC_graph.md)。

## 6）红线（FIT 不是什么）

- 不是价值判断框架。
- 不是对“进步/改进”的保证。
- 不是对复杂系统具体轨迹/事件的预测器。
- 不是替代领域理论（它是一个元语言）。
