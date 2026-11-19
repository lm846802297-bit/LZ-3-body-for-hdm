# 矢量耦合暗物质三体散射与天然氙反冲率

本目录包含整理后的 Mathematica 主笔记本和计算所需的 AFH v6 氙核响应输入。主计算代码直接保存在 notebook 中，按顺序从物理参数、FeynCalc 振幅与自旋迹、三体相空间 `NIntegrate`，推进到同位素/速度平均、总截面和天然氙事件率。

## 文件

- `矢量耦合暗物质三体散射与天然氙反冲率.nb`：主计算及末尾分组的验证。
- `dmformfactor-V6.m`：AFH v6 默认氙同位素核响应。
- `使用说明.md`：输入、计算顺序、结果和近似说明。
- `完整运行与数值对照.md`：此前完整运行的历史结果；不是本次结构整理后的全量重跑记录。
- `convergence_halo.csv`、`独立验证/methods_comparison.csv`：笔记本验证章节读取的归档对照数据。

## 运行要求

主计算需要 Mathematica；AFH 核响应数据与 notebook 同目录。FeynCalc、FeynRules 2.3.49 与 FeynArts 3.12 的源码副本放在 `../three_body_calculation_and_validation/mathematica_halo_notebook/FeynRules_check/`，版本、许可和 SHA-256 清单见该目录说明。主 notebook 和验证脚本优先加载仓库内的 FeynCalc 副本。笔记本末尾 FeynRules/FeynArts 验证需要按该目录说明运行。

从 notebook 最上方按顺序运行。更改物理输入或积分精度后，要重新运行后续依赖单元；嵌入的旧输出不会自动更新。天然氙事件率没有包含探测器效率、能量分辨率或曝光选择。
