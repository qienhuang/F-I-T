# 结构原型库（Structural Archetypes / Patterns）

目标：让 FIT 真正“被别人用”，而不要求读者先理解或接受全部理论层。

这些 Patterns 处在 **Core 与 Cases 之间**：
- **Core**（MCC / Phase Algebra / PT-MSS）：最小承诺与定义
- **Cases**：面向非专业读者的应用叙事

Patterns **不做定量预测**，而提供可复用的结构模板：
- 1 张结构图
- 1 页描述（触发条件、边界条件、常见误读）
- 1 个正例 + 1 个反例（防止过度泛化）

## 如何使用（建议流程）

1. 先选一个最贴近当前问题的 Pattern。
2. 把你的系统映射到结构图（节点/边）。
3. 检查“最小信号集”（类似 PT-MSS 的定性签名）。
4. 做最小干预（优先可逆改动，避免“过拟合治理”）。
5. 若签名不匹配，把它当作反例，换 Pattern。

## 索引

- [PATTERN_01：Φ₃ Trap（Φ₃⁻ 锁死）](PATTERN_01_Phi3_Trap.md)
- [PATTERN_02：反馈主导（Feedback Dominance）](PATTERN_02_Feedback_Dominance.md)
- [PATTERN_03：约束饱和（Constraint Saturation）](PATTERN_03_Constraint_Saturation.md)
- [PATTERN_04：层级逃逸（Hierarchical Escape）](PATTERN_04_Hierarchical_Escape.md)

## 相关入口

- Core Card：`docs/zh_cn/core/fit_core_card.md`
- Phase Algebra + PT-MSS：`docs/zh_cn/core/phase_algebra.md`
- Φ₃ 稳定性判据族：`docs/zh_cn/core/phi3_stability.md`
- 案例：`docs/zh_cn/cases/README.md`
