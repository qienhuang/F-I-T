# FIT 马尔可夫沙盒（最小发布版 v0.1）

这是马尔可夫链"可证明特化"的**最小、可发布包**。

## 单行声明（论文级措辞）

这是一个可证明的特化：沿惰性硬化路径 $P_{\alpha}=(1-\alpha)P+\alpha I$，熵率 $h(\alpha)$ 趋向 $0$，预测互信息 $C(\alpha)=I(X_t;X_{t+1})$ 趋向 $H(\pi)$；在简单的**自主导**条件下，$h(\alpha)$ 对 $\alpha$ 非递增，$C(\alpha)$ 对 $\alpha$ 非递减。

## 关键图表（一瞥即知）

![FIT 马尔可夫验证](fit_markov_validation.png)

## 最小发布构件

- 论文（简版）：`fit_markov_sandbox_short.md`
- 定义 + 范围：`definitions.md`
- 复现代码（核心）：`experiments.py`
- 关键图表：`fit_markov_validation.png`

## 快速复现（1 条命令）

从本文件夹：

```bash
python plot_validation.py
```

输出：
- `fit_markov_validation.png`
- `fit_markov_validation_small.png`

## 注释（范围纪律）

- **不要**声称对所有链的无条件单调性；单调性仅在明确的充分条件下陈述。
- 在此沙盒中将"涅槃"视为**极限状态描述符**，而非普遍终端声明。
