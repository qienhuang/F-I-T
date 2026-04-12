# FIT Reader Spec（中文短规范）

[[English]](../spec_reader.md) | [完整 current spec](../spec_current.md)

## 这是什么

这是一份面向当前 FIT 2.x 线的**最短正式入口文档**。

适合在这些情况下阅读：

- 想在一个文件里把 FIT 的主张快速读清；
- 想先理解当前证据姿态，再决定是否进入完整规范；
- 想先掌握边界与防误读规则；
- 想得到一条干净的继续阅读路径。

如果你需要完整整合规范，请读 [`../spec_current.md`](../spec_current.md)。  
如果你需要更新理由，请读 [`../v2.4.1.md`](../v2.4.1.md)。  
如果你需要历史完整快照，请读 [`../v2.4.md`](../v2.4.md) 或 [`v2.4.zh_cn.md`](./v2.4.zh_cn.md)。

---

## 一句话理解

FIT 是一个最小化、受 estimator discipline 约束的框架，用来描述演化系统如何形成结构、稳定结构，并在纠正速度赶不上约束累积速度时逐渐变得难以逆转。

---

## 核心思想

许多系统的失败，不是因为什么都没发生，而是因为变化**锁定得太快**，以至于纠正已来不及起作用。

FIT 把这个锁定问题理解为以下几项之间的关系问题：

- 有向变化如何传播，
- 什么结构能被留下，
- 特征时间尺度如何形成，
- 可达空间如何被压缩。

这个框架刻意保持最小化。
它不替代领域理论，而是提供一套共同的结构语言，用来问：

- 什么在变，
- 什么被保留下来，
- 什么越来越难以撤回，
- 以及何时这些变化应该被读作真实 regime shift，而不只是噪声。

---

## 五个原语

FIT 使用五个原语：

- **状态（S）**：研究中的系统配置
- **力（F）**：有向影响、压力或漂移
- **信息（I）**：能够持续并对未来仍然重要的结构
- **约束（C）**：可达状态空间的缩减
- **时间（T）**：由 F 与 I 的相互作用中涌现出来的特征尺度

约束并不被当作独立的形而上实体。
在当前线里，它更适合被读作：稳定化的信息反过来压缩未来可达空间的结构性结果。

---

## 不可谈判的纪律

每一个 FIT 主张都必须绑定到显式 estimator tuple。

这意味着要说明：

- 测了什么，
- 在哪个窗口里测，
- 采用了什么 admissibility 规则，
- 经过了什么 coherence gate，
- 边界条件是什么。

没有 estimator discipline，就没有 FIT 主张。

这也是 FIT 不只是“有意思的话语”的原因。
它的科学姿态取决于：主张是否 estimator-scoped、在需要时是否 preregistered、以及在失败时是否用正式状态标签报告。

---

## Phase 是一级对象

当前 FIT 2.x 线把 **Phase** 视为一级 regime object。

Phase 不是叙事上的“阶段”。
它是在显式 estimator scope 下的一类动力学类型，其中：

- 主要的 Force 传播结构保持足够稳定，
- 主要的信息承载结构没有发生结构性跳变，
- 主要的 Constraint 增长机制保持一致。

最小 canonical basis 是：

- **Φ₁ Accumulation**：探索占主导，稳定结构还很弱
- **Φ₂ Crystallization**：局部结构开始稳定，但协调仍然碎片化
- **Φ₃ Coordination**：全局约束开始调制子结构，回滚变得越来越不可能

这套相位基是刻意压小的、跨领域的 regime 语言。
它不是在说所有真实系统都能被三个形而上状态完整穷尽。

---

## Transition claims 需要 PT-MSS

FIT 不默认允许“相变”式叙述。

最小 transition rule 是 PT-MSS：

- **S1**：Force redistribution
- **S2**：Information re-encoding
- **S3**：Constraint reorganization

只有当这三类信号在一个声明好的窗口里共同出现时，transition 才能被登记。

这条规则的重要性在于它阻止了两类常见错误：

- 把平滑趋势变化误读成真实 regime change
- 把局部扰动误读成深层结构重组

所以 transition window 本身就是对象的一部分，而不是围绕更“干净曲线”的偶然噪声。

---

## 当前线改变了什么

当前整合 2.x 线把几件事说得更明确了。

### 1. P2 不再被读作一个全局单调性命题

它被拆成：

- **P2a**：phase 内单调性
- **P2b**：晚期相位中的概率性不可逆

这样既不会把每个局部回退都读成反例，也保留了真正的晚期硬化主张。

### 2. P17 被读作结构性的、窗口化的、且常常带循环的重组

维度塌缩不再被读成一个永远下降的标量。
它更适合被读作结构重组，可能包含塌缩、再配置与再次硬化。

### 3. 晚期相位评估必须是分级的

进入 `Φ₃` 和判断 `Φ₃` 的**深度**，是两个不同任务。

当前线采用 `SC` family：

- **SC-1**：持久性
- **SC-2**：有界扰动下的恢复力
- **SC-3**：可迁移稳定性

这让“晚期稳定”不再只是一个二元印象，而是可分级的评估语言。

---

## FIT 真正主张什么

在当前范围内，FIT 主张：

- 结构形成与锁定可以在跨领域中被放入同一种 estimator-bound 语言中讨论
- boundary conditions 常常是对象的一部分，而不是实现细节
- 当系统不是平滑演化而是在重组时，phase-aware interpretation 是必要的
- 不可逆性通常应被读作概率性硬化，而不是形而上的绝不可能
- 证据状态必须保持局部化、命题化、并绑定 estimator

---

## FIT 不主张什么

FIT **不**主张：

- 它是“万物理论”
- 它能预测精确轨迹
- 它能仅靠结构诊断就决定未来事实
- 它提供价值排序、道德理论或政治正当性
- 每个系统都应该被强行讲成 `Φ₁/Φ₂/Φ₃`
- interpretive 或 companion artifacts 自动等于 evidence

总的 anti-misuse rule 是：

> FIT 约束结构性可能空间；它不选择未来事实、价值或权威。

---

## 当前证据姿态

当前最诚实的 evidence posture 是：

- **部分计算支持**
- **明确记录的负结果**
- **越来越严格的 estimator 方法层**
- **仍然开放的更广验证议程**

当前最强的 footing 仍主要集中在 Tier-1 计算系统及其 estimator-disciplined 解读上。

高层概括：

- Conway 和 Langton 提供的是混合但实质性的支持
- 某些核心信息型命题，例如 P7，在已测 toy systems 上较强
- boundary choice 明确重要
- 学习动力学是有价值的验证域，但不自动等于真实世界验证

当前线最强的地方，在于它会明确说明：

- 哪个 proposition，
- 在什么 estimator family 下，
- 在什么系统上，
- 以及对应什么 status label。

它最弱的地方，是当人们试图把这些压成：

- “FIT 已经被证明”
- 或“这个框架就是有效”

这类说法都不应使用。

---

## Evidence 不等于 articulation

FIT 现在有不少很强的 compressed artifacts。
这对教学和 handoff 是好事。

但框架自己也明确说了：

- core artifacts 不是 evidence documents
- interpretive artifacts 不是 evidence documents
- bridge language 不是 evidence

只有 evidence layer 能改变 proposition status。

这是当前 repo 姿态里最健康的一部分之一。

---

## Misuse boundaries

最重要的三条边界是：

### 1. FIT 不是预测引擎

不要写：

- “FIT predicts X”
- “FIT proves this path will occur”
- “因为系统在 `Φ₂`，所以 `Φ₃` 必然到来”

要用有边界的表达：

- “under declared scope”
- “structurally compatible with”
- “appears increasingly unlikely”
- “within this estimator family”

### 2. FIT 不是道德或意识形态理论

不要把：

- stability 译成 virtue
- lateness 译成 blame
- Path A / Path B 译成价值排序

### 3. “太晚了”不会产生权威

尤其在 Phase II 风格的判断环境里：

- structural lateness 不会正当化 coercion
- loss of steering 不会中止 non-authority rule
- No-Return diagnosis 不会授权 domination

---

## 如何阅读这个 repo

如果你是新读者：

1. [`core/fit_two_page_card.md`](./core/fit_two_page_card.md)
2. 本文
3. [`core/MCC.md`](./core/MCC.md)
4. [`../spec_current.md`](../spec_current.md)（如果你需要完整当前线）

如果你是来评估科学姿态的：

1. 本文
2. [`../spec_current.md`](../spec_current.md)
3. [`core/FIT_Misuse_Guard_and_FAQ.md`](./core/FIT_Misuse_Guard_and_FAQ.md)
4. [`../benchmarks/README.md`](../benchmarks/README.md)

如果你需要历史可追踪性：

1. [`../spec_current.md`](../spec_current.md)
2. [`../v2.4.1.md`](../v2.4.1.md)
3. [`v2.4.zh_cn.md`](./v2.4.zh_cn.md) / [`../v2.4.md`](../v2.4.md)

---

## Bottom line

当前 FIT 2.x 线最简洁的短表述是：

> FIT 是一个最小化、phase-aware、受 estimator discipline 约束的框架，用来讨论演化系统中的结构积累、转变与硬化。

而当前最诚实的状态表述是：

> FIT 目前具有有边界的计算支持、明确的 guardrails，以及一个严肃但尚未完成的验证计划。
