# FIT 最小自洽核心（MCC）- v2.4.1+

状态：**核心文档**（压缩版理论入口）。这不是证据文档。

MCC 的目标：把 FIT 压缩成一个最小、自洽的骨架，使外部读者不依赖作者也能重建其余部分（命题集、EST 层、领域案例）。

导航：[`core 索引`](./README.md) | [`核心卡片`](./fit_core_card.md) | [`MCC 依赖图`](./MCC_graph.md) | [`Phase Algebra`](./phase_algebra.md) | [`Φ₃ 稳定性`](./phi3_stability.md) | [`重建导言`](./reconstruction_guide.md)

记号：相位写作 `Φ₁/Φ₂/Φ₃`（在文件名/代码中用 `Phi1/Phi2/Phi3`）。

## 设计约束

1. **不引入新术语**：只使用 `F / I / T / Phase / Constraint`。
2. **不依赖案例**：案例是可选扩展，不是定义本身。
3. **不依赖命题列表**：命题是展开层；MCC 是核心层。

## MCC-1：Force 传播

在演化系统中，变化由一种**可传播的驱动力**（Force）触发。若 Force 无法跨层级/子系统传播，系统只会出现表层/局部变化。

## MCC-2：Information 持久性

只有能在时间上**稳定保存**的结构才算系统中的 Information。短期拟合或瞬态模式默认不算“学到的结构”。

## MCC-3：Constraint 累积

稳定结构的形成伴随可达状态空间的**收缩**，由累积的 Constraints 诱发。Constraints 不是外部规则，而是稳定信息的副产物。

## MCC-4：阶段化演化

演化并非全局平滑，而是被分割为由不同动力学类型定义的 **Phases**（在给定约束结构与 estimator scope 下）。

## MCC-5：相变信号

只有当 **Force 传播**、**Information 编码** 与 **Constraint 结构**在一个显式观测窗与 estimator scope 下“同时重组”时，才登记相变（PT-MSS）。

## MCC-6：晚期不可逆性

当系统进入协调的晚期（Φ₃ 风格）后，大尺度结构性回退会随时间迅速变得不太可能。不可逆性是概率性的（“回退变稀少”），不是绝对的“不能改变”。

## 重建提示（MCC 如何展开）

给定 MCC，其余 FIT 可按以下方式重建：
- **原语与记号**（见 [`docs/zh_cn/v2.4.zh_cn.md`](../v2.4.zh_cn.md)）
- **EST 纪律**：admissibility、coherence gate、robustness reporting（见 [`docs/zh_cn/v2.4.zh_cn.md`](../v2.4.zh_cn.md) 与 [`docs/est/diagnostics.md`](../../est/diagnostics.md)）
- **命题注册表**：P1-P18（在显式 scope + estimators 下的展开）
- **领域案例**：可审计的证据层（例如 `experiments/`）

另见：
- [`MCC_graph.md`](./MCC_graph.md)（依赖图）
- [`reconstruction_guide.md`](./reconstruction_guide.md)（逐步重建导言）
