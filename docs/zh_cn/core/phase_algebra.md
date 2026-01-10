# Phase Algebra + PT-MSS（v2.4.1+）

状态：**核心文档**。本文件引入与 EST 兼容的“相位语言”，并用 PT-MSS 把“相变”操作化为可登记对象。

导航：[`core 索引`](./README.md) | [`核心卡片`](./fit_core_card.md) | [`MCC`](./MCC.md) | [`Φ₃ 稳定性`](./phi3_stability.md) | [`v2.4.1 更新（英文）`](../../v2.4.1.md)

记号：相位写作 `Φ₁/Φ₂/Φ₃`（在文件名/代码中用 `Phi1/Phi2/Phi3`）。

## 为什么需要 Phase Algebra

在 v2.4.1 之前，“phase/stage”容易被误读为叙事式分段。
Phase Algebra 把 Phase 提升为一级对象，使其：
- **estimator-scoped**（EST 合规）
- **可组合**（嵌套 / 并行 / 重启）
- 支持“相位条件化”的命题精炼（例如 v2.4.1 中对 P2 的相位条件化）

## 定义：Phase（EST-scoped）

在一个显式 estimator specification（EST）下，**Phase** 是一组状态集合，在其中：
1. **Force 传播拓扑**（propagation topology）近似不变；
2. 主要 **Information 存储载体**未发生结构性跳变；
3. 主要 **Constraint 增长机制**保持一致。

Phase 的改变意味着上述至少一条在声明的 estimator scope / windowing 下被打破。

## 典型相位基（最小基）

核心文档使用三类最小相位基：

### Φ₁ - Accumulation（累积）

- Force 存在，但无法稳定写入结构；
- Information 以短期/表层相关为主；
- Constraint 的增长更多依赖外部注入，而非系统内协调。

### Φ₂ - Crystallization（结晶）

- 局部结构稳定；
- 子系统相对独立演化；
- Constraint 在局部快速增长，但全局仍不一致。

### Φ₃ - Coordination（协调）

- 子结构被全局约束调制；
- 冗余结构被抑制；
- 系统进入可持续、可转移的稳定性状态。

## 组合规则（最小）

允许的组合模式包括：
- **嵌套**：`Φ₃(Φ₂(Φ₁))`
- **并行**：`Φ₂ || Φ₂`（多个子系统并行结晶）
- **重启**：`Φ₃ -> Φ₁`（新的 Force 注入重新打开探索）

## PT-MSS：Phase Transition Minimal Signal Set

目标：使“相变”在 EST 下可登记，而不是叙事标签。

只有当在一个声明的观测窗 `W` 内，三类信号同时出现时，才登记相变：

### (S1) Force redistribution（Force 重新分配）

证据表明 Force 的传播路径改变（例如梯度开始进入某表征层；外部冲击重写模型权重）。

### (S2) Information re-encoding（Information 重新编码）

证据表明信息载体/表征改变（例如表层记忆 -> 抽象特征；个体知识 -> 制度规则）。

### (S3) Constraint reorganization（Constraint 重组）

证据表明约束代理发生非平滑重组（例如维度突降、相关结构重连、先前稳定结构被抑制）。

最小决策规则：

`register_transition := (S1 && S2 && S3) within W`

## 与命题的关系

- P11（相变存在性）通过 PT-MSS 变得可操作；
- P13（相变可预测性）通过 PT-MSS 变得可测：评估“提前/同步检测”相对于 PT-MSS 与 EST scope。

另见：
- [`docs/zh_cn/v2.4.zh_cn.md`](../v2.4.zh_cn.md)（命题注册表）
- [`docs/est/diagnostics.md`](../../est/diagnostics.md)（EST/估计器诊断与 scope 报告）
