# FeynRules → FeynArts → FeynCalc + AFH：单核三体截面

## 计算对象和接口

主 notebook “五 C”使用 FeynRules 的 `ThreeBodyVV.fr` 导出的 FeynArts 模型，在独立 Mathematica 内核中生成 chi1+N -> chi1+N+s 的两个树图，使用 FCFAConvert 转入 FeynCalc。核子线投影为前导静态时间分量 2 mA delta_mu0，暗费米子做初态 1/2 自旋平均与末态求和；FeynCalc 进行 Dirac 迹及传播子处理。最后按现有模型核流匹配，乘 AFH 的物理归一化响应 `R_A=A² W00(y)/W00(0)` 并积分三体相空间。

脚本 `feynrules_feyncalc_xe131.wls` 实际支持 128、129、130、131、132、134、136 七种 AFH 氙同位素。输入 A 和 mA 必须一致；mA 使用 AME2020 原子质量减去 54 个 CODATA-2022 电子质量并加回 AME 总电子结合能修正后的裸核质量。它与 notebook 第一、二节和 1.4 节的设置对接；`pole` 处方只给辐射后的 p'+k 传播子添加 i m2 Gamma，`zero` 则两张图都无宽度。脚本核验插入宽度的结构，并拒绝 chi2 可上壳的运动学区间。

该计算不是将 AFH 弹性 DiffCrossSection 直接当作三体截面。两种计算仍使用相同 AFH 响应约定、核流前导时间分量及相同理论相空间测度；FeynCalc 导出的符号迹不同于手写数值迹，但积分调用共用独立 NIntegrate 运动学映射。两者一致不单独证明 AFH 到模型的完整匹配或整体相空间归一化。

## 基准与结果

Xe-131；mchi1=1000 GeV、mV=10 GeV、ms=300 keV、deltaM=1 MeV、g1=g2=gVN=1、ER=200 keV、v=776 km/s；辐射后极点宽度 Gamma=0.000151823911579 GeV；氙响应 RA=9.56767024757783。FeynCalc 自旋迹数值积分使用工作精度 35、目标精度 5。

旧的基准截面与误差表使用了旧靶质量，现已移除。脚本按 AME2020/CODATA-2022 精确 Xe-131 裸核质量输入，但在本机缺少 FeynArtsPatched 时无法生成 FeynCalc 振幅，因此当前没有新的 FeynCalc 数值可报告。独立 NIntegrate 与核响应结果保存在主笔记本对应的精确质量 CSV 中。

这是单一入射速度和单一氙同位素的三体微分截面；它不包括天然氙同位素加权、银河晕平均、探测器效率、能量分辨率或曝光。

## 运行

先从主 notebook 顶部运行第一至第三节，再运行“五 C”。输入来自第一、二节及 1.4 节，参数修改后必须重新运行。

直接命令行默认基准：

```
wolframscript -file feynrules_feyncalc_xe131.wls
```

带参数顺序为：`mchi ms deltaM mA ER v mV g1 g2 gVN A widthMode`；除 v 为 km/s、A 为质量数外，质量与 ER 均为 GeV，宽度模式为 `pole` 或 `zero`。零耦合、关闭的相空间和可上壳极点按脚本提示停止计算，而不是输出可能误解的数值。

修改 `ThreeBodyVV.fr` 后，依次运行 `export_feynarts.wls` 和 `patch_exported_feynarts.wls`。源模型和已导出模型的 SHA-256 会检查一致；然后再运行三体截面脚本。需要本机 FeynCalc 和 wolframscript；FeynRules、FeynArts 项目副本随文件包提供。
