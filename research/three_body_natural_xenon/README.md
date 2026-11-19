# 矢量耦合暗物质三体散射与天然氙反冲率

本目录包含整理后的 Mathematica 主笔记本和计算所需的 AFH v6 氙核响应输入。主计算代码直接保存在 notebook 中，按顺序从物理参数、FeynCalc 振幅与自旋迹、三体相空间 `NIntegrate`，推进到同位素/速度平均、总截面和天然氙事件率。

## 2026-11-19 基准状态

Mathematica notebook 保留为原始 AFH 有限尺寸 A 参考；本次正式采用的 B 基准是在相同 AFH (W_M(y_A)) 上加入低动量核子 Dirac–Pauli 形状因子 (widehat F_1(t_N),widehat F_2(t_N))，不加入其他 AFH 响应。原 notebook 的历史主 rate 路径不能直接视为已经完成 B。B 的统一公式、(g_{VN}) factor-three 归一化、AFH factor-four 账本和 Python 实现见 `research/three_body_full_current_nucleon_match/NUCLEAR_FINITE_SIZE_BASELINE_POLICY.md`。

## 文件

- `矢量耦合暗物质三体散射与天然氙反冲率.nb`：主计算及末尾分组的验证。
- `dmformfactor-V6.m`：AFH v6 默认氙同位素核响应。
- `使用说明.md`：输入、计算顺序、结果和近似说明。
- `完整运行与数值对照.md`：此前完整运行的历史结果；不是本次结构整理后的全量重跑记录。
- `convergence_halo.csv`、`独立验证/methods_comparison.csv`：笔记本验证章节读取的归档对照数据。

## 运行要求

主计算需要 Mathematica 和本机安装的 FeynCalc；AFH 核响应数据与 notebook 同目录。笔记本末尾的 FeynRules/FeynArts 验证还需要相应软件包及模型导出环境。本仓库不打包第三方 Mathematica 软件；这些验证的已保存输出保留在 notebook 中，重新运行时需先配置本地软件。

从 notebook 最上方按顺序运行。更改物理输入或积分精度后，要重新运行后续依赖单元；嵌入的旧输出不会自动更新。天然氙事件率没有包含探测器效率、能量分辨率或曝光选择。
