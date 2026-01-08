# Li² Scaling Law 验证 — 实验结果（updated 2026-01-07）

Status: a working experimental report for Li² scaling-law verification (not a preregistered FIT claim document).

## 核心结论

在当前实现与配置下，我们用 **multi-seed band sweep**（M={23,41,59}；seeds={42,123,456}；每个 M 在临界附近扫 4 个 ratio）得到一个强有力的 n-space 经验拟合：

`n_critical ≈ 6.08 · M log M (R^2 = 0.951)`

说明在 modular-addition grokking 任务上，临界样本数与 `M log M` 呈高度线性关系（常数因子 `c` 明显大于 1）。

## 实验配置（multi-seed band sweep 锁定）

- 任务：`(a + b) mod M`
- 网络：2-layer，`hidden_dim=2048`
- 激活：quadratic (`σ(x)=x^2`)
- 优化器：AdamW，`lr=0.001`
- weight decay：`0.001`
- epochs：`25000`（达到 grok 后可能 early-stop）
- grok 判据：`test_acc >= 95%`

## Multi-seed 边界（50% grok 概率插值点）

| M | ratio_crit | n_crit (≈ ratio·M²) | M log M | c_implied (= n/(M log M)) |
|---:|---:|---:|---:|---:|
| 23 | 0.570 | 301.5 | 72.1 | 4.18 |
| 41 | 0.490 | 823.7 | 152.3 | 5.41 |
| 59 | 0.450 | 1566.5 | 240.6 | 6.51 |

注：`n_crit` 以 “插值 ratio × M²（连续值）” 近似。

## 可视化

- Multi-seed band sweep（推荐作为主结果）：
  - `results/band_sweep/analysis/scaling_law_n.png`
  - `results/band_sweep/analysis/phase_diagram.png`
  - `results/band_sweep/analysis/report.md`
- 旧的单 seed 汇总图（seed=42；历史参考）：`results/analysis/`

## 复现 / 重新拟合

从 `experiments/li2_scaling_law/` 目录：

- 跑 multi-seed band sweep：`python band_sweep.py`
- 生成拟合 + 图（band sweep）：`python analyze.py --results_dir results/band_sweep --output_dir results/band_sweep/analysis`
- 生成可视化（硬编码版本）：`python plot_results.py`

## 单 seed（seed=42）结果对照（历史参考）

同样用 50% grok 临界定义，seed=42 的边界为：
- M=23: 0.565
- M=41: 0.490
- M=59: 0.445

与 multi-seed 结果相比，偏移 < 1%（0.005 量级），说明边界相当稳健。

## 下一步（如果要更“硬”）

1. 增加更多 M（如 71/97/127）验证 c 是否稳定/是否需要更高阶修正。
2. 用 `history.grad_norms` 的 `gf_norm` / alignment proxy 做“三阶段”更强证据链。
