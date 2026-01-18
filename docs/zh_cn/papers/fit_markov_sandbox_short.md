
# FIT 框架的可证明特化

## 有限马尔可夫链中通过惰性的约束累积

**作者**: Qien Huang  
**框架**: F-I-T (力–信息–时间)  
**许可**: CC BY 4.0  

---

## 摘要

F-I-T（力–信息–时间）框架提出许多演化和学习系统遵循渐进约束累积的轨迹，最终趋近高度稳定或冻结的状态。
然而，如果没有数学上可分析的特化，这样的声明有沦为解释性的风险。

在本工作中，我们在有限状态马尔可夫链的沙盒内提出 FIT 的首个可证明特化。
使用标准的惰性转移硬化路径，我们表明信息产生——通过熵率度量——随着链硬化趋向零，而约束——定义为预测互信息——趋向其最大值。
在简单的自主导条件下，这些趋势沿硬化路径是单调的。
此过程允许将 FIT 提出的"涅槃"状态精确解释为冻结的、完全受约束的动力学状态。

我们的结果表明，核心 FIT 直觉可以在既定的概率论内重新表述为可证伪的、数学上可辩护的陈述。

---

## 1. 引言

FIT 旨在通过三个最小组件描述演化、学习和治理动力学：

* **力 (F)**：状态转移的驱动因素，
* **信息 (I)**：动力学中的不确定性和结构，
* **时间 (T)**：特征时间尺度。

FIT 的核心声明是系统常常通过**累积约束**演化，减少运动自由度同时增加可预测性，最终进入非正式描述为*涅槃*的终端状态。

本文的目标是刻意狭窄但具有基础性：

> 我们不断言所有系统都是马尔可夫的。
> 我们表明，**在标准的、可证明的马尔可夫沙盒内**，FIT 的精确特化表现出向良定义的终端极限的约束累积（并且在简单的自主导条件下，这种累积沿硬化路径是单调的）。

选择有限马尔可夫链是由于其严格的基础、可分析的信息论量，以及在机器学习和统计物理中的广泛接受度。

---

## 2. 马尔可夫沙盒和硬化路径

设 $ \mathcal{S} $ 是一个有限状态空间，$ |\mathcal{S}| = n $。
设 $ P $ 是一个不可约、非周期的行随机转移矩阵。

马尔可夫过程满足：

$$
P(i,j) = \Pr(X_{t+1} = j \mid X_t = i)
$$

### 惰性硬化族

我们引入单参数硬化族：

$$
P_{\alpha} = (1 - \alpha) P + \alpha I
$$

其中 $ \alpha \in [0,1) $ 且 $ I $ 是单位矩阵。

这种构造：

* 增加自转移概率，
* 对所有 $ \alpha < 1 $ 保持遍历性，
* 在活跃动力学和冻结极限之间平滑插值。

---

## 3. 马尔可夫沙盒中的 FIT 特化

设 $ \pi_{\alpha} $ 表示满足以下条件的平稳分布：

$$
\pi_{\alpha} = \pi_{\alpha} P_{\alpha}
$$

对于这个特定的硬化族，平稳分布对所有 $ \alpha < 1 $ 保持不变（命题 1）。
我们保留下标以强调在更一般硬化族中出现的依赖性。

### 信息产生 (I)

我们将信息产生定义为熵率：

$$
I(\alpha) := h(\alpha)
$$

其中

$$
h(\alpha) = H(X_{t+1} \mid X_t)
= \sum_{i \in \mathcal{S}} \pi_{\alpha}(i)\, H(P_{\alpha}(i,\cdot))
$$

此量度量每步产生的新不确定性量。

---

### 约束 (C)

约束定义为预测互信息：

$$
C(\alpha) := I(X_t ; X_{t+1})
$$

在平稳条件下，

$$
C(\alpha) = H(\pi_{\alpha}) - h(\alpha)
$$

更高的 $ C(\alpha) $ 值表示更强的时间依赖和更少的演化自由度。

---

### 时间 (T)

时间由系统的弛豫尺度表征：

$$
T(\alpha) := t_{\mathrm{mix}}(\varepsilon; P_{\alpha})
$$

在数值实验中，谱量被用作代理。

---

## 4. 主要结果

### 命题 1（平稳分布不变性）

设 $P$ 是有限、不可约、非周期的，具有唯一平稳分布 $\pi$。
对于惰性硬化族
$$
P_{\alpha} = (1-\alpha)P + \alpha I
$$
其中 $\alpha \in [0,1)$，平稳分布是不变的：
$$
\pi_{\alpha} = \pi
$$
对所有 $\alpha \in [0,1)$ 成立。

**证明.**
由于 $\pi P = \pi$，我们有
$$
\pi P_{\alpha} = (1-\alpha)\pi P + \alpha \pi = \pi.
$$
由遍历性，平稳分布是唯一的，所以 $\pi_{\alpha} = \pi$。

### 引理 1（行熵抑制）

对任意状态 $ i \in \mathcal{S} $，

$$
P_{\alpha}(i,\cdot) = (1 - \alpha) P(i,\cdot) + \alpha \delta_i
$$

其中 $ \delta_i $ 是 $ i $ 处的点质量。

由于香农熵是凹的且 $P_{\alpha}(i,\cdot)$ 仿射依赖于 $ \alpha $，函数
$\alpha \mapsto H(P_{\alpha}(i,\cdot))$ 在 $[0,1]$ 上是凹的且满足 $\lim_{\alpha \to 1} H(P_{\alpha}(i,\cdot)) = 0$。
特别地，凹性意味着界：

$$
H(P_{\alpha}(i,\cdot)) \ge (1 - \alpha) H(P(i,\cdot))
$$

然而，凹性不意味着单调递减：如果 $P(i,\cdot)$ 高度集中在某个 $j \ne i$，$H(P_{\alpha}(i,\cdot))$ 对小 $ \alpha $ 可以增加。

如果另外 $i$ 是该行的众数（即对所有 $j$，$P(i,i) \ge P(i,j)$），则 $H(P_{\alpha}(i,\cdot))$ 对 $ \alpha $ 非递增（通过优超和香农熵的舒尔凹性）。
简述：对于 $\alpha' > \alpha$，向量 $P_{\alpha'}(i,\cdot)$ 通过将额外质量转移到其最大坐标并缩放余量从 $P_{\alpha}(i,\cdot)$ 获得，这产生优超序；香农熵是舒尔凹的，因此不能增加。

---

### 引理 2（熵率抑制）

熵率满足：

$$
h(\alpha) = \sum_i \pi_{\alpha}(i) H(P_{\alpha}(i,\cdot))
$$

由于对所有 $ \alpha < 1 $，$ \pi_{\alpha} = \pi $，我们有 $\lim_{\alpha \to 1} h(\alpha) = 0$。
此外，$\alpha \mapsto h(\alpha)$ 在 $[0,1]$ 上是凹的。
在引理 1 的行自主导条件下，$h(\alpha)$ 对 $ \alpha $ 非递增；没有这样的条件，单调性不保证。

**证明（极限陈述）。**
对每个 $i$，当 $\alpha \to 1$ 时 $P_{\alpha}(i,\cdot) \to \delta_i$，所以 $H(P_{\alpha}(i,\cdot)) \to 0$。
由于状态空间是有限的且 $\pi$ 是固定的（命题 1），有限和
$h(\alpha) = \sum_i \pi(i) H(P_{\alpha}(i,\cdot))$
也收敛到 $0$。

---

### 推论 1（沿硬化路径的约束累积）

由命题 1，平稳分布是常数（$\pi_{\alpha}=\pi$），所以
$C(\alpha) = H(\pi) - h(\alpha)$ 且 $C(\alpha) \to H(\pi)$ 当 $\alpha \to 1$。

在引理 1 的行自主导条件下，$h(\alpha)$ 非递增因此 $C(\alpha)$ 沿硬化路径非递减。

---

### 定理 1（涅槃极限）

当 $ \alpha \to 1 $：

* $ h(\alpha) \to 0 $，
* $ C(\alpha) \to H(\pi) $，
* $ T(\alpha) \to \infty $。

我们定义**马尔可夫特化涅槃状态**为以下状态：

$$
h(\alpha) \to 0
\quad \text{且} \quad
T(\alpha) \to \infty
$$

对应于完全受约束的、冻结的动力学系统。

$T(\alpha) \to \infty$ 的理由：对任意初始状态 $i$，惰性机制意味着 $\Pr(X_t=i \mid X_0=i) \ge \alpha^t$，因此
$
\lVert \Pr(X_t \in \cdot \mid X_0=i) - \pi \rVert_{\mathrm{TV}} \ge \tfrac12(\alpha^t - \pi(i)).
$
要使此值小于固定的 $\varepsilon$ 需要 $t \gtrsim \log(1/(\pi(i)+2\varepsilon))/(-\log \alpha)$，当 $\alpha \to 1$ 时发散。

---

## 5. 数值验证

我们使用随机生成的遍历转移矩阵验证理论趋势。

对每个实例，我们在 $ \alpha \in [0,0.99] $ 上扫描并计算：

* 平稳分布 $ \pi_{\alpha} $，
* 熵率 $ h(\alpha) $，
* 互信息 $ C(\alpha) $，
* 谱弛豫代理。

在随机生成的遍历转移矩阵样本集中：

* $ h(\alpha) $ 向零减少（在我们的抽样实例中通常是单调的），
* $ C(\alpha) $ 向 $H(\pi)$ 增加，
* 弛豫时间随 $ \alpha \to 1 $ 发散。

实现细节在附带代码中提供。

---

## 6. 讨论和范围

本工作为 FIT 框架建立了**可证明的锚点**。

它不声称普遍性，但表明 FIT 的核心声明——约束累积和终端稳定化——可以在标准概率模型内被严格实例化。

### 注释（外部与内生硬化）

在本工作中，参数 $\alpha$ 被视为用于以受控方式追踪硬化轨迹的外部同伦变量。
在内生系统中，有效硬化参数可能从学习动力学本身涌现（如策略熵衰减、吸收到亚稳态、或约束预算耗尽）。
建立这种内生机制留待未来工作。

未来扩展包括吸收链、马尔可夫决策过程、强化学习和连续时间极限。

---

## 7. 结论

通过将 FIT 嵌入有限马尔可夫沙盒，我们将定性直觉转化为可验证的数学。

这代表 FIT 框架的第一次不可逆硬化步骤。

---

## 参考文献

[1] D. A. Levin, Y. Peres, and E. L. Wilmer. *Markov Chains and Mixing Times*.
    American Mathematical Society, 2009.

[2] T. M. Cover and J. A. Thomas. *Elements of Information Theory*, 2nd ed.
    Wiley-Interscience, 2006.

[3] A. W. Marshall, I. Olkin, and B. C. Arnold. *Inequalities: Theory of
    Majorization and Its Applications*, 2nd ed. Springer, 2011.

[4] D. Aldous and J. A. Fill. *Reversible Markov Chains and Random Walks on Graphs*.
    Unpublished manuscript, 2002.
