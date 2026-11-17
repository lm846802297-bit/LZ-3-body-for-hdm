# FeynRules 模型经 FeynArts 与 FeynCalc 的完整点状靶计算

## 计算链和物理范围

`ThreeBodyVV.fr` 首先由 FeynRules 的 `export_feynarts.wls` 导出类模型与通用模型。`patch_exported_feynarts.wls` 把导出模型复制到项目私有的 patched FeynArts 并更新来源哈希。`feynrules_feyncalc_2to3.wls` 验证源模型哈希，在独立 Mathematica 内核加载 FeynCalc + patched FeynArts，生成 `chi1 + N -> chi1 + N + s` 的两张树图，通过 `FCFAConvert` 转换振幅。Xe-131 的 pole-width 脚本以 `FermionSpinSum/2` 对暗物质初态自旋平均并完成四维 Dirac 迹，再对静态核流投影后的三体相空间执行 NIntegrate；零宽度点状靶脚本会在极点可达时按设计中止，不作为当前数值截面。

这是从 FeynRules 同一个 `.fr` 模型导出的 FeynArts 文件计算；没有将 UFO 数值矩阵元交给 MadGraph，也没有假称 FeynCalc 直接导入 UFO。本次靶 N 是质量按 Xe-131 估计的点状 Dirac 费米子，采用完整矢量流；不包含真实 Xe-131 核自旋与 AFH 响应。为使两图统一，chi2 两条传播子的宽度均为零；若相空间可达 chi2 极点，脚本停止。理论相空间测度和相空间映射与其他 NIntegrate 验证共用，不能用本对照独立证实全部归一化。

## 当前重算状态

Xe-131 点状靶质量使用 AME2020/CODATA-2022 裸核质量 `121.90992244721734 GeV`。FeynCalc 安装在 Mathematica 应用目录；FeynArts 3.12 及 patched 副本位于工作区根目录下的 `天然氙三体散射/feynarts/FeynArts-3.12/` 与 `天然氙三体散射/FeynRules_check/FeynArtsPatched/`。脚本现在按 `FEYNARTS_DIR`、脚本同目录、工作区本地 patched 安装的顺序查找 FeynArts。

2026-11-18 实际运行 Xe-131 pole-width 脚本：FeynArts 从现有、经源文件 SHA-256 校验的 FeynRules 导出模型生成两张树图；FeynCalc 打印振幅，插入极点宽度并完成自旋迹及三体 NIntegrate。点状静态核流振幅与笔记本独立迹的固定点相对差为 `1.70×10⁻¹⁰`；FeynCalc 截面为 `1.9021840213 GeV⁻³`，与 `{24,24,12}` Mathematica Gauss 截面相对差 `−9.82×10⁻⁶`。完整输出见 `../../results/feyncalc_feynarts_ame2020_xe131_2026-11-18/feynrules_feynarts_feyncalc_xe131.log`。本次复用了已有 FeynRules 导出并验证其源哈希，没有重新执行 FeynRules 导出。该运行是点状 Dirac 靶计算，不含 AFH 核响应；AFH 核响应计算另见“五 C”。

## 在 notebook 运行与重新生成模型

先从主 notebook 第一节运行到第三节，再执行“五 B”节。脚本接收 notebook 当前 mchi、ms、deltaM、靶质量、ER、速度、mV、g1、g2、gVN（此处作为点状 gN）。数值必须非零，运动学必须打开并远离零宽度极点。

如修改 `.fr`，在本目录依次执行：

```
wolframscript -file export_feynarts.wls
wolframscript -file patch_exported_feynarts.wls
```

两步都完成后才运行 `feynrules_feyncalc_2to3.wls` 或 notebook 五 B。导出和 patch 阶段均校验源文件 SHA-256。FeynCalc 是本机依赖，项目携带独立副本的 FeynArts；不覆盖系统 FeynArts。
