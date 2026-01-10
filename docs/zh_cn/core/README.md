# FIT 核心文档（v2.4.1+）

状态：本目录为 **中文译稿**，用于降低阅读门槛；英文 canonical 版本在 [`docs/core/README.md`](../../core/README.md)。

这些文档：
- 不引入任何超出 [`docs/zh_cn/v2.4.zh_cn.md`](../v2.4.zh_cn.md) 的新原语或新命题。
- 提供一个最小、可教学、可交接的框架入口，并保持 EST 纪律。
- 目标是减少误读，而不是替代证据层（实验/案例）。

## 索引

记号：相位写作 `Φ₁/Φ₂/Φ₃`（在文件名/代码中用 `Phi1/Phi2/Phi3`）。

### 从这里开始
- [`fit_core_card.md`](./fit_core_card.md) - 一页入口（操作化速览）
- [`fit_two_page_card.md`](./fit_two_page_card.md) - 两页入口（核心 + Φ₃ 之后分岔）
- [`MCC.md`](./MCC.md) - 最小自洽核心（6 条 MCC 断言）

### 结构
- [`MCC_graph.md`](./MCC_graph.md) - MCC 依赖图（DAG）
- [`phase_algebra.md`](./phase_algebra.md) - Phase Algebra + PT-MSS（对 P11/P13 的操作化）

### 稳定性
- [`phi3_stability.md`](./phi3_stability.md) - Φ₃ 稳定性判据（SC-1/SC-2/SC-3；nirvana 的工程化定义）

### 扩展与护栏
- [`FIT_Core_Extension_Post_Phi3.md`](./FIT_Core_Extension_Post_Phi3.md) - Φ₃ 之后：协调后的两条结构路径（A/B）
- [`FIT_Misuse_Guard_and_FAQ.md`](./FIT_Misuse_Guard_and_FAQ.md) - 误用防护与 FAQ（红线与边界条件）

### 应用
- [`grokking_phase_mapping.md`](./grokking_phase_mapping.md) - Grokking 的 FIT 相变映射（ML 中的 Φ₁→Φ₂→Φ₃）

### 给新读者
- [`reconstruction_guide.md`](./reconstruction_guide.md) - 如何从 MCC 重建完整 FIT
