# FIT Framework v2.3 实验程序使用说明

## 概述

这两个Python程序完全自动化地运行FIT Framework v2.3中定义的验证实验：

1. **conway_fit_experiment.py** - Conway's Game of Life验证
2. **langton_fit_experiment.py** - Langton's Ant验证

## 特点

✓ **完全自动运行** - 无需任何人工干预
✓ **生成详细报告** - 自动输出report.txt文件
✓ **可配置参数** - 可调整实验规模和阈值
✓ **统计验证** - 多次运行确保结果可靠性
✓ **进度显示** - 实时显示实验进度

## 系统要求

- Python 3.7+
- NumPy

安装依赖：
```bash
pip install numpy
```

## 使用方法

### 1. Conway's Game of Life实验

```bash
python conway_fit_experiment.py
```

**测试的命题：**
- P1: 涅槃不可逆性
- P2: 晚期约束非递减
- P4: 平台检测准则
- P7: 熵容量上界
- P10: 约束估计器等价性

**预计运行时间：** 5-10分钟

**输出文件：**
- `conway_report.txt` - 详细实验报告
- `conway_data/` - 数值数据目录

### 2. Langton's Ant实验

```bash
python langton_fit_experiment.py
```

**测试的命题：**
- P1: 吸引子持久性（高速公路类比）
- P3: 力方差衰减族
- P11: 相变信号
- P18: 时间尺度分离

**预计运行时间：** 10-20分钟（因需要等待高速公路出现）

**输出文件：**
- `langton_report.txt` - 详细实验报告
- `langton_data/` - 数值数据目录

## 配置选项

两个程序都在开头定义了`ExperimentConfig`类，可以调整参数：

### Conway配置示例
```python
@dataclass
class ExperimentConfig:
    grid_size: int = 50           # 网格大小
    num_runs: int = 20            # 独立运行次数
    max_steps: int = 2000         # 每次运行的最大步数
    window_W: int = 50            # 测量窗口
    epsilon_force: float = 0.01   # 力方差阈值
```

### Langton配置示例
```python
@dataclass
class ExperimentConfig:
    grid_size: int = 200          # 网格大小（需要较大以观察高速公路）
    num_runs: int = 10            # 独立运行次数
    max_steps: int = 15000        # 每次运行的最大步数
    highway_start: int = 8000     # 预期高速公路出现窗口
```

## 实验报告格式

报告包含以下部分：

1. **配置信息** - 实验参数
2. **执行摘要** - 总体通过率和统计
3. **各命题详情** - 每个命题的测试结果
4. **解释** - 对结果的FIT框架解读
5. **建议** - 后续实验方向

## 快速验证模式

如需快速测试（约1-2分钟），可以修改配置：

```python
# Conway快速模式
num_runs: int = 5
max_steps: int = 500

# Langton快速模式
num_runs: int = 3
max_steps: int = 10000
```

## 估计器说明

### Force (F) 估计器
- **Conway**: 基于邻居数偏离稳定值
- **Langton**: 基于步长方向对齐度

### Constraint (C) 估计器
- **冻结比例**: 窗口内不变单元的占比
- **压缩率**: 基于运行长度编码
- **内在维度**: 基于协方差矩阵

### Information (I) 估计器
- **Shannon熵**: 基于block模式
- **预测信息**: 基于轨迹序列
- **复杂度代理**: 基于网格状态标准差

## 解读结果

### 命题通过标准

- **P1**: 涅槃态下< 10%的逃逸率
- **P2**: 晚期违反率< 5%
- **P3**: > 50%运行显示指数衰减
- **P4**: 检测到平台区域
- **P7**: 违反率< 1%
- **P10**: 估计器相关性> 0.5
- **P11**: > 50%检测到预期范围内的相变
- **P18**: > 50%显示时间尺度分离（比值> 2）

### 成功率解读

- **≥ 80%**: FIT框架获得强支持
- **50-80%**: 中等支持，部分命题需要改进
- **< 50%**: 面临重大挑战，需要修订

## 常见问题

**Q: 程序可以中断吗？**
A: 可以用Ctrl+C中断。已完成的运行数据会保留。

**Q: 如何只运行特定命题？**
A: 在`run_all_tests()`方法中注释掉不需要的测试。

**Q: 内存不足怎么办？**
A: 减少`grid_size`或`num_runs`参数。

**Q: 结果不稳定？**
A: 增加`num_runs`以获得更好的统计稳定性。

## 文献对照

这些实验对应FIT Framework v2.3文档的：

- **Section 5**: 可证伪命题总览
- **Section 7**: 验证路线
- **Appendix A**: 命题注册表

## 扩展实验

基于这两个程序，可以进一步：

1. **参数扫描**: 系统地变化`grid_size`、`window_W`等
2. **对比分析**: 比较不同estimator的性能
3. **可视化**: 添加轨迹、熵曲线的图形输出
4. **新命题**: 添加P5、P6等其他命题的测试

## 技术细节

### 随机数种子
Conway程序使用运行索引作为种子，确保可重复性。

### 边界条件
两个系统都使用周期性边界（toroidal网格）。

### 数值稳定性
所有对数和除法运算都包含小常数防止数值错误。

## 联系与反馈

如发现bug或有改进建议，请参考FIT Framework v2.3文档中的联系方式。

---

**版本**: 1.0
**日期**: 2025-12-25
**兼容**: FIT Framework v2.3
