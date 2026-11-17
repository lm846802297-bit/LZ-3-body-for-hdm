# FeynRules 模型经 FeynArts 与 FeynCalc 的完整点状靶计算

## 计算链和物理范围

`ThreeBodyVV.fr` 首先由 FeynRules 的 `export_feynarts.wls` 导出类模型与通用模型。`patch_exported_feynarts.wls` 把导出模型复制到项目私有的 patched FeynArts 并更新来源哈希。`feynrules_feyncalc_2to3.wls` 验证源模型哈希，在独立 Mathematica 内核加载 FeynCalc + patched FeynArts，生成 `chi1 + N -> chi1 + N + s` 的两张树图，通过 `FCFAConvert` 转换振幅，以 `FermionSpinSum/4` 做初态双自旋平均并完成四维 Dirac 迹，对三体相空间执行 NIntegrate。

这是从 FeynRules 同一个 `.fr` 模型导出的 FeynArts 文件计算；没有将 UFO 数值矩阵元交给 MadGraph，也没有假称 FeynCalc 直接导入 UFO。本次靶 N 是质量按 Xe-131 估计的点状 Dirac 费米子，采用完整矢量流；不包含真实 Xe-131 核自旋与 AFH 响应。为使两图统一，chi2 两条传播子的宽度均为零；若相空间可达 chi2 极点，脚本停止。理论相空间测度和相空间映射与其他 NIntegrate 验证共用，不能用本对照独立证实全部归一化。

## 当前重算状态

Xe-131 点状靶输入已更新为 AME2020/CODATA-2022 裸核质量 `121.90992244721734 GeV`。本机 Mathematica 当前找不到 FeynArtsPatched，FeynCalc 因此不能将 FeynRules 导出的模型转换成振幅；旧质量方案的图数、振幅和截面结果已移除，不作为当前数值。待 FeynArts 可用后，运行下述脚本即可重新生成图、振幅、自旋迹与 NIntegrate 截面。点状靶不含 AFH 核响应。

## 在 notebook 运行与重新生成模型

先从主 notebook 第一节运行到第三节，再执行“五 B”节。脚本接收 notebook 当前 mchi、ms、deltaM、靶质量、ER、速度、mV、g1、g2、gVN（此处作为点状 gN）。数值必须非零，运动学必须打开并远离零宽度极点。

如修改 `.fr`，在本目录依次执行：

```
wolframscript -file export_feynarts.wls
wolframscript -file patch_exported_feynarts.wls
```

两步都完成后才运行 `feynrules_feyncalc_2to3.wls` 或 notebook 五 B。导出和 patch 阶段均校验源文件 SHA-256。FeynCalc 是本机依赖，项目携带独立副本的 FeynArts；不覆盖系统 FeynArts。
