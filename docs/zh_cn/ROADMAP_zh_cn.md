## 研发路线图（Roadmap）

### 当前状态概览

- **当前核心规范（离散 / 经典 FIT 层）**  
  `fit_full_v2.3.md` —— 给出 5 个原语、6 条框架原则 / 工作假说、18 条可证伪命题，并引入 T‑theory（尾段动力学子框架）以及一个可解的一维玩具模型。

- **新读者推荐入口**  
  v2.1 “讨论与验证版（Discussion & Validation Edition）” —— 收敛了说法、列出完整命题，并给出 GoL / Langton’s Ant 的示例验证与可操作 estimator。:contentReference[oaicite:1]{index=1}

- **设计理念（Design ethos）**  
  极简原语；明确描述层级；每个原语配至少一种可操作估计器；所有重要命题都可证伪；提供清晰的验证计划与命题注册表。

---

### 里程碑 0 —— 稳定 2.x 主线（约 0–3 个月）

**目标**：把当前 “离散 / 经典 FIT” 堆栈稳定下来，让外部读者易于理解和批评。

- [ ] 将 `fit_full_v2.3.md` 冻结为 2.x 线的权威规范（离散 + 经典系统）。  
- [ ] 保留 v2.1 作为“讨论 / 引用友好”的推荐入口，在 README 顶部显式指向 v2.1 与 v2.3。:contentReference[oaicite:2]{index=2}  
- [ ] 固定 **命题注册表（proposition registry）** 的机器可读 Schema（YAML / JSON）：
  - 为每个 P1–P18 提供：ID、短名、适用范围、估计器定义、边界声明、验证 protocol、当前状态。
- [ ] 发布最小可用的 **Tier‑1 验证脚本**：
  - 康威生命游戏（Conway’s Game of Life）：覆盖 P1、P2、P4、P7、P9、P10、P17、P18 的最小版本。
  - 朗顿蚂蚁（Langton’s Ant）：覆盖 P1、P3、P4、P10、P11、P18 的最小版本。
- [ ] 在仓库中增加一篇简短的 “如何反驳 FIT（How to falsify FIT）” 指南：
  - 推荐优先攻击哪些命题；
  - 如何在注册表里记录负结果。

**成功判据**：  
任意用户 clone 仓库后，能运行一小段脚本，在 GoL / Langton’s Ant 上看到清晰的、可重复的证据——支持或反驳一部分 P1–P18。

---

### 里程碑 1 —— Tier‑1 验证与工具链（约 3–9 个月）

**目标**：让 FIT 从“概念框架”变成一个真正可实验、可破坏的对象。

- [ ] 提供整洁、带文档的 Python 参考实现：
  - GoL + 对应的 `S_t, F, C, I` 估计器与绘图脚本；
  - Langton’s Ant + 对应估计器与绘图脚本。
- [ ] 为关键命题提供可复现的 **验证 Notebook**：
  - GoL 上的 P1 / P2 / P4；
  - Langton’s Ant 上的 P3 / P11。
- [ ] 把验证脚本与 **命题注册表** 连通起来：
  - 每条命题至少有一个可运行 protocol 和一个 status 字段：
    `Untested | Partial | Supported | Falsified | Scope‑limited`。
- [ ] 可选：在 CI 中挂一套轻量验证测试，在 push 时自动跑一小部分案例。

**成功判据**：  
至少有 5–8 条命题在 Tier‑1 系统上拥有明确的“状态”；仓库本身可以作为“如何使用 / 攻击 FIT”的参考实现。

---

### 里程碑 2 —— 连续时间 FIT（迈向 v3.0‑C）（约 6–18 个月）

**目标**：把 FIT 从离散步进提升到连续时间形式，并在一类非平凡系统上给出真正的数学定理。

以一类标准的随机微分方程（SDE / 梯度扩散）作为“母类”：

- [ ] 定义一个连续时间的 FIT 层：
  - 状态：\( S(t) = X_t \in \mathbb{R}^d \)；
  - 动力学：\( dX_t = F(X_t)\,dt + \sigma(X_t)\,dW_t \)；
  - 信息：分布上的熵 / 相对熵 \( D(\mu_t \Vert \mu_\infty) \)；
  - 约束：Lyapunov 型泛函 \( C(t) = C_{\max} - \mathbb{E}_\mu[\Phi(X_t)] \)。
- [ ] 在这类系统上，至少证明一到两个“硬”定理：
  - **连续版 P2**：在适当条件下，所选 \( C(t) \) 单调（或几乎单调）增加，直到平台；
  - **连续版 P3**：在梯度流类系统中，力方差 \( \mathrm{Var}[F(X_t)] \) 指数（或幂律）衰减。
- [ ] 写一篇可以单独投出的短文：
  - 暂定题目：  
    “Constraint Accumulation and Force‑Variance Collapse in Gradient Diffusions: A Continuous‑Time Case Study in the FIT Framework.”
- [ ] 起草 `fit_continuous_v3.0-alpha.md`：
  - 新的记号与假设；
  - 把上述定理显式标为 v2.x 中 P2/P3/P13 的连续时间版本；
  - 给出连续时间 T‑theory 的基本形式（hitting time、exit time、准稳态分布等）。

**成功判据**：  
有一个自洽的“连续时间 FIT 文档 + 数学附录”，在一类非平凡 SDE 上，把“约束积累 ⇒ 力方差塌缩”真正写成定理，而不是经验命题。

---

### 里程碑 3 —— 量子 FIT（迈向 v3.0‑Q）（约 9–24 个月）

**目标**：为 5 个原语给出一个极简的量子版本，并在小维 Lindblad 模型上验证 FIT 风格的命题。

- [ ] 指定一套 **量子原语**：
  - 状态：密度矩阵 \( \rho(t) \)；
  - “力”：生成元 \( \mathcal{L}[\rho] \)（Lindbladian / Liouvillian）；
  - 信息：冯·诺依曼熵、量子相对熵；
  - 约束：秩 / 支撑子空间限制、去相干泛函，或“相对熵到稳态”这类 Lyapunov 泛函。
- [ ] 精算 2–3 个可解的 Lindblad 玩具模型：
  - 量子比特纯去相干（pointer basis / decoherence）；
  - 振幅阻尼（amplitude damping，向基态弛豫）；
  - 简单的 Gibbs 热化模型（收敛到 Gibbs 态）。
- [ ] 在这些模型上，展示 **量子版 FIT 结构**：
  - 某个“量子约束泛函” \( C(t) \) 单调增加；
  - 某种合适定义下的“力方差”算子范数随时间衰减；
  - 给出清晰的“量子涅槃态”定义（稳态 / pointer states）。
- [ ] 起草 `fit_quantum_v3.0-alpha.md` 或短文：
  - 暂定题目：  
    “Quantum FIT: Constraint and Drift Collapse in Simple Lindbladian Systems.”

**成功判据**：  
至少有一个非平凡的 Lindblad 模型被“从头到尾”算清楚：给出 \( C(t) \) 的单调性、力（生成元）意义下的塌缩，并定义了 T‑theory 在该模型中的量子版本。

---

### 里程碑 4 —— FIT v3.0 的整体整合与重构（约 18–36 个月）

**目标**：把离散、连续、量子三层整合成一个结构一致的 “FIT v3.x 世代”。

- [ ] 重构主规范文档，拆成三个互相配套的部分：
  - Part I：离散 / 经典 FIT（清理后的 2.x 主线）；
  - Part II：连续时间 FIT（SDE / Markov 半群层）；
  - Part III：量子 FIT（有限维 Lindblad 层）。
- [ ] 对 P1–P18 做一次按 **数学地位** 的重标记：
  - “在离散上已证明”、“在连续上有定理”、“在量子上有定理”、“目前仅经验支持”、“仍是开放问题”。
- [ ] 把 T‑theory 提升为一级子文档：
  - 离散系统的 T‑theory；
  - 连续时间 SDE 的 T‑theory；
  - 开放量子系统（pointer states / decoherence）的 T‑theory。
- [ ] 增加一节专门讨论 **尺度变换 / coarse‑graining**：
  - \( F, I, C \) 在粗粒化下如何变换；
  - 在什么条件下，FIT 风格的“定律”在多尺度之间保持形式不变，或出现修正项。

**成功判据**：  
读者在同一套 v3 文档中，可以一眼看清：FIT 在离散 / 连续 / 量子三种设定下分别是什么样；每条命题在哪些设定中已被证明；T‑theory 如何在三层上统一描述“尾段动力学”。

---

### 里程碑 5 —— 应用与合作（持续进行）

**目标**：让 FIT 从“内部研究计划”变成其他领域可以直接调用的工具箱。

- [ ] AI 安全方向：
  - 用 T‑theory 形式化“对齐涅槃（alignment nirvana）”，设计奖励 / 算法，使系统自然收敛到高约束、低力方差、目标停止的区域；
  - 发布一批带代码的例子（比如 termination‑friendly 的 RL 试验）。
- [ ] 复杂性与相变：
  - 与复杂性、生态、气候或 ML 动力学方向的合作者一起，在真实或大规模仿真系统中测试 P13 / P14 / P16–P18；
  - 看看 FIT 的相变 / 临界减速指标是否比现有方法有优势。
- [ ] 制度与治理设计：
  - 用 \( I/C \) 与约束层级的视角分析不同制度在“稳定性 vs 适应性”上的权衡，例如带 / 不带 sunset 条款的制度差异。
- [ ] 把仓库维护成 FIT 的 **规范注册中心**：
  - 命题定义与状态；
  - 验证脚本和负结果；
  - 外部论文与实现的链接。

---

### 如何参与

如果你对以下任一方向感兴趣：

- 连续时间 / 随机微分方程 / Markov 半群；
- Lindblad 动力学 / 开放量子系统；
- 复杂性科学 / 相变 / 临界现象；
- AI 训练动力学 / AI 安全；
- 制度设计 / 演化博弈 / 社会系统建模；

欢迎直接在本仓库开一个 **Issue** 或 **Discussion**，简单说明：

- 你感兴趣的 **里程碑 ID**（例如 “Milestone 2: Continuous‑time FIT”）；  
- 你熟悉的工具 / 领域（如 PDE / SDE，量子信息，RL，复杂网络等）；  
- 你打算从哪一条命题或哪一个玩具模型开始动手。

这个 Roadmap 会随着进展持续更新，也欢迎任何形式的批评、缩减建议或 alternative framing。  
目标不是把 FIT 说成“终极理论”，而是把它打磨成一个**足够可反驳、足够好用**的公共语言。
