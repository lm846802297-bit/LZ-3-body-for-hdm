# 氙同位素精确核质量计算状态

## 采用方案

同位素反冲运动学统一使用 AME2020 的 Xe 同位素中性原子质量，并按

`M_nucleus = (M_atom - 54 m_e) u + B_e(54)`

转换为裸核质量。`u` 和电子质量比采用 CODATA 2022；`B_e` 采用 AME2020 电子总结合能近似。Xe-131 的输入值为 `121.90992244721734 GeV`。天然氙核素数密度则使用丰度加权平均原子摩尔质量 `131.29276127759823 g/mol`，二者分开处理。

## 已按同一质量方案重算

| 计算 | 当前输出 | 结论 |
| --- | --- | --- |
| 主 Mathematica 笔记本的质量函数和核素映射 | `research/three_body_natural_xenon/矢量耦合暗物质三体散射与天然氙反冲率.nb` | 已改为同位素精确裸核质量；旧缓存结果已清除，63 个输入单元保留 |
| Mathematica `NIntegrate`、Gauss 阶数对照及点状靶独立 Python 积分 | `research/three_body_natural_xenon/独立验证/methods_comparison.csv`、`mma_i6_convergence.csv`、`point_target_convergence.csv` | 六个开放点的 Python 与 Mathematica `NIntegrate` 相对差小于 `1.6e-7`；阈值外检查点返回零 |
| 天然氙速度平均阶数对照 | `research/three_body_natural_xenon/convergence_halo.csv` | {6,6,4}/v6 至 {16,16,8}/v16 在 110、200、267、542 keV 的对照已更新 |
| AFH-7、Hybrid-9、AFH-7+A² ceiling、Helm-9 的 84 点连续谱 | `research/afh_default_density_natural_xenon_halo/results/afh7_hybrid9_ame2020_exact_2026-11-17/` | 元数据 `PASS`；32 个速度节点、{8,8,4} 三体求积；速度与积分阶数交叉检查均通过 |
| 相空间映射、角度、阈值、Eq. (6) 前因子、800 km/s 与近极点检查 | `research/three_body_calculation_and_validation/results/phase_space_convergence_ame2020_exact_2026-11-17/` | 所有选定 Xe-131 运动学点已用 AME2020 裸核质量重新计算 |
| 参数缩放与速度阈值 | `mathematica_halo_notebook/独立验证/model_limits.wls` | `couplingSq` ×4 时截面 ×4；400 km/s 检查点闭合 |

同一 AFH-7 精确谱在 `ER=200 keV`、`coupling_product_squared=1e-8` 下得到：红色 benchmark `1.5320145e-9`、绿色 `1.8132011e-11`、黑色 `0`、蓝色 `1.4811075e-13 events/(kg day keV)`。对应 benchmark 定义和所有能点在该谱目录的 CSV 与 `metadata.json` 中。

## 尚未能重算的链条

FeynRules→FeynArts→FeynCalc 的 Xe-131 pole-width 计算已于 2026-11-18 实际运行：脚本从工作区根目录 `天然氙三体散射/FeynRules_check/FeynArtsPatched` 加载 FeynArts，生成 2 张树图，FeynCalc 打印振幅并完成自旋迹与 NIntegrate。点状靶静态流迹的固定点相对差为 1.70×10⁻¹⁰；乘 Xe-131 AFH 响应后的截面与 Mathematica `{24,24,12}` Gauss 结果相差 −9.82×10⁻⁶。输出日志在 `results/feyncalc_feynarts_ame2020_xe131_2026-11-18/`。本次复用已存在的 FeynRules 导出模型并通过源文件哈希检查，没有重新导出 FeynRules 模型。

## 已清理的过期结果

由新精确质量结果替代的 2026-11-14 AFH-7/Hybrid-9 连续谱与高阶结果目录已删除；独立积分脚本生成的重复 CSV 也已移除，只保留主 notebook 读取的精确质量结果表。其他与本次核质量无关的模型源文件和核响应数据没有改动。
