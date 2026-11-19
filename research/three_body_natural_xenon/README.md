# 矢量耦合暗物质三体散射与天然氙反冲率

本目录包含整理后的 Mathematica 主笔记本和计算所需的 AFH v6 氙核响应输入。主计算代码直接保存在 notebook 中，按顺序从物理参数、FeynCalc 振幅与自旋迹、三体相空间 `NIntegrate`，推进到同位素/速度平均、总截面和天然氙事件率。

## 文件

- `矢量耦合暗物质三体散射与天然氙反冲率.nb`：主计算及末尾分组的验证。
- `dmformfactor-V6.m`：AFH v6 默认氙同位素核响应。
- `使用说明.md`：输入、计算顺序、结果和近似说明。
- `完整运行与数值对照.md`：此前完整运行的历史结果；不是本次结构整理后的全量重跑记录。
- `convergence_halo.csv`、`独立验证/methods_comparison.csv`：笔记本验证章节读取的归档对照数据。

## 物理基准说明

主 notebook 的 AFH 氙核路径保留有限尺寸 W_M(y_A)，但使用常数有效核子耦合，未显式加入 F_1^{V,N}(t_N)、F_2^{V,N}(t_N)；因此它是 A 类历史参考，不是当前采用的 B 基准。W_M(y_A) 不是点核响应。详细的核子形状因子、AFH 核响应和历史结果分级见 [全仓库物理与命名审计](../three_body_full_current_nucleon_match/REPOSITORY_WIDE_PHYSICS_AND_NAMING_AUDIT_2026-11-19.md)。

## 运行要求

主计算需要 Mathematica 和本机安装的 FeynCalc；AFH 核响应数据与 notebook 同目录。笔记本末尾的 FeynRules/FeynArts 验证还需要相应软件包及模型导出环境。本仓库不打包第三方 Mathematica 软件；这些验证的已保存输出保留在 notebook 中，重新运行时需先配置本地软件。

从 notebook 最上方按顺序运行。更改物理输入或积分精度后，要重新运行后续依赖单元；嵌入的旧输出不会自动更新。天然氙事件率没有包含探测器效率、能量分辨率或曝光选择。
