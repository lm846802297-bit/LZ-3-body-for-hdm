# Mathematica notebook：三体截面与天然氙 halo 反冲率

打开 `Figure2_三体微分截面与天然氙事件率.nb`。可运行文件及依赖应放在同一目录：

- `figure2_engine.wl`：三体振幅、自旋迹、相空间积分、固定速度微分截面和 halo 率；
- `dmformfactor-V6.m`：AFH v6.0 默认核响应包副本，运行前会核对官方源文件 SHA-256；
- `Figure2_完整反冲率_原始下载版.nb`：从 GitHub 取回的原始备份，不作为当前编辑入口。

笔记本内嵌了七种 AFH 可用氙同位素的精确核质量。质量约定与仓库主计算一致：
`m_A=(m_{atomic,A}-54m_e)u`，忽略电子结合能；数据源为
`research/afh_default_density_natural_xenon_halo/input/natural_xenon_isotope_weights.csv`
（SHA-256：`fd1bb996e5f582c74c3c86d129f1d2dded510c65237d0a7b2ba08861f1d8c991`）。
靶材平均摩尔质量使用全部九种天然氙同位素，`131.29276144779053 g/mol`；
AFH 响应只覆盖七种同位素，七种丰度之和为 `0.998158`，不重新归一化。

从 notebook 顶部开始逐节运行，或使用 Mathematica 的“评估整个笔记本”。第九节会在 notebook 所在目录创建 `g2_output/`，输出 CSV 和 `rate_compare.png`、`ratio_compare.png`；这些是运行时生成文件，不是本 PR 已提交的归档结果。

笔记本依次计算固定同位素/固定速度的三体微分截面、实验室截断 Maxwell 速度积分，以及按天然氙丰度加权的七同位素理论反冲率。示例耦合为 `g1=g2=gVN=1`。结果不含探测器效率、能量分辨率、选择函数或 LZ likelihood。

**数值状态：** 质量输入已改为精确同位素核质量，但当前 notebook 中保留的嵌入式输出来自此前的 `A u` 质量近似。必须在 Wolfram Mathematica 14.2 中从头重跑并重新归档输出/元数据后，才能将数值结果标记为 exact-mass 版本。