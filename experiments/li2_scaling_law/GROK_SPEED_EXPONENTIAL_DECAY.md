# Li² / Grokking：临界点之上 time-to-grok 的“加速效应”（阶段性结论）

日期：2026-01-07  
数据来源：`results/band_sweep/`（36 个实验；3 seeds；M ∈ {23, 41, 59}；每个 M 仅 4 个 ratio 点）

## 结论（目前最稳妥的表述）

`band_sweep` 清晰显示：**在各自的临界比率 `r_crit` 之上，time-to-grok 对 ratio 极其敏感，并呈现快速下降**。  
例如，对 M=41/59，ratio 从 `r_crit+0.01` 增加到 `r_crit+0.03`（+0.02），`t_grok` 约下降到原来的 ~1/2。

## 重要限制：当前不足以“证明指数律”

`band_sweep` 里每个 M 在 `r_crit` 之上只有 **2 个**可用于拟合的 grok 点（且都是 3/3 grok）。  
这意味着：

- 无论你拟合 `T = A·exp(-β·Δr)` 还是 `T = K·(Δr)^(-γ)`，**都可以得到“完美拟合”**（因为两点必然可拟合出任意两参数模型）。
- 因此，**当前数据只能支持“快速下降/强敏感”这一事实**，不能支持“函数形式 = 指数/幂律”的判别，也不能支持“β 阶跃”的断言。

更详细的解释见：`ANALYSIS_LIMITATIONS.md`。

## 记录：两点推导的“局部敏感度”（仅作参考）

我们仍可把两点之间的斜率当作“局部敏感度”做记录（不是通用律）：

令 `Δr = r - r_crit`，若用指数形式写作局部近似：

`β_local := ln(T1/T2) / (Δr2-Δr1)`

基于 `results/band_sweep` 的中位数（median）time-to-grok：

- M=23：`r_crit≈0.57`，(0.58 → 17500), (0.60 → 13300) ⇒ `β_local≈13.7`
- M=41：`r_crit≈0.49`，(0.50 → 12900), (0.52 → 6900) ⇒ `β_local≈31.3`
- M=59：`r_crit≈0.45`，(0.46 → 6900), (0.48 → 3500) ⇒ `β_local≈33.9`

这些数值反映“在当前采样点附近，ratio 增加会显著缩短 grok 时间”，但不应被当作已验证的普适指数。

## 可复现分析

从 `experiments/li2_scaling_law/` 目录运行：

```bash
# 以 grok_epoch 为 time-to-grok（默认）
python analyze_grok_speed.py --results_dir results/band_sweep --min_prob 1.0 --min_points 3

# 以 grok_delay = grok_epoch - mem_epoch（train_acc≥0.99）为 time-to-grok
python analyze_grok_speed.py --results_dir results/band_sweep --min_prob 1.0 --min_points 3 --use_delay
```

输出：
- `results/band_sweep/analysis/grok_speed_fit.json`
- `results/band_sweep/analysis/grok_speed_fit.png`
- `results/band_sweep/analysis/grok_speed_fit_delay.json`
- `results/band_sweep/analysis/grok_speed_fit_delay.png`

## 下一步：把它变成“可发表的第二条律”

要区分“指数 vs 幂律 vs 分段”，每个 M 需要至少 **5–8 个** `r_crit` 之上的点（例如 `r_crit+0.01` 到 `+0.10`，步长 0.01），并最好保留多 seed。

如果目标是研究 “β 是否随 M 有结构变化（阶跃/分段）”，则需要在 M≈25–35 附近加密 M 采样（见 `dense_m_sweep.py` / `analyze_beta_transition.py` 的路线）。
